import { authorizedFetch } from "../auth/refresh.js";
import { getCookie } from "../auth/getCookie.js";


const gameId = window.location.pathname.split("/").pop();

document.addEventListener("DOMContentLoaded", async () => {
    const form = document.getElementById("delete_game_form");
    const message = document.getElementById("message");

    form.addEventListener("submit", async (e) =>{
        e.preventDefault();

        const response = await authorizedFetch(`/games/${gameId}`, {
            method: "DELETE",
            headers: {
                "X-CSRF-TOKEN":getCookie("csrf_access_token")
            }
        })

        if (response.ok){
            message.innerText = "deletion successful";
           setTimeout(() => {
                window.location.href='/my-games'
           }, 900);
        }
        else{
            message.innerText = "deletion failed";
        }
    })
})