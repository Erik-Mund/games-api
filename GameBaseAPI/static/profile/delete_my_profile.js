import { authorizedFetch } from "../auth/refresh.js"
import { getCookie } from "../auth/getCookie.js";

document.addEventListener("DOMContentLoaded", () => {
   const form = document.getElementById("delete_profile")
   const message = document.getElementById("message")

   form.addEventListener("submit", async function(e){
       e.preventDefault();

       const data = {};

       const password = document.getElementById("password").value;
       data.password = password;

       const response = await authorizedFetch("/me", {
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