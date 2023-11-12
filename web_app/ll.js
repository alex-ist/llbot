const VER = 14

class Card {
    constructor(cid, direction, foreignW, nativeW, example, link) {
        this.cid = cid;
        this.direction = direction;
        this.foreignW = foreignW;
        this.nativeW = nativeW;
        this.example = example;
        this.answer = -1;  // not showed card
        this.lnk = link;
		this.a_lnk=`/au/en/w/${foreignW}.ogg`
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
ss='q';

function d() {
    return Date.now()/1000;
}

function playAudio(audioSrc) {
    let c=cardSet.getCurrentCard();
    if (c) {
        if (audioSrc == "fw") {
            c.audio.play();
            //console.log("F:"+s_link);
        }
        else if  (audioSrc == "ex")
            getHash(c.example).then(hash => {
                console.log(hash + ":"+ c.example);
                s_link="/au/en/e/"+hash+".ogg?uid="+user_id+"&cid="+c.cid;
                const audio = new Audio(s_link);
                audio.play();
                console.log("E:"+s_link);
            });
        else
            return;
    }
}

function updateCardUI(fl, card) {
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
        back.querySelector(".foreign-text").textContent = card.foreignW;
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
mc.on("tap", function (ev) {
    if (ev.target.closest('img'))
        return;

    if (ss=='q') {
        ss='a';
        gsap.to(upFlash, {duration: 0.7, rotationY:180, ease:Back.easeOut,
            onComplete: function(v) {
                if (isSoundEnabled) {
                    let card=cardSet.getCurrentCard();
                    if (card && card.direction!=0){
                        playAudio("fw");
                        console.log("play1: d=" + card.direction+"  fw="+card.foreignW);}
                }
            }
        });
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

function endPan(ev) {
    if (Math.abs(ev.deltaX) > BREAK_POINT) {
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
                playAudio("fw");
                console.log("play1: d=" + card.direction+"  fw="+card.foreignW);
            }
        }

        gsap.to(upFlash, 0.3, { 
            ease: Cubic.easeInOut, 
            x: ev.deltaX>0 ? '120%' : '-120%', 
            onCompleteParams: [upFlash],
            onComplete: function(v) {
                v.style.zIndex -= 2;
                if (cardSet.getLen()>=2) {
                    u=upFlash;
                    upFlash=downFlash;
                    downFlash=u;    
                    updateCardUI(downFlash, cardSet.getNextCard());
                }
                else if (cardSet.getLen()==1) {
                    updateCardUI(downFlash, null);
                    updateCardUI(upFlash, cardSet.getNextCard());
                }
                else {
                    updateCardUI(upFlash, null);
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
tg.expand()

let init_data = tg.initData ? tg.initData: "NoInitData"

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
    console.log(d()+":sent:" + r);
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
        window.location.reload(true); //no return from here
        return
    }
    else if (receivedData.type === "tren-data") {
        if ('autoplay' in receivedData) 
            setAutoPlay(receivedData.autoplay, by_ui=false);
        receivedData.card.forEach(cardData => {
            cardSet.addCard(new Card(cardData.cid, cardData.dir, cardData.fw, cardData.nw, cardData.ex, cardData.lnk));
        });
    
        document.querySelector('.txt-counter').textContent =cardSet.cards.length;

        updateCardUI(upFlash, cardSet.getCurrentCard())
        upFlash.style.zIndex = 0;
        
        updateCardUI(downFlash, cardSet.getNextCard())
        downFlash.style.zIndex = -2;

        // Последовательно загружаем аудиофайлы
        for (const card of cardSet.cards) {
            try {
                await card.loadAudio();
                console.log(d()+`:Audio for ${card.foreignW} loaded`);
            } catch (error) {
                console.error(d()+`:Error loading audio for ${card.foreignW}:`, error);
            }
        }            
    }
});

ws.addEventListener('close', () => {
    console.log("close ws");
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
    console.log("invertAutoPlay1 -a");
    setAutoPlay(!isSoundEnabled, by_ui=true);
    console.log("invertAutoPlay1 -b");
}

speakerE.addEventListener('click', invertAutoPlay);
speakerD.addEventListener('click', invertAutoPlay);
