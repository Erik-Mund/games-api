import { isLoggedIn } from "./checkLogin.js";

const form = document.getElementById("registration-form");
const message = document.getElementById("message")

form.addEventListener("submit", async function (e) {
    e.preventDefault();

    const email = document.getElementById("email").value;
    const name = document.getElementById("name").value;
    const password = document.getElementById("password").value;

    if (await isLoggedIn()) {
        message.innerText = "You already have an account";
        return;
    }

    const response = await fetch("/register", {
        method:"POST", headers:{
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                email: email,
                name: name,
                password: password
            })

        });

    const data = await response.json();

    if(response.ok){
        message.innerText = "registration successful";
        setTimeout(() => {
            window.location.href = "/login";}, 900);
    }
    else{
        if(data.error) {
            message.innerText = data.error;
        }
        else if (data.errors){
            const errors = data.errors.json;

            const firstKey = Object.keys(errors)[0];
            message.innerText = errors[firstKey][0];
        }
        else{
            message.innerText = "Too many attempts";
        }

    }
})