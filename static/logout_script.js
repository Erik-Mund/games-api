async function loadLogout() {
    const access_token = localStorage.getItem("access_token");
    const refresh_token = localStorage.getItem("refresh_token")
    const message = document.getElementById("message");

    if (!access_token || !refresh_token){
        message.innerText = "not authorized";
        return;
    }

    const response = await fetch("/logout", {
        method: "POST",
        headers: {
            "Authorization": `Bearer ${access_token}`
        }
    });

    const refresh_response = await fetch("/logout/refresh", {
        method: "POST",
        headers: {
            "Authorization": `Bearer ${refresh_token}`
        }
    });

    if (response.ok && refresh_response.ok){
        localStorage.removeItem("access_token")
        localStorage.removeItem("refresh_token")
        message.innerText = "Logged out successfully";
        setTimeout(() => {
            window.location.href = "/";
            }, 900);
    }
    else {
        message.innerText = "expired token";
    }
}