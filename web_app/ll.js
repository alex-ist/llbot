"use strict";
const VER = 51
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
            this.cards.splice(0, 1);
            document.querySelector('.txt-counter').textContent =this.cards.length;
    
        } else //if (val == 0)
        {
            let card = this.cards.splice(0, 1)[0];
            if (this.cards.length > 10)
                this.cards.splice(9, 0, card); 
            else
                this.cards.push(card); // Добавление карты в конец массива, если в нем меньше 10 карт
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
const maxWidth=document.getElementById('container').offsetWidth;
const flash0 = document.getElementById('flash0');
const flash1 = flash0.cloneNode(true);
flash1.id = 'flash1';
flash1.style.zIndex = -1;
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
                console.log("play1: d=" + card.direction + "  fw=" + card.foreignW);
            }
        }
    }

}

async function satrtPan(ev) {
    await mic_off();
    let rot=-48.0*ev.deltaX/maxWidth;
    let op=Math.min(Math.abs(4.0*ev.deltaX)/maxWidth, 1.0);
    
    // Determine if this is primarily an upward swipe for removal
    let isUpwardDominant = ev.deltaY < 0 && Math.abs(ev.deltaY) > Math.abs(ev.deltaX) * 1.5;
    let UP_THRESHOLD = maxWidth / 8; // Minimum upward distance to trigger deletion mode
    
    // Preserve the current rotationY (flip state) during swipes
    let currentRotationY = ss === 'a' ? 180 : 0;
    
    if (isUpwardDominant && Math.abs(ev.deltaY) > UP_THRESHOLD) {
        // Handle upward swipe for removal - only when upward is dominant gesture
        let upOp = Math.min(Math.abs(2.0*ev.deltaY)/maxWidth, 1.0);
        gsap.set(upFlash, {
            x: ev.deltaX, 
            y: ev.deltaY, 
            rotationZ: 0, 
            rotationY: currentRotationY,
            scale: 1 - upOp * 0.3,
            filter: `brightness(${1 - upOp * 0.2}) sepia(${upOp * 0.3})`
        });
        gsap.set(".corner-box-left", {opacity: 0});
        gsap.set(".corner-box-right", {opacity: 0});
        showRemovalIndicator(upOp);
    } else {
        // Handle normal horizontal swipes or insufficient upward movement
        gsap.set(upFlash, {
            x: ev.deltaX, 
            y: ev.deltaY, 
            rotationZ: rot,  // Use rotationZ instead of rotation to avoid conflicts
            // ↓ задаём собственный шаблон, где Y идёт первым
            transformTemplate: ({rotationY, rotationZ}) =>
                `rotateY(${rotationY}deg) rotateZ(${rotationZ}deg)`,
              scale: 1, 
            filter: 'brightness(1) sepia(0)'
        });
        hideRemovalIndicator();
        if (ev.deltaX<0) {
            gsap.set(".corner-box-left", {opacity: op});
            gsap.set(".corner-box-right", {opacity: 0});
        } else {
            gsap.set(".corner-box-right", {opacity: op});
            gsap.set(".corner-box-left", {opacity: 0});
        }
    }
}

async function endPan(ev) {
    let BREAK_POINT = maxWidth / 6;
    let UP_BREAK_POINT = maxWidth / 4;
    let UP_THRESHOLD = maxWidth / 8;
    
    // Determine if this was primarily an upward swipe for removal
    let isUpwardDominant = ev.deltaY < 0 && Math.abs(ev.deltaY) > Math.abs(ev.deltaX) * 1.5;
    
    // Handle upward swipe for removal - only if upward is dominant and exceeds threshold
    if (isUpwardDominant && Math.abs(ev.deltaY) > UP_BREAK_POINT && Math.abs(ev.deltaY) > UP_THRESHOLD) {
        hideRemovalIndicator();
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
                    await updateCardUI(upFlash, cardSet.getCurrentCard());
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
                gsap.set(v, {x: '0%', y: '0%', rotationZ: 0, rotationY:0});
            }
        });
    } else {
        hideRemovalIndicator();
        let currentRotationY = ss === 'a' ? 180 : 0;
        gsap.to(upFlash, .2, {
            ease: Cubic.easeInOut,
            x: '0%',
            y: '0%',            
            rotationZ: 0,
            rotationY: currentRotationY,
            scale: 1,
            filter: 'brightness(1) sepia(0)'
        });
        gsap.to(".corner-box",  .2, {opacity: 0});
    }

}


