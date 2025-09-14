# cambridge_scrape.py
# Python 3.9+
import json
import re, os
from urllib.parse import urljoin
import httpx

import requests
from bs4 import BeautifulSoup
from bot_db import *
import random

BASE = "https://dictionary.cambridge.org"
AUDIO_PATH="data/en/w"
HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 OPR/120.0.0.0"
    }

def text(el):
    return re.sub(r"\s+", " ", el.get_text(" ", strip=True)) if el else None
def text_all(els):
    r =  ""
    for el in els:
        t = text(el)
        if r != "":
            r += ","
        r += t
    r = r.strip()
    if r == "":
        r = None
    return r


def join_url(href):
    return urljoin(BASE, href) if href else None

def collect_audio(block):
    for s in block.select("audio source[src]"):
        href = s.get("src", "").strip()
        if href.endswith(".ogg"):
            return join_url(href)
            
    return None

def parse_pronunciations(soup):
    """Собирает произношения по всем частям речи на странице."""
    out = []
    dict_block = soup.select_one(".pr.dictionary")
    if not dict_block:
        return out    
    
    entry_num = 0
    for entry in dict_block.select(".entry"):
        for entry_el in entry.select(".entry-body__el"):
            pos = text(entry_el.select_one(".pos-header .pos"))
            head = text(entry_el.select_one(".headword"))  # lemma (hw) в шапке
            # UK/US блоки произношений
            for reg_cls in (".uk.dpron-i", ".us.dpron-i"):
                reg_block = entry_el.select_one(reg_cls)
                if not reg_block:
                    continue
                region = text(reg_block.select_one(".region"))  # 'uk' / 'us'
                ipa = text(reg_block.select_one(".pron .ipa"))
                audio = collect_audio(reg_block)
                if region or ipa or any(audio.values()):
                    out.append( {
                        "hw": head,
                        "pos": pos,
                        "region": region,       # 'uk' | 'us'
                        "ipa": ipa,             # 'wɪnd'
                        "audio": audio,          # {'mp3':..., 'ogg':...}
                        "entry_num": entry_num  # чтобы отличать одинаковые POS
                    })
        entry_num += 1
    return out

def parse_senses(soup):
    """Собирает смыслы (sense) c определениями и примерами."""
    senses = []
    
    dict_block = soup.select_one(".pr.dictionary")
    if not dict_block:
        return senses    
    
    entry_num = 0
    e  = []
    for entry in dict_block.select(".entry"):
        for entry_el in entry.select(".pr.entry-body__el"):
            pos = text(entry_el.select_one(".pos-header .pos"))
            hw = text(entry_el.select_one(".pos-header .headword .hw"))
            # Каждый смысл — .pr.dsense (внутри .pos-body)
            senses = []
            for sblock in entry_el.select(".pos-body .pr.dsense"):
                guide = text(sblock.select_one(".dsense_h .dsense_gw span"))  # Guideword в скобках
                # Внутри sense обычно несколько def-block (подсмыслы/подзначения)
                sub_senses = []
                for d in sblock.select(".sense-body .def-block"):
                    if d.find_parent(class_="dphrase_b"):
                        continue  # пропускаем блоки внутри phrase-body                    
                    # коды и грам. пометы
                    level = text(d.select_one(".ddef_h .def-info .epp-xref"))  # A1, B2 ...
                    # Пример грам. помет: [ C ] / [ C or U ]
                    gram = text_all(d.select(".ddef_h .def-info .gram .gc"))
                    definition = text(d.select_one(".ddef_h .def"))
                    if definition[-1] == ":":
                        definition = definition[:-1].strip()
                    # Варианты/синонимы в этой шапке (например US also ... / (US gas))
                    variant = text(d.select_one(".ddef_h .var"))
                    # Примеры
                    examples = [text(x) for x in d.select(".def-body .examp .eg") if text(x)]
                    # Collocations/lemmas units прямо внутри примеров (lu dlu)
                    collocs = [text(x) for x in d.select(".def-body .examp .lu.dlu") if text(x)]
                    if definition:
                        item = {
                            "definition": definition,     # основной текст дефиниции
                        }
                        if level is not None: item["level"] = level
                        if gram is not None: item["grammar"] = gram
                        if variant is not None: item["variant"] = variant
                        if examples: item["examples"] = examples
                        if collocs: item["collocations"] = collocs
                        sub_senses.append(item)
                        
                if sub_senses:
                    senses.append({
                        "gw": guide,
                        "sub_senses": sub_senses
                    })
                
            if senses:
                e.append({
                    "hw": hw,
                    "pos": pos,
                    "entry_num": entry_num,
                    "senses": senses
                })
                
        entry_num += 1
    return e

