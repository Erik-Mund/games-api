import { authorizedFetch } from "../auth/refresh.js";
import { getCookie } from "../auth/getCookie.js";

const gameId = window.location.pathname.split("/").pop();
const message = document.getElementById("review_message");
const delete_button = document.getElementById("delete_review");

let result = null;

async function delete_review(){
    const review_id = localStorage.getItem("my_review_id");

    const response = await authorizedFetch(`/games/${gameId}/reviews/${review_id}`, {
        method: "DELETE",
        headers: {
            "X-CSRF-TOKEN": getCookie("csrf_access_token")
        }
    });

    if (response.status !== 204){
        result = await response.json()
    }

    if (response.ok){
        document.getElementById("review_label").innerText = "Post review: ";
        message.innerText = "Review deleted";
        document.getElementById("review_text").value = "";
        document.getElementById("submit_review").innerText = "Submit review";
        localStorage.removeItem("my_review_id");
        delete_button.style.display = "none";
    }
    else{
        message.innerText = JSON.stringify(result);
    }
}

delete_button.addEventListener("click", async (e) => {
    e.preventDefault()

    delete_review();
})


