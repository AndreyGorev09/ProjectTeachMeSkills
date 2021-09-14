async function fetchWithTimeout(resource, options = {}) {
    const {timeout = 4000} = options;

    const controller = new AbortController();
    const id = setTimeout(() => controller.abort(), timeout);

    const response = await fetch(resource, {
        ...options,
        headers: {'Content-Type': 'application/json'},
        mode: 'cors',
        signal: controller.signal
    });
    clearTimeout(id);

    return response;
}


async function checkEdgeCases(url) {
    // 1. check method
    let resp = await fetchWithTimeout(url, {method: "GET"});
    let req = `GET ${url}\n\n\n\n\n\n------------\n`;

    if (resp.status !== 405) {
        throw Error(
            req +
            `Сервер должен был вернуть статус 405,` +
            ` а вернул ${resp.status} ${resp.statusText}.` +
            `\nТолько метод POST должен быть разрешён для этой задачи.`
        );
    }

    // 2. check positive range
    let n = 101;
    let body = JSON.stringify(n);
    resp = await fetchWithTimeout(url, {method: "POST", body: body});
    req = `POST ${url}\n\n${body}\n\n\n\n------------\n`;

    if (resp.status !== 422) {
        throw Error(
            req +
            `Сервер должен был вернуть статус 422,` +
            ` а вернул ${resp.status} ${resp.statusText}.` +
            `\nЧисло ${n} должно быть за границей допустимого.`
        );
    }

    // 3. check negative range
    n = -101;
    body = JSON.stringify(n);
    resp = await fetchWithTimeout(url, {method: "POST", body: body});
    req = `POST ${url}\n\n${body}\n\n\n\n------------\n`;

    if (resp.status !== 422) {
        throw Error(
            req +
            `Сервер должен был вернуть статус 422,` +
            ` а вернул ${resp.status} ${resp.statusText}.` +
            `\nЧисло ${n} должно быть за границей допустимого.`
        );
    }

    // 3. check unknown input
    n = Math.floor(Math.random() * 10).toString();
    body = JSON.stringify(n);
    resp = await fetchWithTimeout(url, {method: "POST", body: body});
    req = `POST ${url}\n\n${body}\n\n\n\n------------\n`;

    if (resp.status !== 422) {
        throw Error(
            req +
            `Сервер должен был вернуть статус 422,` +
            ` а вернул ${resp.status} ${resp.statusText}.` +
            `\nВвод ${body} должен восприниматься сервером как неизвестный и неподдерживаемый.`
        );
    }
}


async function checkHappyPath(url) {
    // 1. send 'stop'
    let body = JSON.stringify("stop");
    let resp = await fetchWithTimeout(url, {method: "POST", body: body});
    let req = `POST ${url}\n\n${body}\n\n\n\n------------\n`;

    if (resp.status !== 200) {
        throw Error(
            req +
            `Сервер должен был вернуть статус 200,` +
            ` а вернул ${resp.status} ${resp.statusText}.`
        );
    }

    body = await resp.text();
    let payload = null;
    try {
        payload = JSON.parse(body);
    } catch (e) {
    }

    if ((typeof payload) !== "number") {
        throw Error(
            req +
            `Сервер должен был вернуть число,` +
            ` а вернул ${body}.`
        );
    }

    // 2. send number
    const n = Math.floor(Math.random() * 100);
    body = JSON.stringify(n);
    resp = await fetchWithTimeout(url, {method: "POST", body: body});
    req = `POST ${url}\n\n${body}\n\n\n\n------------\n`;

    if (resp.status !== 200) {
        throw Error(
            req +
            `Сервер должен был вернуть статус 200,` +
            ` а вернул ${resp.status} ${resp.statusText}.`
        );
    }

    body = await resp.text();
    let payload2 = null;
    try {
        payload2 = JSON.parse(body);
    } catch (e) {
    }

    if ((typeof payload2) !== "number") {
        throw Error(
            req +
            `Сервер должен был вернуть число,` +
            ` а вернул ${body}.`
        );
    }
    if (payload2 !== (payload + n)) {
        throw Error(
            req +
            `Сервер должен был вернуть ${payload + n} = ${payload} + ${n},` +
            ` а вернул ${payload2}.`
        );
    }

    // 3. send -number
    body = JSON.stringify(-n);
    resp = await fetchWithTimeout(url, {method: "POST", body: body});
    req = `POST ${url}\n\n${body}\n\n\n\n------------\n`;

    if (resp.status !== 200) {
        throw Error(
            req +
            `Сервер должен был вернуть статус 200,` +
            ` а вернул ${resp.status} ${resp.statusText}.`
        );
    }

    body = await resp.text();
    let payload3 = null;
    try {
        payload3 = JSON.parse(body);
    } catch (e) {
    }

    if ((typeof payload3) !== "number") {
        throw Error(
            req +
            `Сервер должен был вернуть число,` +
            ` а вернул ${body}.`
        );
    }
    if (payload3 !== payload) {
        throw Error(
            req +
            `Сервер должен был вернуть ${payload} = ${payload} + ${-n} + ${n},` +
            ` а вернул ${payload3}.`
        );
    }
}


