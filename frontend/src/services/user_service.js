import client from "./api_service";
import { useEffect, useState } from "react";
import { faker } from "@faker-js/faker";

const base_uri = "http://localhost:8000"

export const UserService = {

    useGetUserDetails(userId) {
        const [userDetails, setUserDetails] = useState();
        const [isLoading, setIsLoading] = useState(true);
        const [error, setError] = useState(null);

        useEffect(() => {
            const url = base_uri + "/account/" + userId;
            client.get(url)
                .then(response => {
                    let output = response.data();
                    output["avatar"] = faker.image.avatar();
                    output["location"] = faker.address.city() + ", " + faker.address.stateAbbr();
                    output["subscriptionTier"] = faker.helpers.arrayElement(['admin', 'developer', 'viewer']);
                    setUserDetails(response);
                    console.log(response);
                    setIsLoading(false);
                })
                .catch(error => {
                    setError(error);
                    setIsLoading(false);
                })
        }, [userId]);
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
