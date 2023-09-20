let tg=window.Telegram.WebApp;
tg.ready()
const socket = new WebSocket('wss://lingolink.bot.nu/tren-wh/');
let chat_id = "484679683";    


function startConn() {
    const dataToSend = {chat_id: chat_id};
    socket.send(JSON.stringify(dataToSend));
}

function sendMessage(msg) {
    const dataToSend = {value: msg};
    socket.send(JSON.stringify(dataToSend));
}

socket.addEventListener('open', () => {
    startConn()
});

let f=document.getElementById("flash");
f.addEventListener("click",()=> {
    sendMessage("click")
    tg.close()
});

