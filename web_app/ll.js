class Card {
    constructor(cardId, wordId, direction, foreignW, nativeW, example, dictLnk) {
        this.cardId = cardId;
        this.wordId = wordId;
        this.direction = direction;
        this.foreignW = foreignW;
        this.nativeW = nativeW;
        this.example = example;
        this.dictLnk = dictLnk;
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
    
        } else if (val == 0) {
            let card = this.cards.splice(this.currentCardIndex, 1)[0];
            this.cards.push(card);
        }
    }
}

// Создание тестового CardSet
let cardSet = new CardSet();
cardSet.addCard(new Card(1, 1, 0, "front curtain", "занавес", "ex", "reconvene"));
cardSet.addCard(new Card(3, 2, 0, "reconvene", "вновь собраться", "After a short break, the meeting will reconvene at 2:00 PM in the boardroom.", "reconvene"));
cardSet.addCard(new Card(2, 1, 1, "front curtain", "занавес", "In the middle of the scene, the front curtain unexpectedly started to lower, catching the actors off-guard.", "reconvene"));
cardSet.addCard(new Card(4, 2, 1, "reconvene", "вновь собраться", "After a short break, the meeting will reconvene at 2:00 PM in the boardroom.", "reconvene"));

var container = document.getElementById('container');
var maxMidth=container.offsetWidth;
var flash0 = document.getElementById('flash0');

var flash1 = flash0.cloneNode(true);
flash1.id = 'flash1';
flash1.style.zIndex = -1;
flash0.parentNode.insertBefore(flash1, flash0.nextSibling); // Вставляем новый элемент сразу после оригинала
var upFlash=flash0;
var downFlash=flash1;
var ss='q';



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


updateCardUI(upFlash, cardSet.getCurrentCard())
upFlash.style.zIndex = 0;

updateCardUI(downFlash, cardSet.getNextCard())
downFlash.style.zIndex = -2;

var BREAK_POINT = maxMidth / 6;
var mc = new Hammer.Manager(container);
mc.add(new Hammer.Pan({
    direction: Hammer.DIRECTION_ALL,
    threshold: 5,
    pointers: 0
}));




mc.add(new Hammer.Tap());
mc.on("tap", function (ev) {
    ss=(ss=='q')?'a':'q';
    if (ss=='a')
        gsap.to(upFlash, {duration: 0.7, rotationY:180, ease:Back.easeOut});
    else
        gsap.to(upFlash, {duration: 0.7, rotationY:0, ease:Back.easeOut});
});

mc.on("panleft panright panup", function (ev) {
    let rot=-48.0*ev.deltaX/maxMidth;
    let op=Math.min(Math.abs(4.0*ev.deltaX)/maxMidth, 1.0);
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
        gsap.to(upFlash, 0.3, { 
            ease: Cubic.easeInOut, 
            x: ev.deltaX>0 ? '120%' : '-120%', 
            onCompleteParams: [upFlash],
            onComplete: function(v) {
                v.style.zIndex -= 2;
                cardSet.setAnswer(ev.deltaX>0 ? 1 : 0 );
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
                }
                gsap.set(v, {x: '0%', y: '0%', rotation: 0});
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
tg.ready()
//const socket = new WebSocket('wss://lingolink.bot.nu/tren-wh/');
//let chat_id = "484679683";    


function startConn() {
    const dataToSend = { chat_id: chat_id };
    //socket.send(JSON.stringify(dataToSend));
}

function sendMessage(msg) {
    const dataToSend = { value: msg };
    //socket.send(JSON.stringify(dataToSend));
}

//socket.addEventListener('open', () => {
//  startConn()
//});

let f = document.getElementById("flash0");
f.addEventListener("click", () => {
    //sendMessage("click")
    //tg.close()
});

