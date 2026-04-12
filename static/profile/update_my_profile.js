import { authorizedFetch } from "../refresh.js"

document.addEventListener("DOMContentLoaded", () => {
    console.log("JS loaded");

    const form = document.getElementById("update_user_info");
    const message = document.getElementById("message");

    form.addEventListener("submit", async function (e){
        e.preventDefault();

        const data = {};

        const old_password = document.getElementById("old_password").value;
        const password = document.getElementById("password").value;
        const name = document.getElementById("name").value.trim();

        if(name) data.name = name;
        if(old_password) data.old_password = old_password;
        if(password) data.password = password;

        const response = await authorizedFetch("/me", {
            method: "PUT",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
    });

    const result = await response.json()

    if(response.ok){
        message.innerText = "Profile updated";
    }
    else{
        message.innerText = result?.error;
    }
});
})


