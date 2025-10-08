// frontend/src/api.js
import axios from "axios";

const BASE = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

const api = axios.create({
  baseURL: BASE,
  timeout: 30000,
});

export default api;
