"use strict";
const VER = 56
let query_id;

class Card {
    constructor(cardData, q_id) {
        this.cid = cardData.cid;
        this.direction = cardData.dir;
        this.foreignW = cardData.fw;
        this.nw_list = cardData.nw_list;
        this.pos = cardData.pos;
        this.example = cardData.ex;
        this.native_example = cardData.n_ex;
        this.answer = -1;  // not showed card
        this.dict_lnk = cardData.lnk;
        this.q_id = q_id;
        const firstLetter = this.foreignW[0].toLowerCase();
		this.a_lnk=`/au/en/w/${firstLetter}/${this.foreignW}.ogg?q=${q_id}`;
        const cdict_au = cardData.cdict_au;
        this.cdict_a_lnk = cdict_au ? `/au/en/w/${firstLetter}/${cdict_au}?q=${q_id}` : null;
        this.ipa = cardData.ipa;
        this.audio = null; 
    }
    //вернет слово для изучения
    getA(){
        if (this.direction==0)
            return this.foreignW;
        else
            return this.nw_list[0];
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
            return this.cards[0];
        else
            return null;
        }
    
    // Возвращает следующую карточку
    getNextCard() {
        if (this.cards.length>1)
            return this.cards[1];
        else {
            console.log("getNextCard->nul");
            return null;}
    }

