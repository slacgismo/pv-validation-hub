import axios from "axios";

const client = axios.create({
  baseURL: "http://13.58.157.194:8090",
});
export default client;