import { getCookie } from "./getCookie.js";

export async function Refresh(){
    const response = await fetch("/refresh", {
        method: "POST",
        credentials: "include",
        headers: {
            "X-CSRF-TOKEN": getCookie("csrf_refresh_token")
        }
    });

    if (!response.ok){
        return null;
    }

    return true;
}

export async function authorizedFetch(url, options = {}) {
    options = {
        ...options,
        credentials: "include",
        headers: {
            ...options.headers
        }
    };

    let response = await fetch(url, options);
    console.log("loading");

    if(response.status === 401) {
        const refreshed = await Refresh();

        if (!refreshed) {
            return response;
        }
        options.headers["X-CSRF-TOKEN"] = getCookie("csrf_access_token");

        await new Promise(r => setTimeout(r, 50))

        response = await fetch(url, options);
    }

    return response;
}