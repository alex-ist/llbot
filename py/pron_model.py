import math
import os
from typing import Dict, Optional, Tuple

import torch
import torch.nn as nn
from torch import Tensor
from transformers import AutoFeatureExtractor, AutoModel


CACHE_DIR = os.environ.get("HF_CACHE_DIR")


def load_backbone(model_name: str, device: str):
    if CACHE_DIR:
        os.makedirs(CACHE_DIR, exist_ok=True)
    backbone = AutoModel.from_pretrained(model_name, cache_dir=CACHE_DIR).to(device)
    feature_extractor = AutoFeatureExtractor.from_pretrained(model_name, cache_dir=CACHE_DIR)
    return backbone, feature_extractor


def freeze_backbone(backbone):
    backbone.eval()
    for param in backbone.parameters():
        param.requires_grad = False


def unfreeze_top_encoder_layers(backbone, num_layers: int):
    freeze_backbone(backbone)
    backbone.train()
    if hasattr(backbone, "encoder") and hasattr(backbone.encoder, "layer_norm"):
        for param in backbone.encoder.layer_norm.parameters():
            param.requires_grad = True
    if not hasattr(backbone, "encoder") or not hasattr(backbone.encoder, "layers"):
        raise RuntimeError("Unexpected backbone structure; encoder.layers not found.")
    for layer in backbone.encoder.layers[-num_layers:]:
        for param in layer.parameters():
            param.requires_grad = True


def get_backbone_trainable_params(backbone):
    return [param for param in backbone.parameters() if param.requires_grad]


class RelPositionalEmbedding(nn.Module):
    def __init__(self, dim: int = 144, base: int = 10000, init_len: int = 256):
        super().__init__()
        self.dim = dim
        self.base = base
        pe = self.create_pe(init_len, torch.device("cpu"))
        self.register_buffer("pe", pe, persistent=False)

    def create_pe(self, length: int, device: torch.device) -> Tensor:
        positions = torch.arange(-length + 1, length, device=device).float()
        pe = torch.zeros(positions.size(0), self.dim, device=device)

        i = torch.arange(0, self.dim, 2, device=device).float()
        step = -math.log(self.base) / self.dim
        div_term = torch.exp(i * step)
        angles = positions.unsqueeze(1) * div_term.unsqueeze(0)

        pe[:, 0::2] = torch.sin(angles)
        pe[:, 1::2] = torch.cos(angles)
        return pe.unsqueeze(0)

    def forward(self, x: Tensor) -> Tuple[Tensor, Tensor]:
        input_len = x.size(1)
        if self.pe.size(1) < 2 * input_len - 1:
            self.pe = self.create_pe(input_len, self.pe.device)

        full_len = self.pe.size(1)
        center = full_len // 2
        start = center - (input_len - 1)
        end = center + input_len
        return x, self.pe[:, start:end]


class MultiHeadAttention(nn.Module):
    def __init__(self, input_dim: int, n_head: int):
        super().__init__()
        assert input_dim % n_head == 0
        self.d_k = input_dim // n_head
        self.h = n_head
        self.linear_q = nn.Linear(input_dim, input_dim)
        self.linear_k = nn.Linear(input_dim, input_dim)
        self.linear_v = nn.Linear(input_dim, input_dim)
        self.linear_out = nn.Linear(input_dim, input_dim)

    def forward_qkv(self, query: Tensor, key: Tensor, value: Tensor):
        b = query.size(0)
        q = self.linear_q(query).view(b, -1, self.h, self.d_k)
        k = self.linear_k(key).view(b, -1, self.h, self.d_k)
        v = self.linear_v(value).view(b, -1, self.h, self.d_k)
        return q.transpose(1, 2), k.transpose(1, 2), v.transpose(1, 2)

    def forward_attention(self, value: Tensor, scores: Tensor, mask: Optional[Tensor]):
        if mask is not None:
            scores = scores.masked_fill(mask.unsqueeze(1), -10000.0)
        attn = torch.softmax(scores, dim=-1)
        x = torch.matmul(attn, value)
        b = value.size(0)
        x = x.transpose(1, 2).reshape(b, -1, self.h * self.d_k)
        return self.linear_out(x)