    // Устанавливает ответ для текущей карточки
    setAnswer(val) {
        this.getCurrentCard().answer = val;
        if (val == 1) {
            this.removeCurrentCard();
        } else //if (val == 0)
        {
            let card = this.cards.splice(0, 1)[0];
            if (this.cards.length > 10)
                this.cards.splice(9, 0, card); 
            else
                this.cards.push(card); // Добавление карты в конец массива, если в нем меньше 10 карт
        }
    }
    // удаляет текущую карточку
    removeCurrentCard() {
        if (this.cards.length > 0) {
            this.cards.splice(0, 1);
            document.querySelector('.txt-counter').textContent = this.cards.length;
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
const cardSet = new CardSet();
let isSoundEnabled = true
const flashContainer = document.getElementById('flashContainer');

// const flash = document.getElementById('flash');
let maxWidth = document.getElementById('container').offsetWidth;
maxWidth = maxWidth ? maxWidth : 100; 
let maxHeight = document.getElementById('container').offsetHeight;
maxHeight = maxHeight ? maxHeight : 200;

console.log("maxWidth=" + maxWidth);
const flash0 = document.getElementById('flash0');
const flash1 = flash0.cloneNode(true);
flash1.id = 'flash1';
flash0.parentNode.insertBefore(flash1, flash0.nextSibling); // Вставляем новый элемент сразу после оригинала
let upFlash=flash0;
let downFlash=flash1;
let ss='q';

function d() {
    return Date.now()/1000;
}

let last_audio;
async function playAudio(audioSrc) {
    let c=cardSet.getCurrentCard();
    if (c) {
        stopPlayAudio();
    
        if (audioSrc == "fw") {
            last_audio=c.audio;
        }
        else if (audioSrc == "ex") {
            const hash = await getHash(c.example);
            //console.log(hash + ":" + c.example);
            let s_link = "/au/en/e/" + hash + ".ogg?q=" + query_id + "&c=" + c.cid;
            last_audio = new Audio(s_link);
            //console.log("E:" + s_link);
        }
        else
            return;

        try {
            await last_audio.play();
        } catch (err) {
            console.warn('Audio play failed:', err);
        }            
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
        const front=fl.querySelector(".front");
        const frontForeign = front.querySelector(".foreign");
        const frontNative = front.querySelector(".native");

        let n_text = card.nw_list[0];
        for (let i = 1; i < card.nw_list.length; i++) {
            if (card.nw_list[i])
                n_text += ", " + card.nw_list[i];
            else
                break;
        }
        let pos_text = card.pos ? card.pos : "";
        if (pos_text == "phrase" || pos_text == "other")
            pos_text = "";

        let ipa_text = card.ipa ? card.ipa : "";
        let reg_text = "us";


        if (card.direction==0)  { //show foreign
            frontNative.style.visibility = "hidden";
            frontForeign.querySelector(".foreign-text").textContent = card.foreignW;
            frontForeign.querySelector(".pos-text").textContent = pos_text;
            frontForeign.querySelector(".ipa_text").textContent = ipa_text;
            frontForeign.querySelector(".reg_text").textContent = reg_text;
            frontForeign.style.visibility = "visible";

        } else {
            frontForeign.style.visibility = "hidden";
            frontNative.querySelector(".native-text").textContent = n_text;
            frontNative.style.visibility = "visible";
        }
        const back =fl.querySelector(".back");
        const backExampleText = back.querySelector(".example .example-text");

        backExampleText.querySelector(".ex-native").textContent  = card.native_example || "";
        backExampleText.querySelector(".ex-native").style.opacity = 1;

        backExampleText.querySelector(".ex-foreign").textContent = card.example || "";
        backExampleText.querySelector(".ex-foreign").style.opacity = 0;
        backExampleText.dataset.state = "native";

        backExampleText.onclick = () => toggleExample(backExampleText);

        // front.style.display = "flex";
        
        let old_ft=back.querySelector(".foreign-text");
        let new_ft;
        if (card.dict_lnk === undefined) 
            new_ft = document.createElement('div');
        else 
        {
            new_ft = document.createElement('a');
            new_ft.href = card.dict_lnk;
            new_ft.target = '_blank';
            // console.log("lnk: " + card.dict_lnk);
        }
        new_ft.className = 'foreign-text';
        new_ft.textContent = card.foreignW;
        old_ft.parentNode.replaceChild(new_ft, old_ft);
        back.querySelector(".native-text").textContent = n_text;
        back.querySelector(".foreign .pos-text").textContent = pos_text;
        if (ipa_text){
            back.querySelector(".foreign .ipa-text").textContent = `/${ipa_text}/`;
            back.querySelector(".foreign .reg-text").textContent = `${reg_text}: `;
        } else {
            back.querySelector(".foreign .ipa-text").textContent = "";
            back.querySelector(".foreign .reg-text").textContent = "";
        }

        // back.style.display = "flex";
    }
    else
        fl.style.display = "none";
}

async function tapHandler (ev) {
    await mic_off();
    if (ev.target.closest('img'))
        return;

    await flipFlash()
}

async function flipFlash(){
    if (ss=='q') {
        ss='a';
        gsap.to(upFlash, {
            duration: 0.7, rotationY: 180, ease: Back.easeOut,
        });

        if (isSoundEnabled) {
            let card = cardSet.getCurrentCard();
            if (card && card.direction != 0) {
                await playAudio("fw");
                // console.log("play1: d=" + card.direction + "  fw=" + card.foreignW);
            }
        }
    }

}

async function startPan(ev) {
    await mic_off();
    let rot = -48.0*ev.deltaX/maxWidth;
    gsap.set(upFlash, {x: ev.deltaX, y: ev.deltaY, rotation: rot});
    const absDX = Math.abs(ev.deltaX);
    const absDY = Math.abs(ev.deltaY);

    // 1) горизонтальный жест
    if (absDX >= absDY) {
        const op = Math.min(absDX * 4 / maxWidth, 1);
        if (ev.deltaX<0) {
            gsap.set(".corner-box-left", {opacity: op});
            gsap.set(".corner-box-right", {opacity: 0});
        } else {
            gsap.set(".corner-box-right", {opacity: op});
            gsap.set(".corner-box-left", {opacity: 0});
        }
    }
    // 2) вертикальный жест «вверх»
    else if (ev.deltaY < 0) {
    }
}

async function completeSwipe(){
    upFlash.style.zIndex -= 2; // перетаскиваем html карточки назад
    ss='q';
    gsap.set(upFlash, {x: '0%', y: '0%', rotation: 0, rotationY:0, scale: 1, opacity: 1});

    if (cardSet.getLen()>=1) {
        const u=upFlash;
        upFlash=downFlash;
        downFlash=u;
        await updateCardUI(downFlash, cardSet.getNextCard());
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
}

async function endPan(ev) {
    const BREAK_POINT = maxWidth / 6;
    
    // Determine if this was primarily an upward swipe for removal
    const isUpwardDominant = ev.deltaY < 0 && Math.abs(ev.deltaY) > Math.abs(ev.deltaX);
    
    // Handle upward swipe for removal - only if upward is dominant and exceeds threshold
    if (isUpwardDominant && Math.abs(ev.deltaY) > BREAK_POINT*2) {
        await showRemovalConfirmation();
        return;
    }


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
            onComplete: completeSwipe
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


let mc = new Hammer.Manager(flashContainer);
mc.add(new Hammer.Pan({
    direction: Hammer.DIRECTION_ALL,
    threshold: 5,
    pointers: 0
}));

mc.add(new Hammer.Tap());
mc.on("tap", tapHandler);
mc.on("panleft panright panup", startPan);
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
    console.log(d()+":sent:" + r + " : query_id="+query_id);
    if (query_id == null)
        query_id=1;

}

ws.addEventListener('open', () => {
  startConn()
});

let cmd_reload=0;
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
            setAutoPlay(receivedData.autoplay, false);

        receivedData.card.forEach(cardData => {
            cardSet.addCard(new Card(cardData, query_id));
        });
    
        document.querySelector('.txt-counter').textContent =cardSet.cards.length;

        await updateCardUI(upFlash, cardSet.getCurrentCard())
        upFlash.style.zIndex = 0;
        
        await updateCardUI(downFlash, cardSet.getNextCard())
        downFlash.style.zIndex = -1;

        // Последовательно загружаем аудиофайлы
        let loadedCount = 0;
        for (const card of cardSet.cards) {
            try {
                await card.loadAudio();
                console.log(d()+`:Audio for ${card.foreignW} loaded`);
            } catch (error) {
                console.log(d()+`:Error loading audio for "${card.foreignW}":`, error);
            }
            loadedCount++;
            if (loadedCount === 2) { // Если загружено 2 карточки, скрываем индикатор и показываем карточки
                downFlash.querySelector(".loading").style.display = 'none';
                downFlash.querySelector(".front").style.display = 'flex';
                upFlash.querySelector(".loading").style.display = 'none';
                upFlash.querySelector(".front").style.display = 'flex';
            }
        }
    }
    else if (receivedData.type === "info-msg") {
        console.log("Rx info msg:"+receivedData.text);
        document.querySelector('.info-msg').innerHTML=receivedData.text;
    }
    else if (receivedData.type === "flip-flash") {
        console.log("flip-flash");
        await flipFlash()
    }
});

ws.addEventListener('close', () => {
    console.log("closed ws");
    mc.destroy();        
    if (!cmd_reload)
        tg.close()
});

let speakerE = document.querySelector('.speaker-e');
let speakerD = document.querySelector('.speaker-d');

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
    setAutoPlay(!isSoundEnabled, true);
}

