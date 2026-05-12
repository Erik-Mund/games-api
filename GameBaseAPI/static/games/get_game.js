import { authorizedFetch } from "../auth/refresh.js";

document.getElementById("title").innerText = "Loading...";

let gameId = 0;
let devId = 0;
let grId = 0;

const path = window.location.pathname.split("/");
console.log(path);
console.log(path[0]);
console.log(path[3]);

let report_endpoint = "";

if (path[1] === "game-page"){
    gameId = path[2];
    console.log(gameId);
    report_endpoint = `/game-report-page/${gameId}`;
}
else if (path[1] === "developers"){
    devId = path[2];
    gameId = path[4];
    console.log(gameId);
    report_endpoint = `/developers/${devId}/game-report-page/${gameId}`;
}
else if (path[1] === "developer"){
    devId = path[2];
    gameId = path[4];
    console.log(gameId);
    report_endpoint = `/developer/${devId}/game-report-page/${gameId}`;
}
else if (path[1] === "genres"){
    grId = path[2];
    gameId = path[4];
    console.log(gameId);
    report_endpoint = `/genres/${grId}/game-report-page/${gameId}`;
}

document.addEventListener("DOMContentLoaded", () => {

    const button = document.getElementById("report_button")
    button.addEventListener("click", (e) => {
        e.preventDefault();
        window.location.href = report_endpoint;
    })

    const back_button = document.getElementById("back");
    back_button.addEventListener("click", (e) => {
        e.preventDefault();
        if (path[1] === "game-page"){
            window.location.href = `/all-games`;
        }
        else if (path[1] === "developers"){
            window.location.href = `/developer-games`
        }
        else if (path[1] === "developer"){
            window.location.href = `/my-games`
        }
        else if (path[1] === "genres"){
            window.location.href = `/genres-games`
        }
    })

    const see_reviews_button = document.getElementById("get_reviews_button");
    see_reviews_button.addEventListener("click", (e) => {
        e.preventDefault();
        window.location.href = `/games/${gameId}/reviews-page`;
    })

    let update_button;
    let delete_button;
    console.log("1");
    if (document.getElementById("update_game") !== null){
        console.log("2");
        update_button = document.getElementById("update_game");
        delete_button = document.getElementById("delete_game");

        update_button.addEventListener("click", (e) => {
            e.preventDefault();
            window.location.href = `/developer/update-game/${gameId}`;
        })

        delete_button.addEventListener("click", (e) => {
            e.preventDefault();
            window.location.href = `/delete-game/${gameId}`;
        })
    }
    else{
        console.log(document.getElementById("update_game"));
    }
})



async function loadGame() {
    let response = await authorizedFetch(`/games/${gameId}`);
    let data = await response.json();

    document.getElementById("title").innerText = data.title;
    document.getElementById("platform").innerText = `Platform(s): ${data.platform}`;
    if (data.average_rating === 0){
        document.getElementById("average_rating").innerText = `Rating: no reviews yet`;
    }
    else{
        const rating = Math.round(data.average_rating * 10) / 10
        document.getElementById("average_rating").innerText = `Rating: ${rating}/5`;
    }
    document.getElementById("release_year").innerText = `Release year: ${data.release_year}`;
    document.getElementById("genres").innerText = `Genres: ${data.genres}`
    document.getElementById("price").innerText = `Price: ${data.price}$`;
    document.getElementById("summary").innerText = `Summary: ${data.summary}`;

    if (!data.my_review){
        response = await authorizedFetch(`/games/${gameId}`);
        if (response.ok) {
            data = await response.json()
        }
    }

    if (data.my_review){
        document.getElementById("review_label").innerText = "My review: ";
        document.getElementById("delete_review").style = "block";

        const score = data.my_review.score;
        const star = document.querySelector(`input[name="rating"][value="${score}"]`);
        if (star) {
            star.checked = true;
        }

        document.getElementById("review_text").value = data.my_review.comment;
        localStorage.setItem("my_review_id", data.my_review.id);

        document.getElementById("submit_review").innerText = "Update review";
    }
    else{
        localStorage.removeItem("my_review_id");
    }

    console.log(data);
}


document.addEventListener("DOMContentLoaded", async () => {
    await authorizedFetch("/me");
    await loadGame();
})

