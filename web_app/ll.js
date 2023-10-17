class Card {
    constructor(cid, direction, foreignW, nativeW, example) {
        this.cid = cid;
        this.direction = direction;
        this.foreignW = foreignW;
        this.nativeW = nativeW;
        this.example = example;
        this.answer = -1;  // not showed card
    }
    //вернет слово для изучения
    getA(){
        if (this.direction==0)
            return this.foreignW;
        else
            return this.nativeW;
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

function playAudio(audioSrc) {
    let s_link="/au/en/";
    let c=cardSet.getCurrentCard();
    if (c) {
        if (audioSrc == "fw") {
            s_link+="w/"+c.foreignW+".ogg";
            const audio = new Audio(s_link);
            audio.play();
            console.log("F:"+s_link);
        }
        else if  (audioSrc == "ex")
            getHash(c.example).then(hash => {
                console.log(hash + ":"+ c.example);
                s_link+="e/"+hash+".ogg?uid="+user_id+"&cid="+c.cid;
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
        gsap.to(upFlash, {duration: 0.7, rotationY:180, ease:Back.easeOut});
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

let user_id = tg.initDataUnsafe.user ? tg.initDataUnsafe.user.id : 484679683; //fixme - if no tg, close app
console.log("user_id:" + user_id);
let protocol = window.location.protocol == 'https:' ? 'wss:' : 'ws:';
let addr=protocol + '//' + window.location.host + '/tren-wh/';
console.log("WS addr:" + addr);
const ws = new WebSocket(addr);

tg.ready()

function startConn() {
    console.log("connected");
    const dataToSend = {
         user_id: user_id,
         type: "start-tren" 
        };
    
    let r=JSON.stringify(dataToSend)
    ws.send(r);
    console.log("sent:" + r);
}

ws.addEventListener('open', () => {
  startConn()
});

ws.addEventListener('close', () => {
    console.log("close ws");
    tg.close()
});

ws.addEventListener('message', (event) => {
    const receivedData = JSON.parse(event.data);
    console.log("Rx data:", receivedData);

    if (receivedData.type === "tren-data") {
        receivedData.card.forEach(cardData => {
            cardSet.addCard(new Card(cardData.cid, cardData.dir, cardData.fw, cardData.nw, cardData.ex));
        });
    }
    
    document.querySelector('.txt-counter').textContent =cardSet.cards.length;

    updateCardUI(upFlash, cardSet.getCurrentCard())
    upFlash.style.zIndex = 0;
    
    updateCardUI(downFlash, cardSet.getNextCard())
    downFlash.style.zIndex = -2;
});
