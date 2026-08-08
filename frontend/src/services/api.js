import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost:8000"
});

export const startInterview = (candidateData) => {
  return api.post("/api/interview", candidateData);
};

export default api;