import { authorizedFetch } from "../auth/refresh.js";
import { getCookie } from "../auth/getCookie.js";

let gameId = 0;
let devId = 0;
let grId = 0;

const path = window.location.pathname.split("/");
console.log(path);
console.log(path[0]);
console.log(path[3]);

if (path[1] === "game-report-page"){
    gameId = path[2];
    console.log(gameId);
}
else if (path[1] === "developers"){
    devId = path[2];
    gameId = path[4];
    console.log(gameId);
}
else if (path[1] === "developer"){
    devId = path[2];
    gameId = path[4];
    console.log(gameId);
}
else if (path[1] === "genres"){
    grId = path[2];
    gameId = path[4];
    console.log(gameId);
}

document.addEventListener("DOMContentLoaded", () => {
    const yes_button = document.getElementById("yes");

    yes_button.addEventListener("click", (e) => {
        e.preventDefault()

        yes_function();
    })

    const back_button = document.getElementById("back");
    back_button.addEventListener("click", (e) => {
        e.preventDefault();

        if (path[1] === "game-report-page"){
            window.location.href = `/game-page/${gameId}`;
        }
        else if (path[1] === "developers"){
            window.location.href = `/developers/${devId}/game-page/${gameId}`;
        }
        else if (path[1] === "developer"){
            window.location.href = `/developer/${devId}/game-page/${gameId}`
        }
        else if (path[1] === "genres"){
            window.location.href = `/genres/${grId}/game-page/${gameId}`
        }
    })
})

async function yes_function(){
    const message = document.getElementById("message");

    const response = await authorizedFetch(`/games/${gameId}/report`, {
        method: "POST",
        headers: {
            "X-CSRF-TOKEN": getCookie("csrf_access_token")
        }
    });

    const data = await response.json();

    if (response.ok){
        message.innerText = "Game reported";
        const no_button = document.getElementById("back");

        no_button.innerText = "Back";

    }
    else{
        message.innerText = JSON.stringify(data);
    }
}