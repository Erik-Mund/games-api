import { authorizedFetch } from "../refresh.js"

async function loadProfile() {
    const token = localStorage.getItem("access_token");
    const profile = document.getElementById("profile");

    if (!token){
        profile.innerText = "Not logged in";
        return;
    }

    const response = await authorizedFetch("/me");
    console.log("loading profile");

    const data = await response.json();

    const update_button = document.getElementById("update_button")
    const delete_button = document.getElementById("delete_button")

    if (response.ok) {
        console.log(data);
        profile.innerText = `
            ID: ${data.id}
            Name: ${data.name}
            Email: ${data.email}
            Role: ${data.role}
        `;

        update_button.style.display = "block";
        delete_button.style.display = "block";
    } else {
        console.log("Unauthorized");
        profile.innerText = "Unauthorized";
    }
}

window.onload = function () {
    loadProfile();
};