import { authorizedFetch } from "../auth/refresh.js";
import { getCookie } from "../auth/getCookie.js";

document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("genre-form");
    const message = document.getElementById("message");
    const name_field = document.getElementById("name");

    form.addEventListener("submit", async function (e){
        e.preventDefault();

        const data = {};
        if (name_field) data.name = name_field.value;

        const response = await authorizedFetch('/genres', {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRF-TOKEN": getCookie("csrf_access_token")
            },
            body: JSON.stringify(data)
        })

        const result = await response.json();

        if (response.ok) {
            message.innerText = "Genre created";
        }
        else{
            message.innerText = JSON.stringify(result);
        }
    })
})