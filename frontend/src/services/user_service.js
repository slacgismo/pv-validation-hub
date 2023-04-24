import client from "./api_service";
import { useEffect, useState } from "react";

export const UserService = {
    useGetUserDetails(url, token) {
        const [userDetails, setUserDetails] = useState();
        const [isLoading, setIsLoading] = useState(true);
        const [error, setError] = useState(null);

        // set authorization token
        client.defaults.headers.common['Authorization'] = "Token " + token;

        // set request
        useEffect(() => {
            client.get(url)
                .then(response => {
                    setUserDetails(response.data);
                    setIsLoading(false);
                })
                .catch(error => {
                    setError(error);
                    setUserDetails({});
                    setIsLoading(false);
                })
        }, [url]);
        return [isLoading, error, userDetails];
    },
    updateUserProfile(token, updatedProfile) {
        const url = "/account";
        // set authorization token
        client.defaults.headers.common['Authorization'] = "Token " + token;

        return client.put(url, updatedProfile).data;
    },
    register(username, email, password, first_name, last_name) {
        let url = "/register";
        client.post(url, {
            username: username,
            email: email,
            password: password,
            firstName: first_name,
            lastName: last_name
        }).then(response => {
            return response;
        }).catch(error => {
            return null;
        })
    }
} 
