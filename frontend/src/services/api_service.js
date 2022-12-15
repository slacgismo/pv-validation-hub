import axios from "axios";

const client = axios.create({
  baseURL: "http://3.136.161.205:8090",
});
export default client;