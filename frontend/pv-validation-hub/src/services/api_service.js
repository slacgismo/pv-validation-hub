import { useState, useEffect } from "react";

export const ApiService = {

    useApiGet(url) {

        const [response, setResponse] = useState();
        const [isLoading, setIsLoading] = useState(true);
        const [error, setError] = useState(null);

        useEffect(() => {
            fetch(url, {
                method: "GET",
                headers: new Headers({
                    Accept: "application/json"
                }),
            })
                .then(response => {
                    setResponse(response.json);
                    setIsLoading(false);
                })
                .catch(error => {
                    setError(error);
                    setIsLoading(false);
                })
        });
        return [isLoading, error, response];
    },

    apiPut(url, body) {
        fetch(url, {
            method: "PUT",
            headers: new Headers({
                Accept: "application/json"
            }),
            body: JSON.stringify(body)
        })
            .then(response => {
                return response.json;
            })
            .catch(error => {
                return null;
            })
    },

    apiPost(url, body) {
        fetch(url, {
            method: "POST",
            headers: new Headers({
                Accept: "application/json"
            }),
            body: JSON.stringify(body)
        })
            .then(response => {
                return response.json;
            })
            .catch(error => {
                return null;
            })
    }
}