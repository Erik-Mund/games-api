import { isAdminOrMod, isModerator } from "../auth/checkAdminMod.js";
import {authorizedFetch} from "../auth/refresh.js";
import { getCookie } from "../auth/getCookie.js";

const sorting = document.getElementById("sort")

let per_page = 20;

let page = 1;
let max_pages = 0;

let isAdminOrModBool = false;

let genres_count = 0;

const genres_div = document.getElementById("genres");
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
    if (!genres_count || genres_count < 0) return 1;
    max_pages = Math.ceil(genres_count / per_page);
    return max_pages;
}

async function get_genres(){
    document.getElementById("loading").style.display = "block";
    document.getElementById("genres").style.display = "none";
    per_page = document.getElementById("per_page").value;
    const params = new URLSearchParams({
            sort: sorting.value,
            per_page: per_page,
            page: getPage()
    })

        const response = await fetch(`/genres?${params.toString()}`)

        const data = await response.json()
        console.log(data);

        if (response.ok){
            if (await isAdminOrMod()){
                isAdminOrModBool = true;
            }

            genres_div.innerHTML = "";

            genres_count = data.total_count;

            if (getPage() <= get_max_page()){
                data.genres.forEach(genre => {
                    const div = document.createElement("div");

                    const info = document.createElement("span");
                    info.innerText = `${genre.name}`;

                    const left = document.createElement("div");
                    left.appendChild(info);

                    const right = document.createElement("div");
                    right.style.display = "flex";
                    right.style.alignItems = "center";
                    right.style.gap = "10px";

                    div.style.display = "flex";
                    div.style.alignItems = "center";

                    if (genre.game_count >= 1){
                        const button = document.createElement("button");
                        button.innerText = "See games";
                        button.onclick = () => {
                            localStorage.setItem("genre_to_load", genre.id);
                            window.location.href = "/genres-games";
                            };
                        right.style.marginLeft = "10px";
                        right.appendChild(button);
                    }
                    if (isAdminOrModBool){
                        const game_count_text = document.createElement("span");
                        game_count_text.innerText = `Games: ${genre.game_count}`;
                        const delete_button = document.createElement("button");
                        delete_button.innerText = "Delete genre";
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
                                const delete_response = await authorizedFetch(`/genres/${genre.id}`, {
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
                                        delete_message.innerText = "genre has too many games";
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
                        right.appendChild(delete_button);
                        right.appendChild(game_count_text);
                        right.appendChild(delete_message);

                    }



                    div.appendChild(left);
                    div.appendChild(right);


                    div.style.fontSize = "20px";
                    div.style.marginBottom = "10px";

                    genres_div.appendChild(div);
                })
            }
            else{
                genres_div.innerText = `Max page: ${get_max_page()}`;
            }
        }
        else{
            genres_div.innerText = JSON.stringify(data);
        }

    document.getElementById("genres").style.display = "block";
    document.getElementById("loading").style.display = "none";
}


window.onload = function () {
    get_genres();
    page_input.value = getPage();
};

sorting.addEventListener("change", () => {
    get_genres();
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
            get_genres();
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

