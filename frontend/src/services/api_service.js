import axios from "axios";

const client = axios.create({
//  baseURL: "http://3.136.161.205:8090",
  baseURL: "http://0.0.0.0:8005",
});
export default client;