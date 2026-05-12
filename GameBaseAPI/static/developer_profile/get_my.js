import { authorizedFetch } from "../auth/refresh.js";

const see_games = document.getElementById("see_games");
let devId = 0;

see_games.addEventListener("click", (e) => {
    e.preventDefault();

    localStorage.setItem("developer_to_load", devId);
})

async function loadDeveloperProfile(){
    const profile_div = document.getElementById("developer_profile");
    const create_button = document.getElementById("create_button");
    const create_game_button = document.getElementById("create_game");
    const update_button = document.getElementById("update_button");
    const delete_button = document.getElementById("delete_button");

    const response = await authorizedFetch('/developers/get-my');

    const data = await response.json()

    if (response.status === 401){
        profile_div.innerText = "Unauthorized";
    }
    else if (response.status === 404){
        create_button.style.display = "block";
        profile_div.innerText = "You have no developer profile";
    }
    else if (response.status === 200){
        profile_div.innerText = `
            Studio_name: ${data.studio_name}
        `;
        devId = data.id;

        see_games.style.display = "block";
        create_game_button.style.display = "block";
        update_button.style.display = "block";
        delete_button.style.display = "block";
    }
    else{
        profile_div.innerText = "Unknown error";
    }

}

document.addEventListener("DOMContentLoaded", () => {
    loadDeveloperProfile();
})