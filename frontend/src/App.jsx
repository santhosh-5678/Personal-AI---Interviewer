import { useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import "./App.css";
import {
  sendInterviewMessage,
  startInterview,
} from "./services/api";

/* =========================================================
   CANDIDATE DATA HELPERS
========================================================= */

function normalizeCandidates(data) {
  if (Array.isArray(data)) {
    return data;
  }

  if (Array.isArray(data?.candidates)) {
    return data.candidates;
  }

  if (Array.isArray(data?.data)) {
    return data.data;
  }

  return [];
}

function getCandidateMember(candidate) {
  return candidate?.member || candidate || {};
}

function getCandidateName(candidate) {
  const member = getCandidateMember(candidate);

  return (
    member.name ||
    member.fullName ||
    member.full_name ||
    candidate?.name ||
    candidate?.fullName ||
    candidate?.full_name ||
    "Interview Candidate"
  );
}

function getCandidateRole(candidate) {
  const member = getCandidateMember(candidate);

  return (
    member.jobRole ||
    member.job_role ||
    member.role ||
    candidate?.jobRole ||
    candidate?.job_role ||
    candidate?.role ||
    "Technical Interview"
  );
}

function getCandidateExperience(candidate) {
  const member = getCandidateMember(candidate);

  const experience =
    member.yearsExperience ??
    member.years_experience ??
    member.experience ??
    member.experienceYears ??
    candidate?.yearsExperience ??
    candidate?.years_experience ??
    candidate?.experience ??
    candidate?.experienceYears;

  if (
    experience === undefined ||
    experience === null ||
    experience === ""
  ) {
    return "Not specified";
  }

  if (typeof experience === "number") {
    return `${experience} years`;
  }

  return String(experience);
}

function getCandidateEducation(candidate) {
  const member = getCandidateMember(candidate);

  return (
    member.education ||
    member.highestQualification ||
    member.highest_qualification ||
    member.degree ||
    candidate?.education ||
    candidate?.highestQualification ||
    candidate?.highest_qualification ||
    candidate?.degree ||
    "Not specified"
  );
}

function getCandidateInitial(candidate) {
  const name = getCandidateName(candidate);

  return name.charAt(0).toUpperCase();
}

function getCandidateId(candidate) {
  const member = getCandidateMember(candidate);

  return (
    candidate?.id ||
    candidate?.candidateId ||
    candidate?.candidate_id ||
    member?.id ||
    member?.candidateId ||
    member?.candidate_id ||
    null
  );
}

/* =========================================================
   SESSION HELPERS
========================================================= */

function createSessionId() {
  if (
    typeof crypto !== "undefined" &&
    typeof crypto.randomUUID === "function"
  ) {
    return crypto.randomUUID();
  }

  return `${Date.now()}-${Math.random()
    .toString(36)
    .substring(2)}`;
}

/* =========================================================
   API RESPONSE HELPER
========================================================= */

function extractReply(data) {
  return (
    data?.reply ||
    data?.message ||
    data?.ai_reply ||
    data?.aiReply ||
    data?.response ||
    data?.content ||
    "I couldn't generate a response. Please try again."
  );
}

/* =========================================================
   APP
========================================================= */

function App() {
  /* =======================================================
     CANDIDATE STATE
  ======================================================= */

  const [candidates, setCandidates] = useState([]);

  const [selectedCandidate, setSelectedCandidate] =
    useState(null);

  const [isLoadingCandidates, setIsLoadingCandidates] =
    useState(true);

  /* =======================================================
     INTERVIEW STATE
  ======================================================= */

  const [sessionId, setSessionId] = useState(
    createSessionId()
  );

  const [messages, setMessages] = useState([]);

  const [input, setInput] = useState("");

  const [isLoading, setIsLoading] = useState(false);

  const [interviewStarted, setInterviewStarted] =
    useState(false);

  /* =======================================================
     ERROR STATE
  ======================================================= */

  const [error, setError] = useState("");

  /* =======================================================
     REFS
  ======================================================= */

  const messagesEndRef = useRef(null);

  /* =======================================================
     LOAD CANDIDATES
     
     File location:
     
     frontend/
       public/
         data/
           candidates.json
  ======================================================= */

  useEffect(() => {
    const loadCandidates = async () => {
      try {
        setIsLoadingCandidates(true);
        setError("");

        const response = await fetch(
          "/data/candidates.json"
        );

        if (!response.ok) {
          throw new Error(
            `Unable to load candidates.json (${response.status})`
          );
        }

        const data = await response.json();

        const loadedCandidates =
          normalizeCandidates(data);

        if (loadedCandidates.length === 0) {
          throw new Error(
            "No candidates found in candidates.json."
          );
        }

        setCandidates(loadedCandidates);

        // Automatically select first candidate
        setSelectedCandidate(loadedCandidates[0]);
      } catch (loadError) {
        console.error(
          "Candidate data error:",
          loadError
        );

        setError(
          loadError.message ||
            "Unable to load candidate data."
        );
      } finally {
        setIsLoadingCandidates(false);
      }
    };

    loadCandidates();
  }, []);

  /* =======================================================
     RESET INTERVIEW WHEN CANDIDATE CHANGES
  ======================================================= */

  useEffect(() => {
    if (!selectedCandidate) {
      return;
    }

    const newSessionId = createSessionId();
    const candidateId = selectedCandidate.member.id;

    setSessionId(newSessionId);
    setMessages([]);
    setInput("");
    setError("");
    setInterviewStarted(false);
    setIsLoading(true);

    const beginInterview = async () => {
      try {
        const data = await startInterview(
          newSessionId,
          candidateId
        );

        setMessages([
          {
            id: `assistant-${Date.now()}`,
            role: "assistant",
            content: extractReply(data),
          },
        ]);
      } catch (requestError) {
        console.error("Interview API error:", requestError);
        setError(
          requestError.message ||
            "Unable to connect to the interview server."
        );
      } finally {
        setIsLoading(false);
      }
    };

    beginInterview();
  }, [selectedCandidate]);

  /* =======================================================
     SCROLL TO LATEST MESSAGE
  ======================================================= */

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [messages, isLoading]);

  /* =======================================================
     SELECT CANDIDATE
  ======================================================= */

  const handleCandidateSelect = (candidate) => {
    if (isLoading) {
      return;
    }

    setSelectedCandidate(candidate);
  };

  /* =======================================================
     SEND MESSAGE TO BACKEND
  ======================================================= */

  const sendMessage = async () => {
    const trimmedMessage = input.trim();

    if (!trimmedMessage || isLoading) {
      return;
    }

    if (!selectedCandidate) {
      setError("No candidate is selected.");
      return;
    }

    /* -------------------------------------------------------
       Create user's message
    ------------------------------------------------------- */

    const userMessage = {
      id: `user-${Date.now()}`,
      role: "user",
      content: trimmedMessage,
    };

    /* -------------------------------------------------------
       Update UI immediately
    ------------------------------------------------------- */

    setMessages((previousMessages) => [
      ...previousMessages,
      userMessage,
    ]);

    setInput("");

    setError("");

    setInterviewStarted(true);

    setIsLoading(true);

    /* -------------------------------------------------------
       Send request to FastAPI
    ------------------------------------------------------- */

    try {
      const data = await sendInterviewMessage(
        sessionId,
        selectedCandidate.member.id,
        trimmedMessage
      );

      /* -----------------------------------------------------
         Extract AI response
      ----------------------------------------------------- */

      const aiReply = extractReply(data);

      const assistantMessage = {
        id: `assistant-${Date.now()}`,
        role: "assistant",
        content: aiReply,
      };

      setMessages((previousMessages) => [
        ...previousMessages,
        assistantMessage,
      ]);
    } catch (requestError) {
      console.error(
        "Interview API error:",
        requestError
      );

      setError(
        requestError.message ||
          "Unable to connect to the interview server."
      );
    } finally {
      setIsLoading(false);
    }
  };

  /* =======================================================
     ENTER KEY
  ======================================================= */

  const handleKeyDown = (event) => {
    if (
      event.key === "Enter" &&
      !event.shiftKey
    ) {
      event.preventDefault();

      sendMessage();
    }
  };

  /* =======================================================
     CANDIDATE DISPLAY DATA
     
     Everything here comes from candidates.json.
  ======================================================= */

  const candidateName = selectedCandidate
    ? getCandidateName(selectedCandidate)
    : "Interview Candidate";

  const candidateInitial = selectedCandidate
    ? getCandidateInitial(selectedCandidate)
    : "C";

  const candidateRole = selectedCandidate
    ? getCandidateRole(selectedCandidate)
    : "Technical Interview";

  const candidateExperience = selectedCandidate
    ? getCandidateExperience(selectedCandidate)
    : "Not specified";

  const candidateEducation = selectedCandidate
    ? getCandidateEducation(selectedCandidate)
    : "Not specified";

  const candidateId = selectedCandidate
    ? getCandidateId(selectedCandidate)
    : null;

  /* =======================================================
     LOADING STATE
  ======================================================= */

  if (isLoadingCandidates) {
    return (
      <div className="app">

        <aside className="candidate-sidebar">

          <div className="candidate-profile">

            <div className="candidate-avatar large">
              ...
            </div>

            <h1>Loading Candidate</h1>

            <div className="candidate-badge">
              Loading...
            </div>

          </div>

        </aside>

        <main className="interview-area">

          <div className="messages-container">

            <div className="messages-list">

              <div className="message-row assistant-row">

                <div className="message-avatar ai-message-avatar">
                  AI
                </div>

                <div className="message-content assistant-content">

                  <div className="message-sender">
                    Interview Agent
                  </div>

                  <div className="message-bubble assistant-bubble">
                    Loading candidate information...
                  </div>

                </div>

              </div>

            </div>

          </div>

        </main>

      </div>
    );
  }

  /* =======================================================
     MAIN UI
  ======================================================= */

  return (
    <div className="app">

      {/* =================================================
          LEFT SIDEBAR
      ================================================= */}

      <aside className="candidate-sidebar">

        {/* Candidate Header */}

        <div className="candidate-header">

          <div className="candidate-avatar small">
            {candidateInitial}
          </div>

          <div className="candidate-header-info">

            <h2>
              {candidateName}
            </h2>

            <p>
              {candidateRole}
            </p>

          </div>

        </div>

        {/* =================================================
            CANDIDATE LIST
        ================================================= */}

        {candidates.length > 1 && (
          <div className="candidate-selector">

            <div className="candidate-selector-title">
              CANDIDATES
            </div>

            <div className="candidate-list">

              {candidates.map((candidate, index) => {

                const itemId =
                  getCandidateId(candidate) ||
                  `candidate-${index}`;

                const isSelected =
                  selectedCandidate === candidate;

                return (
                  <button
                    key={itemId}
                    type="button"
                    className={`candidate-list-item ${
                      isSelected ? "selected" : ""
                    }`}
                    onClick={() =>
                      handleCandidateSelect(candidate)
                    }
                    disabled={isLoading}
                  >

                    <div className="candidate-avatar small">
                      {getCandidateInitial(candidate)}
                    </div>

                    <div className="candidate-list-info">

                      <strong>
                        {getCandidateName(candidate)}
                      </strong>

                      <span>
                        {getCandidateRole(candidate)}
                      </span>

                    </div>

                  </button>
                );
              })}

            </div>

          </div>
        )}

        {/* =================================================
            CANDIDATE PROFILE
        ================================================= */}

        <div className="candidate-profile">

          <div className="candidate-avatar large">
            {candidateInitial}
          </div>

          <h1>
            {candidateName}
          </h1>

          <div className="candidate-badge">
            {candidateRole}
          </div>

        </div>

        {/* =================================================
            CANDIDATE INFORMATION
        ================================================= */}

        <div className="candidate-info">

          {/* Candidate ID */}

          {candidateId && (
            <div className="info-item">

              <span className="info-label">
                CANDIDATE ID
              </span>

              <span className="info-value">
                {candidateId}
              </span>

            </div>
          )}

          {/* Role */}

          <div className="info-item">

            <span className="info-label">
              ROLE
            </span>

            <span className="info-value">
              {candidateRole}
            </span>

          </div>

          {/* Experience */}

          <div className="info-item">

            <span className="info-label">
              EXPERIENCE
            </span>

            <span className="info-value">
              {candidateExperience}
            </span>

          </div>

          {/* Education */}

          <div className="info-item">

            <span className="info-label">
              EDUCATION
            </span>

            <span className="info-value">
              {candidateEducation}
            </span>

          </div>

          {/* Interview Status */}

          <div className="info-item">

            <span className="info-label">
              STATUS
            </span>

            <span
              className={`info-status ${
                interviewStarted
                  ? "in-progress"
                  : "not-started"
              }`}
            >

              <span className="status-dot"></span>

              {interviewStarted
                ? "In Progress"
                : "Not Started"}

            </span>

          </div>

        </div>

      </aside>

      {/* =================================================
          MAIN INTERVIEW AREA
      ================================================= */}

      <main className="interview-area">

        {/* =================================================
            TOP BAR
        ================================================= */}

        <header className="interview-header">

          <div className="interview-header-left">

            <div className="header-ai-avatar">
              AI
            </div>

            <div>

              <h2>
                Interview Agent
              </h2>

              <p>
                AI Technical Interview
              </p>

            </div>

          </div>

          <div className="online-status">

            <span className="online-dot"></span>

            <span>
              Online
            </span>

          </div>

        </header>

        {/* =================================================
            MESSAGES
        ================================================= */}

        <section className="messages-container">

          <div className="messages-list">

            {messages.map((message) => {

              const isAssistant =
                message.role === "assistant";

              return (
                <div
                  key={message.id}
                  className={`message-row ${
                    isAssistant
                      ? "assistant-row"
                      : "user-row"
                  }`}
                >

                  {/* AI Avatar */}

                  {isAssistant && (
                    <div className="message-avatar ai-message-avatar">
                      AI
                    </div>
                  )}

                  {/* Message Content */}

                  <div
                    className={`message-content ${
                      isAssistant
                        ? "assistant-content"
                        : "user-content"
                    }`}
                  >

                    {isAssistant && (
                      <div className="message-sender">
                        Interview Agent
                      </div>
                    )}

                    <div
                      className={`message-bubble ${
                        isAssistant
                          ? "assistant-bubble"
                          : "user-bubble"
                      }`}
                    >
                      {isAssistant ? (
                        <ReactMarkdown>
                          {message.content}
                        </ReactMarkdown>
                      ) : (
                        message.content
                      )}
                    </div>

                  </div>

                  {/* User Avatar */}

                  {!isAssistant && (
                    <div className="message-avatar user-message-avatar">
                      You
                    </div>
                  )}

                </div>
              );
            })}

            {/* =================================================
                AI TYPING INDICATOR
            ================================================= */}

            {isLoading && (
              <div className="message-row assistant-row">

                <div className="message-avatar ai-message-avatar">
                  AI
                </div>

                <div className="message-content assistant-content">

                  <div className="message-sender">
                    Interview Agent
                  </div>

                  <div className="message-bubble assistant-bubble typing-bubble">

                    <span></span>
                    <span></span>
                    <span></span>

                  </div>

                </div>

              </div>
            )}

            <div ref={messagesEndRef}></div>

          </div>

        </section>

        {/* =================================================
            INPUT AREA
        ================================================= */}

        <footer className="input-section">

          {/* Error */}

          {error && (
            <div className="error-message">
              {error}
            </div>
          )}

          {/* Message Input */}

          <div className="input-wrapper">

            <textarea
              value={input}
              onChange={(event) =>
                setInput(event.target.value)
              }
              onKeyDown={handleKeyDown}
              placeholder="Type your answer here..."
              rows={1}
              disabled={
                isLoading ||
                !selectedCandidate
              }
            />

            <button
              type="button"
              className={`send-button ${
                input.trim() && !isLoading
                  ? "active"
                  : ""
              }`}
              onClick={sendMessage}
              disabled={
                !input.trim() ||
                isLoading ||
                !selectedCandidate
              }
              aria-label="Send message"
            >
              ↑
            </button>

          </div>

          {/* Input Footer */}

          <div className="input-bottom">

            <span className="input-context">
              Answer based on your experience
            </span>

            <span className="enter-hint">
              Press Enter to send
            </span>

          </div>

        </footer>

      </main>

    </div>
  );
}

export default App;
