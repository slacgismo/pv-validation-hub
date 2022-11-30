import { ApiService } from "./api_service";
import { create_fake_user_data } from "./fake_data_service";

const protocol = "http";
const host = "192.168.56.1:8000";

function get_base_url() {
    return protocol + "://" + host;
}

export const UserService = {
    GetUserDetails(userId) {
        // let url = get_base_url() + "/account/" + userId;
        // return ApiService.useApiGet(url);
        return create_fake_user_data();

    },
    register(username, email, password) {
        let url = get_base_url() + "/register";
        return ApiService.apiPost(url, {
            username: username,
            email: email,
            password: password
        })
    },

    login(username, password) {
        let url = get_base_url() + "/login";
        return ApiService.apiPost(
            url,
            {
                username: username,
                password: password
            }
        );
    }
} 
