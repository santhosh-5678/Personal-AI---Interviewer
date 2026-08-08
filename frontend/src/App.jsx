import { useEffect, useState } from "react";
import { startInterview } from "./services/api";

function App() {
  const [reply, setReply] = useState("");

  useEffect(() => {
    const candidateData = {
      sessionId: "abc-123",
      candidate: {
        member: {
          id: "CAND-001",
          name: "Sarah Johnson",
          jobRole: "Senior Data Engineer",
          yearsExperience: 9,
          education: "MS Computer Science",
          status: "COMPLETED"
        },
        missions: [
          {
            day: 7,
            title: "Embeddings Explained",
            passed: true,
            attempts: 1
          }
        ],
        signals: {
          commitDays: 28,
          missionsCompleted: 30,
          missionsFirstTry: 20
        }
      }
    };

    startInterview(candidateData)
      .then((response) => {
        setReply(response.data.reply);
      })
      .catch((error) => {
        console.error("Interview API failed:", error);
      });
  }, []);

  return (
    <div>
      <h1>AI Interview Agent</h1>
      <p>{reply}</p>
    </div>
  );
}

export default App;