from botlog import logger
from trans import web_get_en_dictionary_link
    
async def scrape_lemma(fw):    
    link, status = await web_get_en_dictionary_link("111", fw) #None - нет такого слова
    if status != "ok":
        return None, None, None, status
   
    try:
        async with httpx.AsyncClient(headers=HEADERS, timeout=20, follow_redirects=True) as client:
            resp = await client.get(link)
            
            if resp.status_code == 404 or resp.status_code == 410:
                return None, None, link, "not_found" #страницы точно нет.
            elif resp.status_code == 403:
                logger.info(f" !!!!!!!!!!!!!! CAMBRIGE DICT 403 FORBIDDEN fw = {fw}: resp.code={resp.status_code}")
                return None, None, link, "banned"
            elif resp.status_code == 200:
                soup = BeautifulSoup(resp.text, "html.parser")
                pronunciations = parse_pronunciations(soup)
                entries = parse_senses(soup)
                return pronunciations, entries, link, "ok"
            else:
                print(f"Unknown status code: {resp.status_code}")
                logger.warning(f"Unknown status code: {resp.status_code}")
                return None, None, link, "error" #неизвестно (таймаут, сбой, непредвиденный код).

    except httpx.TimeoutException:
        logger.error(f"httpx: read cambrige dict fw={fw}: Exception: Timeout")
        return None, None, link, "error"
    except Exception as e:
        logger.error(f"httpx: read cambrige dict fw={fw}: Exception ({type(e).__name__}): {e}")
        return None, None, link, "error"


def get_num_for_link(region_map: dict[str, int], audio_link: str) -> tuple[int, bool]:
    """
    Возвращает (num, is_new_link). Если новая ссылка — num = max+1.
    """
    if audio_link in region_map:
        return region_map[audio_link], False
    n = (max(region_map.values()) + 1) if region_map else 1
    region_map[audio_link] = n
    return n, True

async def download_file(audio_link, full_path):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        async with httpx.AsyncClient(headers=headers, timeout=5) as client:
            response = await client.get(audio_link, follow_redirects=True)
            if response.status_code != 200:
                logger.error(f"!!!!!!!cambrige dict download error: {audio_link}: resp.code={response.status_code}")
                return False
            data = response.content
            if not data:
                logger.error(f"empty body for {audio_link}")
                return False
            with open(full_path, 'wb') as f:
                f.write(data)
            return True
    except Exception as e:
        logger.error(f"!!!!!!!cambrige dict download error: GET {audio_link}: Exception ({type(e).__name__}): {e}")
    return False

def save_json(fw, raw_json):
    if not raw_json or not fw:
        return
    
    fw = re.sub(r"[\\/]", "_", fw)
    
    subdir = os.path.join("data", "en", "c_json", fw[0].lower())
    if not os.path.exists(subdir):
        os.makedirs(subdir)
    full_path = os.path.join(subdir, f"{fw}.json")
    with open(full_path, 'w', encoding='utf-8') as f:
        f.write(raw_json)

