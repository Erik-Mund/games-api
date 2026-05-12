import { authorizedFetch } from "../auth/refresh.js";
import { getCookie } from "../auth/getCookie.js";

const gameId = window.location.pathname.split("/").pop();
const message = document.getElementById("review_message");

export async function update_review(){
    const comment_area = document.getElementById("review_text").value;
    const rating = document.querySelector('input[name="rating"]:checked')?.value;
    const data = {};
    if (comment_area) data.comment = comment_area;
    if (rating) data.score = parseInt(rating);

    const review_id = parseInt(localStorage.getItem("my_review_id"));
    const response = await authorizedFetch(`/games/${gameId}/reviews/${review_id}`, {
        method: "PUT",
        headers: {
            "Content-Type": "application/json",
            "X-CSRF-TOKEN": getCookie("csrf_access_token")
        },
        body: JSON.stringify(data)
    })

    const result = await response.json()

    if (response.ok){
        message.innerText = "Review updated";
    }
    else{
        message.innerText = JSON.stringify(result);
    }
}