import { authorizedFetch } from "./auth/refresh.js";
import { isAdminOrMod } from "./auth/checkAdminMod.js";
import { isLoggedIn } from "./auth/checkLogin.js";

document.addEventListener("DOMContentLoaded", async () => {
    const games_button_var = document.getElementById("get_all_games");

    const login_button = document.getElementById("login_button");
    const registration_button = document.getElementById("registration_button");
    const my_profile_button = document.getElementById("my_profile_button");

    const create_genres_button = document.getElementById("create_genres");

    if (await isLoggedIn()){
        login_button.style.display = "none";
        registration_button.style.display = "none";
        my_profile_button.style.display = "block";
    }

    if (await isAdminOrMod() === true){
        create_genres_button.style.display = "block";
    }

    games_button_var.addEventListener("click", (e) => {
        e.preventDefault();

        GameButton();
    })
})

function GameButton(){
    localStorage.setItem("page", 1);
    window.location.href = "/all-games";
}