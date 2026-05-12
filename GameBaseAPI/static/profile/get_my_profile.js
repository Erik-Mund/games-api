import { authorizedFetch } from "../auth/refresh.js"

const loading = document.getElementById("loading");

async function loadProfile() {
    const profile = document.getElementById("profile");

    const response = await authorizedFetch("/me");
    console.log("loading profile");

    const data = await response.json();

    const logout_button = document.getElementById("logout_button");
    const update_button = document.getElementById("update_button");
    const delete_button = document.getElementById("delete_button");

    if (response.ok) {
        profile.innerText = `
            Name: ${data.name}
            Email: ${data.email}
            Role: ${data.role}
        `;

        logout_button.style.display = "block";
        update_button.style.display = "block";
        delete_button.style.display = "block";
    } else {
        console.log("Unauthorized");
        profile.innerText = "Unauthorized";
    }

    loading.style.display = "none";
}

document.addEventListener("DOMContentLoaded", async () => {
    loadProfile();
})