class RelPositionMultiHeadAttention(MultiHeadAttention):
    def __init__(self, input_dim: int, n_head: int):
        super().__init__(input_dim, n_head)
        self.linear_pos = nn.Linear(input_dim, input_dim, bias=False)
        self.pos_bias_u = nn.Parameter(torch.FloatTensor(self.h, self.d_k))
        self.pos_bias_v = nn.Parameter(torch.FloatTensor(self.h, self.d_k))
        nn.init.xavier_uniform_(self.pos_bias_u)
        nn.init.xavier_uniform_(self.pos_bias_v)

    def rel_shift(self, x: Tensor) -> Tensor:
        b, h, qlen, pos_len = x.size()
        x = x.view(b, h, pos_len, qlen)
        x = x[:, :, 1:, :]
        x = x.view(b, h, qlen, pos_len - 1)
        return x

    def forward(self, q: Tensor, k: Tensor, v: Tensor, pos_emb: Tensor, mask: Optional[Tensor] = None) -> Tensor:
        q, k, v = self.forward_qkv(q, k, v)
        p = self.linear_pos(pos_emb)
        p = p.view(pos_emb.shape[0], -1, self.h, self.d_k).transpose(1, 2)

        q_with_bias_u = q + self.pos_bias_u.unsqueeze(0).unsqueeze(2)
        q_with_bias_v = q + self.pos_bias_v.unsqueeze(0).unsqueeze(2)

        matrix_bd = torch.matmul(q_with_bias_v, p.transpose(-2, -1))
        matrix_bd = self.rel_shift(matrix_bd)
        matrix_ac = torch.matmul(q_with_bias_u, k.transpose(-2, -1))
        matrix_bd = matrix_bd[:, :, :, : matrix_ac.size(-1)]
        scores = (matrix_ac + matrix_bd) / math.sqrt(self.d_k)
        return self.forward_attention(v, scores, mask)


class MultiHeadedSelfAttentionModule(nn.Module):
    def __init__(self, input_dim: int, num_heads: int, max_len: int = 1024, dropout_p: float = 0.1):
        super().__init__()
        self.pos_enc = RelPositionalEmbedding(dim=input_dim, base=10000, init_len=max_len)
        self.layer_norm = nn.LayerNorm(input_dim)
        self.attention = RelPositionMultiHeadAttention(input_dim, num_heads)
        self.dropout = nn.Dropout(p=dropout_p)

    def forward(self, inputs: Tensor, att_mask: Optional[Tensor] = None):
        batch_size = inputs.size(0)
        inputs, pos_emb = self.pos_enc(inputs)
        if pos_emb.size(0) == 1 and batch_size > 1:
            pos_emb = pos_emb.expand(batch_size, -1, -1)
        inputs = self.layer_norm(inputs)
        outputs = self.attention(inputs, inputs, inputs, pos_emb=pos_emb, mask=att_mask)
        return self.dropout(outputs)


