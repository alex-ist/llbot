const VER = 19

let query_id;

class Card {
    constructor(cid, direction, foreignW, nativeW, example, d_link) {
        this.cid = cid;
        this.direction = direction;
        this.foreignW = foreignW;
        this.nativeW = nativeW;
        this.example = example;
        this.answer = -1;  // not showed card
        this.dict_lnk = d_link;
		this.a_lnk=`/au/en/w/${foreignW}.ogg?q=${query_id}`
        this.audio = null; 
    }
    //вернет слово для изучения
    getA(){
        if (this.direction==0)
            return this.foreignW;
        else
            return this.nativeW;
    }
    loadAudio() {
        return new Promise((resolve, reject) => {
            this.audio = new Audio(this.a_lnk);
            this.audio.addEventListener('canplaythrough', resolve);
            this.audio.addEventListener('error', reject);
        });
    }    
}

class CardSet {
    constructor() {
        this.cards = [];
        this.currentCardIndex = 0;
    }
    
    addCard(card) {
        this.cards.push(card);
    }

    getLen(){
        return this.cards.length;
    }

    // Возвращает текущую карточку
    getCurrentCard() {
        if (this.cards.length>0)
            return this.cards[this.currentCardIndex];
        else
            return null;
    }

    // Возвращает следующую карточку
    getNextCard() {
        return this.cards[(this.currentCardIndex + 1) % this.cards.length];
    }

    // Устанавливает ответ для текущей карточки
    setAnswer(val) {
        this.getCurrentCard().answer = val;
        if (val == 1) {
            this.cards.splice(this.currentCardIndex, 1);
            if (this.currentCardIndex >= this.cards.length) {
                this.currentCardIndex = 0;
            }
            document.querySelector('.txt-counter').textContent =this.cards.length;
    
        } else if (val == 0) {
            let card = this.cards.splice(this.currentCardIndex, 1)[0];
            this.cards.push(card);
        }
    }
}

async function getHash(inputString) {
    const encoder = new TextEncoder();
    const data = encoder.encode(inputString);
    const hashBuffer = await crypto.subtle.digest('SHA-256', data);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
    return hashHex.substring(0, 12);
}

//playAudio("https://lingolink.bot.nu/au/en/audio_words/disposal.ogg");
// Создание тестового CardSet
cardSet = new CardSet();
isSoundEnabled = true
var container = document.getElementById('container');
var maxWidth=container.offsetWidth;
let flash0 = document.getElementById('flash0');
let flash1 = flash0.cloneNode(true);
flash1.id = 'flash1';
flash1.style.zIndex = -1;
flash0.parentNode.insertBefore(flash1, flash0.nextSibling); // Вставляем новый элемент сразу после оригинала
upFlash=flash0;
downFlash=flash1;
let ss='q';

function d() {
    return Date.now()/1000;
}

var last_audio;
async function playAudio(audioSrc) {
    let c=cardSet.getCurrentCard();
    if (c) {
        stopPlayAudio();
    
        if (audioSrc == "fw") {
            last_audio=c.audio;
        }
        else if (audioSrc == "ex") {
            const hash = await getHash(c.example);
            console.log(hash + ":" + c.example);
            let s_link = "/au/en/e/" + hash + ".ogg?q=" + query_id + "&c=" + c.cid;
            last_audio = new Audio(s_link);
            console.log("E:" + s_link);
        }            
        else
            return;
        last_audio.play();
    }
}


function stopPlayAudio() {
    if (last_audio) {
        last_audio.pause();
        last_audio.currentTime = 0;
    }
    last_audio = null
}


async function updateCardUI(fl, card) {
    if (card) {
        let front=fl.querySelector(".front");
        let frontForeign = front.querySelector(".foreign");
        let frontNative = front.querySelector(".native");
        let back=fl.querySelector(".back");
        if (card.direction==0)  { //show foreign
            frontForeign.querySelector(".foreign-text").textContent = card.foreignW;
            frontNative.style.display = "none";
            frontForeign.style.display = "flex";
        } else {
            frontNative.querySelector(".native-text").textContent = card.nativeW;
            frontForeign.style.display = "none";
            frontNative.style.display = "flex";
        }
        front.style.display = "flex";
        
        var old_ft=back.querySelector(".foreign-text");
        if (card.dict_lnk === undefined) 
            new_ft = document.createElement('div');
        
        else 
        {
            new_ft = document.createElement('a');
            new_ft.href = card.dict_lnk;
            new_ft.target = '_blank';
            console.log("lnk: " + card.dict_lnk);
        }
        new_ft.className = 'foreign-text';
        new_ft.textContent = card.foreignW;
        old_ft.parentNode.replaceChild(new_ft, old_ft);

        back.querySelector(".native-text").textContent = card.nativeW;
        back.querySelector(".example-text").textContent = card.example;
        back.style.display = "flex";
    }
    else
        fl.style.display = "none";
}

