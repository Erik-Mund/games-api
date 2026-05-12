import {authorizedFetch} from "../auth/refresh.js";
import {getCookie} from "../auth/getCookie.js";
import {isAdmin} from "../auth/checkAdminMod.js";

const sorting = document.getElementById("sort")

let per_page = 20;
let isAdminBool = false;

let page = 1;
let max_pages = 0;

let developers_count = 0;

const developers_div = document.getElementById("developers");
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
    if (!developers_count || developers_count < 0) return 1;
    max_pages = Math.ceil(developers_count / per_page);
    return max_pages;
}

async function get_developers(){
    document.getElementById("loading").style.display = "block";
    document.getElementById("developers").style.display = "none";

    per_page = document.getElementById("per_page").value;
    const params = new URLSearchParams({
            sort: sorting.value,
            per_page: per_page,
            page: getPage()
    })

        const response = await fetch(`/developers?${params.toString()}`)

        const data = await response.json()
        console.log(data);

        if (response.ok){
            developers_div.innerHTML = "";

            isAdminBool = await isAdmin();

            developers_count = data.total_count;

            if (getPage() <= get_max_page()){
                data.developers.forEach(developer => {
                    const div = document.createElement("div");

                    const info = document.createElement("span");
                    info.innerText = `${developer.studio_name}`;

                    const left = document.createElement("div");
                    left.appendChild(info);

                    const right = document.createElement("div");

                    div.style.display = "flex";
                    div.style.alignItems = "center";

                    if (developer.games_count >= 1){
                        const button = document.createElement("button");
                        button.innerText = "See games";
                        button.onclick = () => {
                            localStorage.setItem("developer_to_load", developer.id);
                            window.location.href = "/developer-games";
                            };
                        right.style.marginLeft = "10px";
                        right.appendChild(button);
                    }

                    if (isAdminBool){
                        const update_button = document.createElement("button");
                        update_button.innerText = "Update developer";
                        update_button.style.marginLeft = "10px";
                        update_button.style.display = "none";

                        update_button.addEventListener("click", (e) => {
                                e.preventDefault();

                                console.log("clicked");
                                window.location.href = `/developers/update-developer-profile-page/${developer.id}`;
                            })
                            update_button.style.display = "block";
                            const delete_button = document.createElement("button");
                            delete_button.innerText = "Delete developer";
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
                                const delete_response = await authorizedFetch(`/developers/${developer.id}`, {
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
                                    delete_message.innerText = "FORBIDDEN";
                                }
                                else{
                                    delete_message.innerText = `error ${delete_status}`;
                                }
                            })
                            };
                        right.style.marginLeft = "10px";
                        right.style.display = "flex";
                        right.appendChild(update_button);
                        right.appendChild(delete_button);
                        right.appendChild(delete_message);

                    }

                    div.appendChild(left);
                    div.appendChild(right);


                    div.style.fontSize = "20px";
                    div.style.marginBottom = "10px";

                    developers_div.appendChild(div);
                })
            }
            else{
                developers_div.innerText = `Max page: ${get_max_page()}`;
            }
        }
        else{
            developers_div.innerText = JSON.stringify(data);
        }

    document.getElementById("developers").style.display = "block";
    document.getElementById("loading").style.display = "none";
}


window.onload = function () {
    get_developers();
    page_input.value = getPage();
};

sorting.addEventListener("change", () => {
    get_developers();
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
            get_developers();
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