class ConvolutionModule(nn.Module):
    def __init__(self, in_channels: int, kernel_size: int = 31, expansion_factor: int = 2, dropout_p: float = 0.1):
        super().__init__()
        assert (kernel_size - 1) % 2 == 0
        self.ln = nn.LayerNorm(in_channels)
        self.pointwise_conv1 = nn.Conv1d(in_channels, expansion_factor * in_channels, kernel_size=1, bias=True)
        self.glu = nn.GLU(dim=1)
        self.depthwise_conv = nn.Conv1d(
            in_channels,
            in_channels,
            kernel_size=kernel_size,
            stride=1,
            padding=(kernel_size - 1) // 2,
            groups=in_channels,
        )
        self.batch_norm = nn.BatchNorm1d(in_channels)
        self.swish = nn.SiLU()
        self.pointwise_conv2 = nn.Conv1d(in_channels, in_channels, kernel_size=1, bias=True)
        self.dropout = nn.Dropout(dropout_p)

    def forward(self, x: Tensor, pad_mask: Optional[Tensor] = None) -> Tensor:
        x = self.ln(x)
        x = x.transpose(1, 2)
        x = self.pointwise_conv1(x)
        x = self.glu(x)
        if pad_mask is not None:
            x = x.masked_fill(pad_mask.unsqueeze(1), 0.0)
        x = self.depthwise_conv(x)
        x = self.batch_norm(x)
        x = self.swish(x)
        x = self.pointwise_conv2(x)
        x = self.dropout(x)
        return x.transpose(1, 2)


class FeedForwardModule(nn.Module):
    def __init__(self, encoder_dim: int = 144, expansion_factor: int = 4, dropout_p: float = 0.1):
        super().__init__()
        d_ff = encoder_dim * expansion_factor
        self.layer_norm = nn.LayerNorm(encoder_dim)
        self.linear1 = nn.Linear(encoder_dim, d_ff, bias=True)
        self.activation = nn.SiLU()
        self.dropout = nn.Dropout(dropout_p)
        self.linear2 = nn.Linear(d_ff, encoder_dim, bias=True)

    def forward(self, x: Tensor) -> Tensor:
        x = self.layer_norm(x)
        x = self.linear1(x)
        x = self.activation(x)
        x = self.dropout(x)
        x = self.linear2(x)
        x = self.dropout(x)
        return x


class ConformerBlock(nn.Module):
    def __init__(
        self,
        encoder_dim: int = 144,
        num_attention_heads: int = 4,
        feed_forward_expansion_factor: int = 4,
        conv_expansion_factor: int = 2,
        conv_kernel_size: int = 31,
        pos_emb_init_len: int = 256,
        dropout_p: float = 0.1,
    ):
        super().__init__()
        self.fc_factor = 0.5
        self.ffn1 = FeedForwardModule(encoder_dim, feed_forward_expansion_factor, dropout_p)
        self.ffn2 = FeedForwardModule(encoder_dim, feed_forward_expansion_factor, dropout_p)
        self.self_attn = MultiHeadedSelfAttentionModule(
            input_dim=encoder_dim,
            num_heads=num_attention_heads,
            max_len=pos_emb_init_len,
            dropout_p=dropout_p,
        )
        self.conv_module = ConvolutionModule(
            in_channels=encoder_dim,
            kernel_size=conv_kernel_size,
            expansion_factor=conv_expansion_factor,
            dropout_p=dropout_p,
        )
        self.ln = nn.LayerNorm(encoder_dim)
        self.dropout = nn.Dropout(dropout_p)

    def forward(self, x: Tensor, pad_mask: Optional[Tensor] = None, att_mask: Optional[Tensor] = None) -> Tensor:
        x = x + self.fc_factor * self.ffn1(x)
        residual = x
        att_out = self.self_attn(x, att_mask)
        x = residual + self.dropout(att_out)
        x = x + self.conv_module(x, pad_mask=pad_mask)
        x = x + self.fc_factor * self.ffn2(x)
        x = self.ln(x)
        return x


