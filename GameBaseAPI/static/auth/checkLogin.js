import { authorizedFetch } from "./refresh.js";

export async function isLoggedIn() {
    const response = await authorizedFetch("/me");
    return response.ok;
}