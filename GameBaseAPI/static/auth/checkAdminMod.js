import { authorizedFetch } from "./refresh.js";

let cachedUser = null;
let fetched = false;

async function getUser() {
    if (fetched) return cachedUser;

    try {
        const response = await authorizedFetch("/me");

        if (!response.ok) {
            fetched = true;
            cachedUser = null;
            return null;
        }

        const data = await response.json();
        cachedUser = data;
        fetched = true;
        return data;
    } catch {
        fetched = true;
        cachedUser = null;
        return null;
    }
}

export async function isAdminOrMod() {
    const get_user = await getUser();
    console.log(get_user?.role);
    console.log(get_user?.role === "moderator" || get_user?.role === "admin");
    return get_user?.role === "moderator" || get_user?.role === "admin";
}

export async function isAdmin() {
    const get_user = await getUser();
    return get_user?.role === "admin";
}

export async function isModerator() {
    const get_user = await getUser();
    return get_user?.role === "moderator";
}