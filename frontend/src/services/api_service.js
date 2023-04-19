import axios from "axios";
import hubapi from "../config/environment";

const client = axios.create({
  baseURL: hubapi.api.baseUrl.app,
});
export default client;