var BREAK_POINT = maxWidth / 6;
var mc = new Hammer.Manager(container);
mc.add(new Hammer.Pan({
    direction: Hammer.DIRECTION_ALL,
    threshold: 5,
    pointers: 0
}));


mc.add(new Hammer.Tap());
mc.on("tap", async function (ev) {
    if (ev.target.closest('img'))
        return;

    if (ss=='q') {
        ss='a';
        gsap.to(upFlash, {
            duration: 0.7, rotationY: 180, ease: Back.easeOut,
        });

        if (isSoundEnabled) {
            let card = cardSet.getCurrentCard();
            if (card && card.direction != 0) {
                await playAudio("fw");
                console.log("play1: d=" + card.direction + "  fw=" + card.foreignW);
            }
        }
    }
});


mc.on("panleft panright panup", function (ev) {
    let rot=-48.0*ev.deltaX/maxWidth;
    let op=Math.min(Math.abs(4.0*ev.deltaX)/maxWidth, 1.0);
    gsap.set(upFlash, {x: ev.deltaX, y: ev.deltaY, rotation: rot});
    if (ev.deltaX<0) {
        gsap.set(".corner-box-left", {opacity: op});
        gsap.set(".corner-box-right", {opacity: 0});
    } else {
        gsap.set(".corner-box-right", {opacity: op});
        gsap.set(".corner-box-left", {opacity: 0});
    }
});

async function endPan(ev) {
    if (Math.abs(ev.deltaX) > BREAK_POINT) {
        document.querySelector('.info-msg').textContent="";        

        const dataToSend = {
            type:   "answer",
            cid:    cardSet.getCurrentCard().cid,
            a:      ev.deltaX>0?1:0,
        };
        let r=JSON.stringify(dataToSend)
        ws.send(r);
        console.log("sent:" + r);
        cardSet.setAnswer(ev.deltaX>0 ? 1 : 0 );
        if (isSoundEnabled) {
            let card=cardSet.getCurrentCard();
            if (card && card.direction==0){
                await playAudio("fw");
                console.log("play1: d=" + card.direction+"  fw="+card.foreignW);
            }
        }

        gsap.to(upFlash, 0.3, { 
            ease: Cubic.easeInOut, 
            x: ev.deltaX>0 ? '120%' : '-120%', 
            onCompleteParams: [upFlash],
            onComplete: async function(v) {
                cardSet.getCurrentCard()
                v.style.zIndex -= 2;
                if (cardSet.getLen()>=2) {
                    u=upFlash;
                    upFlash=downFlash;
                    downFlash=u;    
                    await updateCardUI(downFlash, cardSet.getNextCard());
                }
                else if (cardSet.getLen()==1) {
                    await updateCardUI(downFlash, null);
                    await updateCardUI(upFlash, cardSet.getNextCard());
                }
                else {
                    await updateCardUI(upFlash, null);
                    const dataToSend = {
                        type: "stop-tren"
                    };
                    let r=JSON.stringify(dataToSend)
                    ws.send(r);
                    console.log("sent:" + r);
                    //конец, нет больше карточек
                }
                ss='q';
                gsap.set(v, {x: '0%', y: '0%', rotation: 0, rotationY:0});
            }
        });
    } else
        gsap.to(upFlash, .2, {
            ease: Cubic.easeInOut,
            x: '0%',
            y: '0%',            
            rotation: 0            
        });
        gsap.to(".corner-box",  .2, {opacity: 0});

}
mc.on("panend pancancel", endPan);


let tg=window.Telegram.WebApp;
tg.expand();

let init_data = tg.initData ? tg.initData: "NoInitData";
let uid=484679683;
if (init_data!="NoInitData")
    uid=tg.initDataUnsafe.user.id;

let protocol = window.location.protocol == 'https:' ? 'wss:' : 'ws:';
let addr=protocol + '//' + window.location.host + '/tren-wh/';
console.log(d()+":WS addr:" + addr);
const ws = new WebSocket(addr);


tg.ready()
function startConn() {
    console.log(d()+":connected");
    const dataToSend = {
         init_data: tg.initData,
         type: "start-tren",
         ver: VER
        };
    
    let r=JSON.stringify(dataToSend)
    ws.send(r);
    //extract query_id
    let params = new URLSearchParams(tg.initData);
    query_id = params.get('query_id');
    if (query_id == null)
        query_id=1;

    console.log(d()+":sent:" + r + " : query_id="+query_id);
}

ws.addEventListener('open', () => {
  startConn()
});