speakerE.addEventListener('click', invertAutoPlay);
speakerD.addEventListener('click', invertAutoPlay);


//mic handling
let play_s1 = new Audio("/3.ogg");
let play_s2 = new Audio("/2.ogg");
play_s2.volume = 0.6;
play_s1.volume = 0.35;

async function playS1() {
    play_s2.pause();
    play_s1.currentTime = 0; 

    try {
        await play_s1.play();
        return new Promise((resolve) => {
            play_s1.onended = resolve; // устанавливаем обработчик для окончания воспроизведения
        });
    } catch (error) {
        console.error("Ошибка при воспроизведении звука 1:", error);
    }
}

function playS2() {
    play_s1.pause();
    play_s2.currentTime = 0;
    play_s2.play();
}

let mediaRecorder;
let audioChunks = [];
let mic_inited =false;
let mic_record_on  =false;

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

let micIcon = document.querySelector('.micbut img');
let micTimeout;

async function micbut_click() {
    console.log("MC");
    if (!mic_inited) {
        await init_mic();
        if (mic_inited)
            micIcon.src = "img/micbut1.png";
        return
    }
    if (mic_record_on) {
        clearTimeout(micTimeout);
        await mic_off();
    }
    else {
        await mic_on();
        micTimeout = setTimeout(mic_off, 10000);
    }
}

async function mic_off() {
    if (mic_record_on) {
        console.log("mic Rec OFF");
        mic_record_on = false;
        micIcon.src = "img/micbut1.png";
        await stopRecording();
        playS2();
    }
}

