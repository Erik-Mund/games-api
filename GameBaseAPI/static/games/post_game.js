import { authorizedFetch } from "../auth/refresh.js";
import { getCookie } from "../auth/getCookie.js";




document.addEventListener("DOMContentLoaded", async () => {
    const form = document.getElementById("post_game_form");

    const title_input = document.getElementById("title");
    const platform_input = document.getElementById("platform");
    const summary_input = document.getElementById("summary");
    const genres_input = document.getElementById("genres");
    const price_input = document.getElementById("price");
    const release_year_input = document.getElementById("release_year");

    const message = document.getElementById("message");

    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        const data = {}

        if (title_input) data.title = title_input.value;

        if (genres_input && genres_input.value.trim() !== "") {
            data.genres = genres_input.value.split(",").map(g => g.trim());
        } else {
            data.genres = [];
        }

        if (price_input && price_input.value !== "") {
            data.price = parseInt(price_input.value);
        }

        if (release_year_input && release_year_input.value !== "") {
            data.release_year = parseInt(release_year_input.value);
        }

        if (platform_input && platform_input.value.trim() !== "") {
            data.platform = platform_input.value;
        }

        if (summary_input && summary_input.value.trim() !== "") {
            data.summary = summary_input.value;
        }

        console.log(data);

        const response = await authorizedFetch('/games', {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRF-TOKEN": getCookie("csrf_access_token")
            },
            body: JSON.stringify(data)
        })

        const result = await response.json()

        if (response.ok){
            message.innerText = "game published successfully";

            const devResponse = await authorizedFetch(`/developers/get-my`);
            const devRes = await devResponse.json();
            console.log(devRes);
            const devId = devRes.id;

           setTimeout(() => {
               window.location.href = `/developer/${devId}/game-page/${result.id}`;
           }, 900);
        }
        else{
            message.innerText = JSON.stringify(result);
        }
    })
})