import {authorizedFetch} from "../auth/refresh.js";
import { getCookie } from "../auth/getCookie.js";
import {isAdminOrMod, isModerator} from "../auth/checkAdminMod.js";

const sorting = document.getElementById("sort");

let isAdminOrModBool = false;

let gameId = 0;
let devId = 0;
let grId = 0;

const path = window.location.pathname.split("/");
console.log(path);
console.log(path[0]);
console.log(path[3]);

if (path[1] === "games"){
    gameId = path[2];
    console.log(gameId);
}
else if (path[1] === "developers"){
    devId = path[2];
    gameId = path[4];
    console.log(gameId);
}
else if (path[1] === "developer"){
    devId = path[2];
    gameId = path[4];
    console.log(gameId);
}
else if (path[1] === "genres"){
    grId = path[2];
    gameId = path[4];
    console.log(gameId);
}

let page = 1;
let max_pages = 0;

let reviews_count = 0;

const reviews_div = document.getElementById("reviews");
const loading = document.getElementById("loading");

const page_input = document.getElementById("page_input");
const go_button = document.getElementById("go");


function getPage(){
    const page_raw = localStorage.getItem("page");

    if(page_raw !== null){
        page = parseInt(page_raw);
    }

    return page;
}
function get_max_page(per_page){
    if (!reviews_count || reviews_count < 0) return 1;
    max_pages = Math.ceil(reviews_count / per_page);
    return max_pages;
}

function createStars(score) {
    const container = document.createElement("div");
    container.className = "stars";

    for (let i = 1; i <= 5; i++) {
        const star = document.createElement("span");
        star.innerText = i <= score ? "★" : "☆";
        container.appendChild(star);
    }

    return container;
}

async function report_review(review_id, message){
    const report_response = await authorizedFetch(`/games/${gameId}/reviews/${review_id}/report`, {
        method: "POST",
        headers: {
            "X-CSRF-TOKEN": getCookie("csrf_access_token")
        }
    });
    const data = await report_response.json();

    if (report_response.ok){
        message.innerText = "Review reported";
        if (isAdminOrModBool){
            get_reviews();
        }
    }
    else{
        message.innerText = JSON.stringify(data);
    }
}

async function get_reviews(){
    document.getElementById("loading").style.display = "block";
    document.getElementById("reviews").style.display = "none";

    if (await isAdminOrMod()){
        isAdminOrModBool = true;
    }

    const per_page = document.getElementById("per_page").value;
    const params = new URLSearchParams({
            sort: sorting.value,
            per_page: per_page,
            page: getPage(),
            with_comments: "true"
    })

    const response = await fetch(`/games/${gameId}/reviews?${params.toString()}`);

        const data = await response.json()
        console.log(data);

        if (response.ok){
            reviews_div.innerHTML = "";

            reviews_count = data.total_count;

            if (reviews_count === 0){
                document.getElementById("reviews").style.display = "block";
                document.getElementById("loading").style.display = "none";
                reviews_div.innerText = "no reviews yet";
                return;
            }

            if (getPage() <= get_max_page(per_page)){
                data.reviews.forEach(review => {
                    if (review.comment !== "" && review.comment !== null){
                        const reviewCard = document.createElement("div");
                        reviewCard.className = "review-card";

                        const stars = createStars(review.score);

                        const comment = document.createElement("p");
                        comment.className = "review-comment";
                        comment.innerText = review.comment || "No comment";

                        const user = document.createElement("p");
                        user.className = "review-user";
                        user.innerText = `— ${review.username}`;

                        const button = document.createElement("button");
                        button.innerText = "Report";
                        button.className = "report-button";

                        const report_message = document.createElement("p");
                        button.addEventListener("click", () => {
                            report_review(review.id, report_message);
                        })

                        const actions = document.createElement("div");
                        actions.className = "review-actions";

                        actions.appendChild(button);
                        actions.appendChild(report_message);

                        if (isAdminOrModBool){
                            const report_count_text = document.createElement("span");
                            report_count_text.innerText = `Reports: ${review.report_count}`;
                            const delete_button = document.createElement("button");
                            delete_button.innerText = "Delete review";
                            delete_button.style.marginLeft = "10px";
                            const delete_message = document.createElement("div");
                            delete_button.addEventListener("click", async (e) => {
                                    e.preventDefault();
                                    const delete_response = await authorizedFetch(`/games/${gameId}/reviews/${review.id}`, {
                                        method: "DELETE",
                                        headers: {
                                            "X-CSRF-TOKEN": getCookie("csrf_access_token")
                                        }
                                    })
                                    const delete_status = delete_response.status;
                                    if (delete_status === 204){
                                        delete_message.innerText = "deleted successfully";
                                        setTimeout(() => {
                                            reviewCard.remove();
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
                            actions.appendChild(delete_button);
                            actions.appendChild(report_count_text);
                            actions.appendChild(delete_message);

                        }

                        reviewCard.appendChild(stars);
                        reviewCard.appendChild(comment);
                        reviewCard.appendChild(user);
                        reviewCard.appendChild(actions);

                        reviews_div.appendChild(reviewCard);
                    }
                })
            }
            else{
                reviews_div.innerText = `Max page: ${get_max_page(per_page)}`;
            }
        }
        else{
            reviews_div.innerText = JSON.stringify(data);
        }

    document.getElementById("reviews").style.display = "block";
    document.getElementById("loading").style.display = "none";
}




window.onload = function () {
    get_reviews();
    page_input.value = getPage();
};

sorting.addEventListener("change", () => {
    get_reviews();
})

go_button.addEventListener("click", () => {
    changePage();
})

document.getElementById("back").addEventListener("click", (e) => {
        e.preventDefault();
        if (path[1] === "game-page"){
            window.location.href = `/game-page/${gameId}`;
        }
        else if (path[1] === "developers"){
            window.location.href = `/developers/${devId}/game-page/${gameId}`;
        }
        else if (path[1] === "developer"){
            window.location.href = `/developer/${devId}/game-page/${gameId}`
        }
        else if (path[1] === "genres"){
            window.location.href = `/genres/${grId}/game-page/${gameId}`
        }
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
            get_reviews();
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