var mc = new Hammer.Manager(flashContainer);
mc.add(new Hammer.Pan({
    direction: Hammer.DIRECTION_ALL,
    threshold: 5,
    pointers: 0
}));

mc.add(new Hammer.Tap());
mc.on("tap", tapHandler);
mc.on("panleft panright panup", satrtPan);
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
        document.querySelector('.info-msg').innerHTML=receivedData.text;
    }
    else if (receivedData.type === "flip-flash") {
        console.log("flip-flash");
        await flipFlash()
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
  mediaRecorder.stop();
  mediaRecorder.onstop = () => {
    const audioBlob = new Blob(audioChunks);
    sendAudioToServer(audioBlob);
  };
}

function sendAudioToServer(audioBlob) {
    cur_card=cardSet.getCurrentCard();

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

// Removal indicator functions - now just visual feedback without text
function showRemovalIndicator(opacity) {
    // Visual feedback through card scaling is handled in satrtPan function
    // No overlay text needed
}

function hideRemovalIndicator() {
    // Visual feedback cleanup is handled in resetCardPosition function
    // No overlay text to hide
}

// Confirmation dialog functions
async function showRemovalConfirmation() {
    return new Promise((resolve) => {
        let currentCard = cardSet.getCurrentCard();
        if (!currentCard) {
            resolve(false);
            return;
        }
        
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
        
        modal.querySelector('.modal-confirm').onclick = () => {
            hideModal(modal);
            removeWord(currentCard);
            resolve(true);
        };
        
        // Hide modal on background click
        modal.onclick = (e) => {
            if (e.target === modal) {
                hideModal(modal);
                resetCardPosition();
                resolve(false);
            }
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
    hideRemovalIndicator();
    let currentRotationY = ss === 'a' ? 180 : 0;
    gsap.to(upFlash, 0.2, {
        ease: Cubic.easeInOut,
        x: '0%',
        y: '0%',            
        rotationZ: 0,
        rotationY: currentRotationY,
        scale: 1,
        filter: 'brightness(1) sepia(0)'
    });
    gsap.to(".corner-box", 0.2, {opacity: 0});
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
    cardSet.cards.splice(0, 1);
    document.querySelector('.txt-counter').textContent = cardSet.cards.length;
    
    // Show success animation and message
    showSuccessAnimation(card.foreignW);
    
    // Animate card removal with upward fade-out
    gsap.to(upFlash, 0.4, { 
        ease: Cubic.easeInOut, 
        y: '-150%',
        opacity: 0,
        scale: 0.8,
        onCompleteParams: [upFlash],
        onComplete: async function(v) {
            // Update card display with proper z-index management
            v.style.zIndex -= 2;
            v.style.opacity = 1; // Reset opacity for next card
            
            if (cardSet.getLen() >= 2) {
                let u = upFlash;
                upFlash = downFlash;
                downFlash = u;
                await updateCardUI(downFlash, cardSet.getNextCard());
            } else if (cardSet.getLen() == 1) {
                await updateCardUI(downFlash, null);
                await updateCardUI(upFlash, cardSet.getCurrentCard());
            } else {
                await updateCardUI(upFlash, null);
                const dataToSend = {
                    type: "stop-tren"
                };
                let r = JSON.stringify(dataToSend)
                ws.send(r);
                console.log("sent:" + r);
            }
            
            ss = 'q';
            gsap.set(v, {x: '0%', y: '0%', rotationZ: 0, rotationY: 0, scale: 1, filter: 'brightness(1) sepia(0)'});
        }
    });
}

// Success animation for word removal
function showSuccessAnimation(word) {
    const infoMsg = document.querySelector('.info-msg');
    
    // Show success message with animation
    infoMsg.innerHTML = `✓ "${word}" removed`;
    infoMsg.style.color = 'rgba(123, 160, 135, 1)'; // Green color
    
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
                infoMsg.style.color = 'rgba(255, 255, 255, 0.9)'; // Reset to original color
            }
        });
    }, 2000);
}
