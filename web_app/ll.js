let tg=window.Telegram.WebApp;
tg.ready()
let f=document.getElementById("flash");

f.addEventListener("click",()=> {
    let chat_id = tg?.initDataUnsafe?.user?.id || "484679683";    
    const dataToSend = {
        value: 'click',
        //query_id: tg.initDataUnsafe.query_id, 
        chat_id: chat_id
    };
    // Отправить данные на сервер
    //fetch("https://ll.du:8000/tren", { 
    fetch("https://lingolink.bot.nu/tren-wh/", { 
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(dataToSend)
    })
    .then(response => console.log(response)) // Вывести результат в консоль
    .catch(error => console.error('Error:', error)); // Обработка ошибок
    tg.close()
});

