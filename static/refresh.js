export async function Refresh(){
    const refresh_token = localStorage.getItem("refresh_token")
    const response = await fetch("/refresh", {
        method: "POST",
        headers: {"Authorization" : `Bearer ${refresh_token}`}
    });

    if (!response.ok){
        return null;
    }

    const data = await response.json()

    localStorage.setItem("access_token", data.access_token);
    localStorage.setItem("refresh_token", data.refresh_token);

    return data.access_token;
}

export async function authorizedFetch(url, options = {}) {
    let token = localStorage.getItem("access_token");

    options.headers = {
        ...options.headers,
        "Authorization": `Bearer ${token}`
    };

    let response = await fetch(url, options);
    console.log("loading");

    if(response.status === 401) {
        token = await Refresh();

        if (!token) {
            window.location.href = "/login";
            return;
        }

        options.headers["Authorization"] = `Bearer ${token}`;
        response = await fetch(url, options);
    }

    return response;
}