async function check(service) {
    let path = "/task4/";
    let scheme = "http://";

    if (service.endsWith("/")) {
        path = path.substr(1);
    }
    if (service.startsWith("http://") || service.startsWith("https://")) {
        scheme = "";
    }

    let url = `${scheme}${service}${path}`;

    let result = {
        ok: true,
        description: null,
        ms: performance.now(),
    }

    try {
        await checkEdgeCases(url);
        await checkHappyPath(url);
    } catch (e) {
        result = {
            ...result,
            ok: false,
            description: e.message,
        }
    }

    result.ms = Math.floor(performance.now() - result.ms);
    return result;
}


async function saveCheckResult(name, service, result) {
    const path = '/task4/check/';
    const payload = {
        description: result.description || null,
        ms: result.ms,
        name: name,
        ok: result.ok,
        service: service,
    }

    const resp = await fetchWithTimeout(
        path, {
            method: "POST",
            body: JSON.stringify(payload),
        });
    const resp2 = resp.clone();

    try {
        const checkObj = await resp.json();
        console.debug(`${resp.status} ${resp.statusText}\n${JSON.stringify(checkObj)}`);
    } catch (e) {
        const body = await resp2.text();
        console.debug(`${resp2.status} ${resp2.statusText}\n${body}\n`);
    }

}


async function loadUserData() {
    return {
        name: localStorage.getItem("task4/name") || "",
        service: localStorage.getItem("task4/service") || "",
    }
}


async function storeUserData(service, name) {
    localStorage.setItem("task4/name", name);
    localStorage.setItem("task4/service", service);
}


async function setUp() {
    let inputName = document.getElementById("id_name");
    let inputService = document.getElementById("id_service");
    let btnCheck = document.getElementById("id_check");
    let sectionResults = document.getElementById("id_results");
    let spanOk = document.getElementById("id_ok");
    let spanDescription = document.getElementById("id_description");
    let spanTiming = document.getElementById("id_timing");

    const userData = await loadUserData();
    inputName.value = userData.name;
    inputService.value = userData.service;

    const checkEventHandler = async function (event) {
        sectionResults.hidden = true;

        const name = inputName.value;
        const service = inputService.value;

        if (!name.length) {
            alert("Необходимо представиться!");
            inputName.focus();
            return;
        }
        if (!service.length) {
            alert("Необходимо указать УРЛ или хост сервиса!");
            inputService.focus();
            return;
        }

        await storeUserData(service, name);

        const result = await check(service);
        await saveCheckResult(name, service, result);

        if (result.ok) {
            spanOk.textContent = "всё работает";
            spanOk.style.color = "green";
            spanDescription.parentElement.hidden = true;
        } else {
            spanOk.textContent = "есть проблемы";
            spanOk.style.color = "red";
            spanDescription.textContent = result.description;
            spanDescription.parentElement.hidden = false;
        }

        spanTiming.textContent = result.ms.toFixed(0).toString();

        sectionResults.hidden = false;
    };

    const checkEventHandlerOnEnter = async function (event) {
        if (event.code === "Enter") {
            event.preventDefault();
            return await checkEventHandler(event);
        }
    };

    btnCheck.addEventListener("click", checkEventHandler);
    inputName.addEventListener("keyup", checkEventHandlerOnEnter);
    inputService.addEventListener("keyup", checkEventHandlerOnEnter);
}


document.addEventListener("DOMContentLoaded", setUp);