async def run_scrap():
    logger.info(f"cambrige dict get link")
    db, c=open_db()
    c.execute("SELECT fw0 FROM words group by fw0 ")
    rows = c.fetchall()
    for w in rows:
        fw = w[0]
        c.execute("SELECT fw FROM c_dict where fw=?", (fw,))
        r2 = c.fetchall()
        if r2 and len(r2)>0:
            continue

        print(fw)
        await asyncio.sleep(2+random.randint(1,10))
        pronunciations, entries, link, status =  await scrape_lemma(fw)
        if status == "banned":
            logger.error(f"!!!!!!!!!!! CAMBRIGE DICT BANNED for fw = {fw}")
            print(f"!!!!!!!!!!! CAMBRIGE DICT BANNED for hw = {fw}")
            exit(1)
        
        if status == "error": #неизвестно (таймаут, сбой, непредвиденный код).
            logger.warning(f"cambrige dict: link is None for fw={fw}, skip")
            continue

        if status == "not_found": #страницы точно нет.
            logger.warning(f"cambrige dict: link == False for fw={fw}")
            c.execute("INSERT OR REPLACE INTO c_dict (fw, source_url) VALUES (?, ?)", (fw, None))
            db.commit()            
            continue
        if not pronunciations and not entries:
            logger.warning(f"cambrige dict: no entries for fw={fw}")
            #like status == "not_found"
            c.execute("INSERT OR REPLACE INTO c_dict (fw, source_url) VALUES (?, ?)", (fw, None))
            db.commit()            
            continue

        if not pronunciations and entries:
            c.execute("INSERT OR REPLACE INTO c_dict (fw, source_url, is_pron) VALUES (?, ?, ?)", (fw, link, 0))
            db.commit()            
            continue
        
        # print("Pronunciations:")
        # print(json.dumps(pronunciations, indent=2, ensure_ascii=False))
        # print("\nEntries:")
        # print(json.dumps(entries, indent=2, ensure_ascii=False))

        region_nums = {
                "uk": {},  # audio_link -> num
                "us": {},  # audio_link -> num
        }
        dl_ok = 'UNKNOWN'
        for p in pronunciations:
            hw = p.get('hw')
            region = (p.get('region') or "").lower().strip()
            audio_link = p.get('audio')
            pos = p.get('pos')
            ipa = p.get('ipa')
            
            if not hw:
                continue
            if region not in ("uk", "us"):
                continue
            if not pos or not audio_link:
                continue
            
            num, is_new = get_num_for_link(region_nums[region], audio_link)
            dst_filename = f"{hw}.{region}.{num}.ogg"
            # change slahes in hw to _
            dst_filename = re.sub(r"[\\/]", "_", dst_filename)
            # change first '-' in hw to '_'
            if dst_filename[0] == '-':
                dst_filename = "_" + dst_filename[1:]
            full_path = os.path.join(AUDIO_PATH, fw[0].lower(), dst_filename)

            
            if is_new and os.path.exists(full_path):
                logger.info(f"cambrige dict audio must be new but it already exists: {full_path}")
                os.remove(full_path) #remove old file
            
            if not is_new and not os.path.exists(full_path):
                logger.warning(f"cambrige dict file must exist but it does not: {full_path}")
            
            if not os.path.exists(full_path):
                dl_ok = await download_file(audio_link, full_path)
                if not dl_ok:
                    logger.error(f"!!!!!!!cambrige dict download error: {audio_link} for {hw}")
                    # если хоть один файл не скачался, то пропускаем всё слово, потом докачаем.
                    break
            
            if dl_ok == True:
                pos = str_to_posdb(pos)
                c.execute("INSERT OR REPLACE INTO c_dict_pron (fw, hw, pos, region, ipa, fn, entry_num) VALUES (?, ?, ?, ?, ?, ?, ?)", 
                            (fw, hw, pos, region, ipa, dst_filename, p.get('entry_num', 0)))

        if dl_ok == True:
            c.execute("INSERT OR REPLACE INTO c_dict (fw, source_url, is_pron) VALUES (?, ?, ?)", (fw, link, 1))
            db.commit()
            raw_json = json.dumps(entries, indent=None, ensure_ascii=False) if entries is not None else None
            save_json(fw, raw_json)
        else:
             #если хоть один файл не скачался, то пропускаем всё слово, потом докачаем.
            db.rollback()
            logger.error(f"!!!!!!!cambrige dict download error: skip word fw={fw}")
    close_db(db)


import asyncio
if __name__ == "__main__":
    asyncio.run(run_scrap())