async function mic_on() {
    if (!mic_record_on) {
        micIcon.src = "img/micbut2.png";
        console.log("mic Rec ON");
        mic_record_on = true;
        await playS1();
        await startRecording();
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
  await init_mic();
  if (mic_inited && mediaRecorder)
  {
    mediaRecorder.start();
    console.log("mediaRecorder.start");
  }
}

function stopRecording() {
  mediaRecorder.onstop = () => {
    const audioBlob = new Blob(audioChunks);
    sendAudioToServer(audioBlob);
  };
  mediaRecorder.stop();
}

function sendAudioToServer(audioBlob) {
    const cur_card=cardSet.getCurrentCard();

    const dataToSend = {
        type:  "rec-voice",
        lang:   cur_card.direction?"fw":"nw",
        cid:    cur_card.cid,
    };
    let r=JSON.stringify(dataToSend)
    ws.send(r);
    //if (uid==484679683 || uid==5800537837){
        ws.send(audioBlob);
        //console.log("sendAudioToServer");
    //}
}


// Confirmation dialog functions
async function showRemovalConfirmation() {
    return new Promise((resolve) => {
        const currentCard = cardSet.getCurrentCard();
        if (!currentCard) {
            resolve(false);
            return;
        }
        gsap.to(".corner-box",  .2, {opacity: 0});

        let modal = document.createElement('div');
        modal.className = 'removal-modal';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-text">Remove "${currentCard.foreignW}" from your learning list?</div>
                <div class="modal-buttons">
                    <button class="modal-btn modal-cancel">Cancel</button>
                    <button class="modal-btn modal-confirm">Remove</button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Show modal with animation
        gsap.fromTo(modal, 
            {opacity: 0, scale: 0.8}, 
            {opacity: 1, scale: 1, duration: 0.3, ease: "back.out(1.7)"}
        );
        
        // Handle button clicks
        modal.querySelector('.modal-cancel').onclick = () => {
            hideModal(modal);
            resetCardPosition();
            resolve(false);
        };
        // Hide modal on background click
        modal.onclick = (e) => {
            if (e.target === modal) {
                hideModal(modal);
                resetCardPosition();
                resolve(false);
            }
        };
        
        modal.querySelector('.modal-confirm').onclick = () => {
            hideModal(modal);
            removeWord(currentCard);
            resolve(true);
        };
    });
}

function hideModal(modal) {
    gsap.to(modal, {
        opacity: 0, 
        scale: 0.8, 
        duration: 0.2, 
        onComplete: () => modal.remove()
    });
}

// Reset card position after cancelled removal
function resetCardPosition() {
    gsap.to(upFlash, .2, {
        ease: Cubic.easeInOut,
        x: '0%',
        y: '0%',            
        rotation: 0            
    });
}

// Remove word function
async function removeWord(card) {
    const dataToSend = {
        type: "remove-word",
        cid: card.cid,
    };
    let r = JSON.stringify(dataToSend);
    ws.send(r);
    console.log("sent remove-word:" + r);
    
    // Remove from current set and update UI
    cardSet.removeCurrentCard();

        
    // // Show success animation and message
    showSuccessAnimation(card.foreignW);

    // Animate card removal with upward fade-out
    gsap.to(upFlash, 0.4, { 
        ease: Cubic.easeInOut, 
        y: '-150%',
        opacity: 0,
        scale: 0.8,
        onComplete: completeSwipe
    });
}

// Success animation for word removal
function showSuccessAnimation(word) {
    const infoMsg = document.querySelector('.info-msg');
    
    // Show success message with animation
    infoMsg.innerHTML = `✓ "${word}" removed`;
    
    gsap.fromTo(infoMsg, 
        {opacity: 0, y: -20}, 
        {opacity: 1, y: 0, duration: 0.5, ease: "back.out(1.7)"}
    );
    
    // Auto-hide after 2 seconds
    setTimeout(() => {
        gsap.to(infoMsg, {
            opacity: 0, 
            duration: 0.3,
            onComplete: () => {
                infoMsg.textContent = '';
            }
        });
    }, 2000);
}

function toggleExample(wrap) {
  const toForeign = wrap.dataset.state === "native";
  const exN = wrap.querySelector(".ex-native");
  const exF = wrap.querySelector(".ex-foreign");
 
  if (toForeign) {
    wrap.dataset.state = "foreign";
    gsap.to(exN, { opacity: 0, duration: 0.2 });
    gsap.to(exF, { opacity: 1, duration: 0.2, onComplete: () => playAudio("ex") });
  } else {
    wrap.dataset.state = "native";
    gsap.to(exF, { opacity: 0, duration: 0.2 });
    gsap.to(exN, { opacity: 1, duration: 0.2 });
 
  }
}