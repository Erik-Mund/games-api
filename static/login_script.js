const form = document.getElementById("login-form")

form.addEventListener("submit", async function(e) {
   e.preventDefault();


    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;
    const message = document.getElementById("message");




    const response = await fetch("/login", {
        method: "POST", headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            email: email,
            password: password
        })
    });

    const data = await response.json();


    if (response.ok){
        localStorage.setItem("access_token", data.access_token);
        localStorage.setItem("refresh_token", data.refresh_token);
        console.log("successful login");
        message.innerText = "successful login";
        setTimeout(() => {
            window.location.href = "/";
            }, 900);
    }
    else{
        console.log("login not successful");
        message.innerText = "login not successful";
    }

});


