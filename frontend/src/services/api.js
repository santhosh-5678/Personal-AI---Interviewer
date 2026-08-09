import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Start interview
export const startInterview = async (sessionId, candidateId) => {
  const response = await api.post("/api/interview", {
    sessionId,
    candidateId,
    message: "",
  });

  return response.data;
};

// Send candidate answer
export const sendInterviewMessage = async (
  sessionId,
  candidateId,
  message
) => {
  const response = await api.post("/api/interview", {
    sessionId,
    candidateId,
    message,
  });

  return response.data;
};

export default api;