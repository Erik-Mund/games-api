import { authorizedFetch } from "../auth/refresh.js";
import { getCookie } from "../auth/getCookie.js";
import { update_review } from "./update_review.js";

const gameId = window.location.pathname.split("/").pop();
const message = document.getElementById("review_message");
const delete_button = document.getElementById("delete_review");
const button = document.getElementById("submit_review");

async function postReview(){
    const data = {};

    const rating = document.querySelector('input[name="rating"]:checked')?.value;
    const comment = document.getElementById("review_text").value;

    if(rating) data.score = parseInt(rating);
    if(comment) data.comment = comment;

    const response = await authorizedFetch(`/games/${gameId}/reviews`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRF-TOKEN": getCookie("csrf_access_token")
        },
        body: JSON.stringify(data)
    });

    const result = await response.json()

    if (response.ok){
        document.getElementById("review_label").innerText = "My review: ";
        message.innerText = "Review published";
        button.innerText = "Update review";
        delete_button.style.display = "block";
        localStorage.setItem("my_review_id", result.id)
    }
    else{
        const stringified_result = JSON.stringify(result);
        message.innerText = JSON.stringify(result);
    }
}

document.addEventListener("DOMContentLoaded", () => {
    button.addEventListener("click", (e) => {
        e.preventDefault();
        if (button.innerText === "Submit review"){
            postReview();
        }
        else{
            update_review();
        }
    })
})