cmd_reload=0;
ws.addEventListener('message', async (event) => {
    const receivedData = JSON.parse(event.data);
    console.log(d()+"Rx data:", receivedData);
    if (receivedData.type === "cmd-reload") {
        cmd_reload=1;
        window.location.reload(true); // <--no return from here
        return
    }
    else if (receivedData.type === "tren-data") {
        if ('autoplay' in receivedData) 
            setAutoPlay(receivedData.autoplay, by_ui=false);
        receivedData.card.forEach(cardData => {
            cardSet.addCard(new Card(cardData.cid, cardData.dir, cardData.fw, cardData.nw, cardData.ex, cardData.lnk));
        });
    
        document.querySelector('.txt-counter').textContent =cardSet.cards.length;

        await updateCardUI(upFlash, cardSet.getCurrentCard())
        upFlash.style.zIndex = 0;
        
        await updateCardUI(downFlash, cardSet.getNextCard())
        downFlash.style.zIndex = -2;

        // Последовательно загружаем аудиофайлы
        for (const card of cardSet.cards) {
            try {
                await card.loadAudio();
                console.log(d()+`:Audio for ${card.foreignW} loaded`);
            } catch (error) {
                console.log(d()+`:Error loading audio for ${card.foreignW}:`, error);
            }
        }            
    }
    else if (receivedData.type === "info-msg") {
        console.log("Rx info msg:"+receivedData.text);
        document.querySelector('.info-msg').textContent=receivedData.text;        
    }
});

ws.addEventListener('close', () => {
    console.log("closed ws");
    if (!cmd_reload)
        tg.close()
});

var speakerE = document.querySelector('.speaker-e');
var speakerD = document.querySelector('.speaker-d');

function save_auto_play() {
    const dataToSend = {
        type:   "autoplay",
        val:   isSoundEnabled?1:0
    };
    let r=JSON.stringify(dataToSend)
    ws.send(r);
}

function setAutoPlay(new_val, by_ui=true) {
    if (new_val==false){
        isSoundEnabled=false
        speakerE.style.display = 'none';
        speakerD.style.display = 'inline-block';    
    }
    else 
    {
        isSoundEnabled=true
        speakerD.style.display = 'none';
        speakerE.style.display = 'inline-block';    
    }
    if (by_ui)
        save_auto_play()
}

function invertAutoPlay() {
    setAutoPlay(!isSoundEnabled, by_ui=true);
}

speakerE.addEventListener('click', invertAutoPlay);
speakerD.addEventListener('click', invertAutoPlay);



let mic_control_type = "0"

async function startRecording_m()  {
    if (mic_control_type=="0")
        mic_control_type ="m";
    
    if (mic_control_type!="m")
        return;
    console.log("startRecording_m");
    await startRecording();
}

function stopRecording_m()  {
    if (mic_control_type!="m")
        return;
    console.log("stopRecording_m");
    stopRecording();
}

async function startRecording_t()  {
    if (mic_control_type=="0")
        mic_control_type ="t";
    if (mic_control_type!="t")
        return;
    console.log("startRecording_t");
    await startRecording();
}

function stopRecording_t()  {
    if (mic_control_type!="t")
        return;
    console.log("stopRecording_t");
    stopRecording();
}

let mediaRecorder;
let audioChunks = [];
let mic_inited =false;
// Получение доступа к микрофону
async function init_mic() {
    if (mic_inited)
        return;
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        const options = { mimeType: 'audio/webm', audioBitsPerSecond: 24000 };
        mediaRecorder = new MediaRecorder(stream, options);
        mediaRecorder.ondataavailable = event => {
            audioChunks.push(event.data);
        };
        mic_inited = true;
    } catch (error) {
        console.error("mic init error:", error);
    }        
}

async function checkMicStatus() {
    try {
        const permissionStatus = await navigator.permissions.query({ name: 'microphone' });
        
        if (permissionStatus.state === 'granted') {
            console.log('Доступ к микрофону уже предоставлен.');
            return true;
        } else if (permissionStatus.state === 'prompt') {
            console.log('Разрешение на доступ к микрофону ещё не запрашивалось.');
            return false;
        } else {
            console.log('Доступ к микрофону запрещён.');
            return false;
        }
    } catch (error) {
        console.error('Ошибка при проверке разрешения микрофона:', error);
        return false;
    }
}


async function startRecording() {
  audioChunks = [];
  mic_st=await checkMicStatus();
  await init_mic();
  if (mic_inited && mediaRecorder && mic_st) { //если доступа к микрофону еще не было, то придется нажимать кнопку в запросе, и поэтому не сможем нормально отловить отжатие кнопки микрофона
    
    mediaRecorder.start();
    console.log("mediaRecorder.start");
  }
}

function stopRecording() {
  mediaRecorder.stop();
  mediaRecorder.onstop = () => {
    const audioBlob = new Blob(audioChunks);
    sendAudioToServer(audioBlob);
  };
}

function sendAudioToServer(audioBlob) {
    const dataToSend = {
        type:  "rec-voice",
        val:   audioBlob
    };
    let r=JSON.stringify(dataToSend)
    ws.send(r);
    if (uid==484679683 || uid==5800537837){
        ws.send(audioBlob);
        console.log("sendAudioToServer");
    }
}


