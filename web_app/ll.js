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
cardSet.addCard(new Card(1, 1, 0, "0 front curtain", "занавес", "In the middle of the scene, the front curtain unexpectedly started to lower, catching the actors off-guard.", "reconvene"));
cardSet.addCard(new Card(3, 2, 0, "1 reconvene", "вновь собраться", "After a short break, the meeting will reconvene at 2:00 PM in the boardroom.", "reconvene"));
cardSet.addCard(new Card(2, 1, 1, "2 front curtain", "занавес", "In the middle of the scene, the front curtain unexpectedly started to lower, catching the actors off-guard.", "reconvene"));
cardSet.addCard(new Card(4, 2, 1, "3 reconvene", "вновь собраться", "After a short break, the meeting will reconvene at 2:00 PM in the boardroom.", "reconvene"));

var container = document.getElementById('container');
var maxMidth=container.offsetWidth
var flash0 = document.getElementById('flash0');
var flash1 = document.getElementById('flash1');
var upFlash=flash0
var downFlash=flash1

function updateCardUI(fl, card) {
    if (card) {
        fl.querySelector(".f-text").textContent = card.foreignW;
        fl.querySelector(".s-text").textContent = card.nativeW;
        fl.querySelector(".t-text").textContent = card.example;
        fl.style.display='flex'
    }
    else
        fl.style.display = "none";
}

updateCardUI(upFlash, cardSet.getCurrentCard())
upFlash.style.zIndex = 0;

updateCardUI(downFlash, cardSet.getNextCard())
downFlash.style.zIndex = -2;

var BREAK_POINT = maxMidth / 4;
var mc = new Hammer.Manager(container);
mc.add(new Hammer.Pan({
    direction: Hammer.DIRECTION_ALL,
    threshold: 5,
    pointers: 0
}));

mc.add(new Hammer.Tap());
mc.on("tap", function (ev) {
    console.log('tap');
    gsap.to(upFlash, 0.2, {ease: Cubic.easeInOut, scaleX: 0.0, repeat:1, yoyo: true});
});

mc.on("panleft panright panup", function (ev) {
    rot=25*ev.deltaX/(maxMidth/2);
    gsap.set(upFlash, {x: ev.deltaX, y: ev.deltaY, rotation: rot});
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
}

mc.on("panend pancancel", endPan);


//let tg=window.Telegram.WebApp;
//tg.expand()
//tg.ready()
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

