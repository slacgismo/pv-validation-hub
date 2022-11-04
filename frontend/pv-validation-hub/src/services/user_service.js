
const axios = require('axios');

export async function GetUsers() {

    try {
        const response = await axios.get('/api/users');
        return response.data;
    } catch (error) {
        return [];
    }

}

export async function CreateUser(data) {
    try {
        const response = await axios.post(`/api/user`, { user: data });
        return response.data;
    } catch (error) {
        return [];
    }
}