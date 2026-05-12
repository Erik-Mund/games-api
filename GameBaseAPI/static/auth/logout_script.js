import  { getCookie } from "./getCookie.js";
import { authorizedFetch } from "./refresh.js";

async function loadLogout() {

    const message = document.getElementById("message");

    const response = await authorizedFetch("/logout", {
        method: "POST",
        headers: {
            "X-CSRF-TOKEN": getCookie("csrf_access_token")
        }
    });

    const refresh_response = await fetch("/logout/refresh", {
        method: "POST",
        headers: {
            "X-CSRF-TOKEN": getCookie("csrf_refresh_token")
        },
        credentials: "include"
    });

    if (response.ok && refresh_response.ok){
        message.innerText = "Logged out successfully";
        setTimeout(() => {
            window.location.href = "/";
            }, 900);
    }
    else {
        message.innerText = "not logged in";
    }

}

document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("logout_button").addEventListener("click", loadLogout);
})