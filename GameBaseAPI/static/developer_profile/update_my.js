import { authorizedFetch } from "../auth/refresh.js";
import { getCookie } from "../auth/getCookie.js";

document.addEventListener("DOMContentLoaded", async () => {
    const form = document.getElementById("dev-form");
    const message = document.getElementById("message");
    const studio_name_field = document.getElementById("studio_name");
    let dev_id = 0;

    const get_response = await authorizedFetch('/developers/get-my');
    const get_response_data = await get_response.json();
    if (get_response.ok){
        dev_id = get_response_data.id;
        studio_name_field.value = get_response_data.studio_name;
    }
    else{
        message.innerText = JSON.stringify(get_response_data);
        return;
    }

    form.addEventListener("submit", async function (e){
        e.preventDefault();

        const data = {};
        if (studio_name_field) data.studio_name = studio_name_field.value;

        const response = await authorizedFetch(`/developers/${dev_id}`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json",
                "X-CSRF-TOKEN": getCookie("csrf_access_token")
            },
            body: JSON.stringify(data)
        })

        const result = await response.json();

        if (response.ok) {
            message.innerText = "Developer profile updated";
            setTimeout(() => {
                window.location.href = "/developer-profile-page";}, 900);
        }
        else{
            message.innerText = JSON.stringify(result);
        }
    })
})