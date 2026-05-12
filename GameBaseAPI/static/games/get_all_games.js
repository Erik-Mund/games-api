import { isAdminOrMod, isModerator, isAdmin } from "../auth/checkAdminMod.js";
import {authorizedFetch} from "../auth/refresh.js";
import { getCookie } from "../auth/getCookie.js";

const sorting = document.getElementById("sort")

let per_page = 20;

let isAdminOrModBool = false;
let isAdminBool = false;

let page = 1;
let max_pages = 0;

let games_count = 0;


const games_div = document.getElementById("games");
const endpoint = games_div.dataset.endpoint;
const page_input = document.getElementById("page_input");
const go_button = document.getElementById("go");

document.getElementById("loading").style.display = "block";


function getPage(){
    const page_raw = localStorage.getItem("page");

    if(page_raw !== null){
        page = parseInt(page_raw);
    }

    return page;
}
function get_max_page(){
    if (!games_count || games_count < 0) return 1;
    max_pages = Math.ceil(games_count / per_page);
    return max_pages;
}

async function get_games(){
    document.getElementById("loading").style.display = "block";
    document.getElementById("games").style.display = "none";

    per_page = document.getElementById("per_page").value;
    const params = new URLSearchParams({
            sort: sorting.value,
            per_page: per_page,
            page: getPage()
    })

        let finalEndpoint = endpoint
        const devId = parseInt(localStorage.getItem("developer_to_load"));
        const grId = parseInt(localStorage.getItem("genre_to_load"));

        if (endpoint === "/developers/games"){

            if (!devId){
                console.error("NO developer id found");
                games_div.innerText = "there is no such developer";
                return;
            }

            finalEndpoint = `/developers/${devId}/games`;
            console.log(finalEndpoint);
        }
        else if (endpoint === "/me/games"){
            if (!devId){
                console.error("NO developer id found");
                games_div.innerText = "there is no such developer";
                return;
            }

            finalEndpoint = `/developers/${devId}/games`;
            console.log(finalEndpoint);
        }
        else if (endpoint === "/genres/games"){
            if (!grId){
                console.error("NO genre id found");
                games_div.innerText = "there is no such genre";
                return;
            }

            finalEndpoint = `/genres/${grId}/games`;
            console.log(finalEndpoint);
        }

        console.log(finalEndpoint)
        console.log(localStorage.getItem("genre_to_load"));

        const response = await fetch(`${finalEndpoint}?${params.toString()}`)

        const data = await response.json()
        console.log(data);

        if (response.ok){
            games_div.innerHTML = "";

            games_count = data.total_count;

            if (await isAdminOrMod()){
                isAdminOrModBool = true;
            }
            if (await isAdmin()){
                isAdminBool = true;
            }

            if (getPage() <= get_max_page()){
                data.games.forEach(game => {
                    const div = document.createElement("div");

                    const info = document.createElement("span");
                    const right = document.createElement("div");
                    right.style.display = "flex";
                    right.style.alignItems = "center";
                    right.style.gap = "10px";

                    if (game.average_rating === 0){
                        info.innerText = `${game.title} - ${game.platform} - ${game.price}$ - no reviews yet   `;
                    }
                    else{
                        const rating = Math.round(game.average_rating * 10) / 10;
                        info.innerText = `${game.title} - ${game.platform} - ${game.price}$ - ${rating}/5   `;
                    }

                    const button = document.createElement("button");
                    button.innerText = "View";

                    button.onclick = () => {
                        console.log(finalEndpoint)
                        if (endpoint === `/games`){
                            window.location.href = `/game-page/${game.id}`;
                        }
                        else if (endpoint === "/developers/games"){
                            window.location.href = `/developers/${devId}/game-page/${game.id}`;
                        }
                        else if (endpoint === "/me/games"){
                            window.location.href = `/developer/${devId}/game-page/${game.id}`;
                        }
                        else if (endpoint === "/genres/games"){
                            window.location.href = `/genres/${grId}/game-page/${game.id}`;
                        }
                    };

                    if (isAdminOrModBool && endpoint !== "/me/games"){
                        const report_count_text = document.createElement("span");
                        report_count_text.innerText = `Reports: ${game.report_count}`;
                        report_count_text.style.marginLeft = "10px";
                        const update_button = document.createElement("button");
                        update_button.innerText = "Update game";
                        update_button.style.marginLeft = "10px";
                        update_button.style.display = "none";

                        update_button.addEventListener("click", (e) => {
                                e.preventDefault();

                                console.log("clicked");
                                if (endpoint === "/developers/games"){
                                    window.location.href = `/developers/${devId}/update-game/${game.id}`;
                                }
                                else if (endpoint === "/me/games"){
                                    window.location.href = `/developer/${devId}/update-game/${game.id}`;
                                }
                                else if (endpoint === "/genres/games"){
                                    window.location.href = `/genres/${grId}/update-game/${game.id}`;
                                }
                                else{
                                    window.location.href = `/all-games/update-game/${game.id}`;
                                }
                            })
                        if (isAdminBool){
                            update_button.style.display = "block";

                        }
                        const delete_button = document.createElement("button");
                        delete_button.innerText = "Delete game";
                        delete_button.style.marginLeft = "10px";
                        const confirm_button = document.createElement("button");
                        confirm_button.innerText = "Confirm deletion";
                        confirm_button.style.display = "none";
                        const delete_message = document.createElement("div");
                        delete_button.onclick = () => {
                            confirm_button.style.display = "block";

                            right.appendChild(confirm_button);

                            confirm_button.addEventListener("click", async (e) => {
                                e.preventDefault();
                                const delete_response = await authorizedFetch(`/games/${game.id}`, {
                                    method: "DELETE",
                                    headers: {
                                        "X-CSRF-TOKEN": getCookie("csrf_access_token")
                                    }
                                })
                                const delete_status = delete_response.status;
                                if (delete_status === 204){
                                    delete_message.innerText = "deleted successfully";
                                    setTimeout(() => {
                                        div.remove();
                                    }, 500);
                                }
                                else if (delete_status === 403){
                                    if (await isModerator()){
                                        delete_message.innerText = "game isn't reported enough times";
                                    }
                                    else{
                                        delete_message.innerText = "FORBIDDEN";
                                    }
                                }
                                else{
                                    delete_message.innerText = `error ${delete_status}`;
                                }
                            })
                            };
                        right.style.marginLeft = "10px";
                        right.appendChild(update_button);
                        right.appendChild(delete_button);
                        right.appendChild(report_count_text);
                        right.appendChild(delete_message);

                    }

                    button.style.marginLeft = "10px";

                    div.appendChild(info);
                    div.appendChild(button);

                    div.appendChild(right);

                    div.style.fontSize = "20px";
                    div.style.marginBottom = "10px";

                    games_div.appendChild(div);
                })
            }
            else{
                games_div.innerText = `Max page: ${get_max_page()}`;
            }
        }
        else{
            games_div.innerText = JSON.stringify(data);
        }

    document.getElementById("games").style.display = "block";
    document.getElementById("loading").style.display = "none";
}


window.onload = function () {
    get_games();
    page_input.value = getPage();
};

sorting.addEventListener("change", () => {
    get_games();
})

go_button.addEventListener("click", () => {
    changePage();
})

function changePage(){
    const input_page = parseInt(page_input.value);
    if (isNaN(input_page)) {
        document.getElementById("page_message");
        return;
    }

    if (!isNaN(input_page)){
        if (input_page >= 1){
            document.getElementById("page_message").innerText = "";
            localStorage.setItem("page", page_input.value)
            get_games();
            page_input.value = getPage();
        }
        else{
            document.getElementById("page_message").innerText = "invalid input";
        }
    }
    else{
        if (input_page > 1){
            document.getElementById("page_message").innerText = `max page: ${get_max_page()}`;
        }
        else{
            document.getElementById("page_message").innerText = "invalid input";
        }
    }
}

