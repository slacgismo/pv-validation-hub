import client from "./api_service";
import { useEffect, useState } from "react";
import { faker } from "@faker-js/faker";

export const UserService = {

    useGetUserDetails(url) {
        const [userDetails, setUserDetails] = useState();
        const [isLoading, setIsLoading] = useState(true);
        const [error, setError] = useState(null);

        useEffect(() => {
            client.get(url)
                .then(response => {
                    console.log('send url: ', url, ", get response: ", response);
                    setUserDetails(response.data);
                    console.log(response.data);
                    setIsLoading(false);
                })
                .catch(error => {
                    console.log('send url: ', url, ", get error: ", error);
                    setError(error);
                    setUserDetails({});
                    setIsLoading(false);
                })
        }, [url]);
        return [isLoading, error, userDetails];

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
