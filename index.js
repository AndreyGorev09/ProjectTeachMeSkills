const TASK_3_URL = '/task/3';
const TASK_4_URL = '/task/4';
const TG_WH_URL = '/tg/webhook';


async function api_call(url, params) {
    let headers = params.headers || new Headers();
    headers.set("Content-Type", "application/json");
    const resp = await fetch(
        url, {
            body: JSON.stringify(params.json),
            headers: headers,
            method: params.method || "POST",
        });

    if (resp.status !== 200) {
        return null;
    }

    return await resp.json();
}


async function getNumber() {
    const payload = await api_call(TASK_4_URL, {json: 'stop'});
    return payload.data.n;
}


async function addNumber(number) {
    const payload = await api_call(TASK_4_URL, {json: number});
    return payload.data.n;
}


async function greet(name) {
    const payload = await api_call(TASK_3_URL, {json: name});
    return payload.data.greeting;
}


async function getWebhook() {
    return await api_call(TG_WH_URL, {method: "GET"});
}


async function setWebhook(url, token) {
    let headers = new Headers();
    headers.append("AUTHORIZATION", token);
    const payload = await api_call(TG_WH_URL, {json: {url: url}, headers: headers});
    return payload.webhook;
}


async function setUpTask3() {
    let input = document.querySelector("#task3 input");
    let span = document.querySelector("#task3 span");

    input.addEventListener("input", async function (event) {
        const name = input.value;
        const greeting = await greet(name);
        span.textContent = greeting;
    });
}


async function setUpTask4() {
    let button = document.querySelector("#task4 button");
    let follow = document.getElementById("id_task_4_cb");
    let input = document.getElementById("id_task_4_input");
    let label = document.querySelector("#task4 label");

    const ping = async function () {
        const number = await getNumber();
        label.textContent = `Накопление: ${number}`;
    }

    await ping();

    follow.addEventListener("click", async function (event) {
        if (follow.checked) {
            follow.interval = setInterval(ping, 5000);
        } else {
            if (follow.interval) {
                follow.interval.clearInterval();
            }
        }
    });

    button.addEventListener("click", async function (event) {
        const value = Number.parseInt(input.value || '0');
        input.value = 0;
        await addNumber(value);
        await ping();
    });
}


async function setUpTg() {
    let inputWebhook = document.querySelector("#id_webhook");
    let labelWebhook = document.querySelector("#tg label[for=id_webhook]");
    let inputToken = document.querySelector("#id_token");
    let button = document.querySelector("#tg button");

    const setLabel = (wh) => {
        labelWebhook.textContent = `Вебхук: ${wh.url}`;
    }

    const wh = await getWebhook();
    setLabel(wh);

    button.addEventListener("click", async function (event) {
        const wh = await setWebhook(inputWebhook.value, inputToken.value);
        inputWebhook.value = inputToken.value = "";
        setLabel(wh);
    });
}


async function setUp() {
    await setUpTask3();
    await setUpTask4();
    await setUpTg();
}


document.addEventListener("DOMContentLoaded", setUp);