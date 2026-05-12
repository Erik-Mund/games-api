import { authorizedFetch } from "../auth/refresh.js"
import { getCookie } from "../auth/getCookie.js";

document.addEventListener("DOMContentLoaded", () => {
   const form = document.getElementById("delete_profile")
   const message = document.getElementById("message")
   let dev_id = 0;

   form.addEventListener("submit", async function(e){
       e.preventDefault();

       const get_response = await authorizedFetch("/me");
       const data = await get_response.json()
       console.log(data);
       if (get_response.ok){
           dev_id = data.developer_profile_id;
       }
       else{
           message.innerText = JSON.stringify(data);
           return;
       }

       const response = await authorizedFetch(`/developers/${dev_id}`, {
            method: "DELETE",
            headers: {
                "Content-Type": "application/json",
                "X-CSRF-TOKEN": getCookie("csrf_access_token")
            },
            body: JSON.stringify(data)
       });

       let result = null;
       try {
           result = await response.json();
       } catch {}

       if(response.ok){
           message.innerText = "Deletion successful";

           setTimeout(() => {
               window.location.href = "/";
           }, 900);
       }
       else{
           message.innerText = JSON.stringify(result);
       }
   })
});