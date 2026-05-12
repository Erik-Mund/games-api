import { authorizedFetch } from "../auth/refresh.js";
import { getCookie } from "../auth/getCookie.js";

document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("dev-form");
    const message = document.getElementById("message");
    const studio_name_field = document.getElementById("studio_name");

    form.addEventListener("submit", async function (e){
        e.preventDefault();

        const data = {};
        if (studio_name_field) data.studio_name = studio_name_field.value;

        const response = await authorizedFetch('/developers', {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRF-TOKEN": getCookie("csrf_access_token")
            },
            body: JSON.stringify(data)
        })

        const result = await response.json();

        if (response.ok) {
            message.innerText = "Developer profile created";
            setTimeout(() => {
                window.location.href = "/developer-profile-page";}, 900);
        }
        else{
            message.innerText = JSON.stringify(result);
        }
    })
})