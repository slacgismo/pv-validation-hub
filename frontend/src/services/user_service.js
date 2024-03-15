import { useEffect, useState } from 'react';
import Cookies from 'universal-cookie';
import client from './api_service.js';

const UserService = {
  useGetUserDetails(url, token) {
    const [userDetails, setUserDetails] = useState();
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);

    // set authorization token
    client.defaults.headers.common.Authorization = `Token ${token}`;

    // set request
    useEffect(() => {
      client.get(url)
        .then((response) => {
          setUserDetails(response.data);
          setIsLoading(false);
        })
        .catch((responseError) => {
          setError(responseError);
          setUserDetails({});
          setIsLoading(false);
        });
    }, [url]);
    return [isLoading, error, userDetails];
  },
  updateUserProfile(token, updatedProfile) {
    const url = '/account';
    // set authorization token
    client.defaults.headers.common.Authorization = `Token ${token}`;

    return client.put(url, updatedProfile).data;
  },
  register(username, email, password, firstName, lastName) {
    const url = '/register';
    client.post(url, {
      username,
      email,
      password,
      firstName,
      lastName,
    }).then((response) => response).catch((error) => console.error(error));
  },
  getUserId(token) {
    // Set the authorization token
    client.defaults.headers.common.Authorization = `Token ${token}`;

    // Send a GET request to the '/user_id' endpoint
    return client.get('/user_id')
      .then((response) => response.data.user_id);
  },
  getUserCookie() {
    // todo(jrl): abstract user cookie information to a service
    const cookies = new Cookies();
    const user = cookies.get('user');
    return user;
  },
};

export default UserService;