class ConformerCTCHead(nn.Module):
    def __init__(
        self,
        input_dim: int,
        encoder_dim: int,
        num_layers: int,
        num_attention_heads: int,
        conv_kernel_size: int,
        n_phones: int,
        dropout: float = 0.1,
        ff_expansion: int = 4,
        conv_expansion: int = 2,
        max_len: int = 1024,
        local_attn_window: Optional[int | Tuple[int, int]] = 25,
    ):
        super().__init__()
        self.blank_id = n_phones
        self.local_attn_window = local_attn_window
        self.input_proj = nn.Sequential(
            nn.Linear(input_dim, encoder_dim),
            nn.LayerNorm(encoder_dim),
            nn.Dropout(dropout),
        )
        self.layers = nn.ModuleList(
            [
                ConformerBlock(
                    encoder_dim=encoder_dim,
                    num_attention_heads=num_attention_heads,
                    feed_forward_expansion_factor=ff_expansion,
                    conv_expansion_factor=conv_expansion,
                    conv_kernel_size=conv_kernel_size,
                    pos_emb_init_len=max_len,
                    dropout_p=dropout,
                )
                for _ in range(num_layers)
            ]
        )
        self.out = nn.Linear(encoder_dim, n_phones + 1, bias=False)

    def _build_local_mask(self, t: int, device: torch.device) -> Optional[Tensor]:
        if self.local_attn_window is None:
            return None
        if isinstance(self.local_attn_window, (tuple, list)):
            backward_window = int(self.local_attn_window[0])
            forward_window = int(self.local_attn_window[1])
        else:
            backward_window = int(self.local_attn_window)
            forward_window = int(self.local_attn_window)

        q_ids = torch.arange(t, device=device).unsqueeze(1)
        k_ids = torch.arange(t, device=device).unsqueeze(0)
        backward_ok = (q_ids - k_ids) <= backward_window
        forward_ok = (k_ids - q_ids) <= forward_window
        return ~(backward_ok & forward_ok)

    def forward(self, x: Tensor, input_lengths: Optional[Tensor] = None) -> Tensor:
        x = self.input_proj(x)
        pad_mask = None
        att_mask = None
        t = x.size(1)
        local_mask = self._build_local_mask(t, x.device)
        if input_lengths is not None:
            ids = torch.arange(t, device=x.device).unsqueeze(0)
            pad_mask = ids >= input_lengths.unsqueeze(1)
            att_mask = pad_mask.unsqueeze(1) | pad_mask.unsqueeze(2)
            if local_mask is not None:
                att_mask = att_mask | local_mask.unsqueeze(0)
        elif local_mask is not None:
            att_mask = local_mask.unsqueeze(0).expand(x.size(0), -1, -1)
        for layer in self.layers:
            x = layer(x, pad_mask=pad_mask, att_mask=att_mask)
        return self.out(x)


def load_conformer_ctc_checkpoint(path: str, device: str, load_backbone_model: bool = False):
    ckpt = torch.load(path, map_location="cpu")
    phone_to_id = ckpt["phone_to_id"]
    cfg = ckpt["head_config"]
    head = ConformerCTCHead(
        input_dim=cfg["input_dim"],
        encoder_dim=cfg["encoder_dim"],
        num_layers=cfg["num_layers"],
        num_attention_heads=cfg["num_attention_heads"],
        conv_kernel_size=cfg["conv_kernel_size"],
        n_phones=cfg["n_phones"],
        dropout=cfg["dropout"],
        ff_expansion=cfg.get("ff_expansion", 4),
        conv_expansion=cfg.get("conv_expansion", 2),
        local_attn_window=cfg.get("local_attn_window", 25),
    ).to(device)
    head.load_state_dict(ckpt["head_state_dict"])
    head.eval()

    backbone = None
    feature_extractor = None
    if load_backbone_model:
        backbone, feature_extractor = load_backbone(ckpt["backbone_id"], device)
        if "backbone_state_dict" in ckpt:
            backbone.load_state_dict(ckpt["backbone_state_dict"])
        backbone.eval()
    return head, phone_to_id, ckpt, backbone, feature_extractor


__all__ = [
    "CACHE_DIR",
    "ConformerCTCHead",
    "freeze_backbone",
    "get_backbone_trainable_params",
    "load_backbone",
    "load_conformer_ctc_checkpoint",
    "unfreeze_top_encoder_layers",
]
