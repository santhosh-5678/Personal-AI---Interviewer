import { useEffect, useState } from "react";
import "./App.css";

import {
  startInterview,
  sendInterviewMessage,
} from "./services/api";


function App() {
  // =========================================
  // STATE
  // =========================================

  const [resumeFile, setResumeFile] = useState(null);
  const [showResumeUpload, setShowResumeUpload] = useState(false);

  const [theme, setTheme] = useState("light");

  const [candidate, setCandidate] = useState(null);

  const [messages, setMessages] = useState([]);

  const [message, setMessage] = useState("");

  const [sessionId, setSessionId] = useState(null);

  const [loading, setLoading] = useState(true);

  const [sending, setSending] = useState(false);

  const [error, setError] = useState("");

  // =========================================
  // HELPER
  // =========================================

  const checkForResumeStage = (reply) => {
    if (!reply) {
      return;
    }

    const text = reply.toLowerCase();

    const resumeKeywords = [
      "upload your resume",
      "upload your cv",
      "upload a resume",
      "upload a cv",
      "please upload your resume",
      "please upload your cv",
      "resume",
      "cv",
    ];

    const shouldShowUpload = resumeKeywords.some(
      (keyword) => text.includes(keyword)
    );

    if (shouldShowUpload) {
      setShowResumeUpload(true);
    }
  };


  // =========================================
  // LOAD CANDIDATE + START INTERVIEW
  // =========================================

  useEffect(() => {
    const initializeInterview = async () => {
      try {
        setLoading(true);
        setError("");

        // -------------------------------------
        // 1. Load candidates.json
        // -------------------------------------

        const candidateResponse = await fetch(
          "/data/candidates.json"
        );

        if (!candidateResponse.ok) {
          throw new Error(
            "Unable to load candidates.json"
          );
        }

        const candidateData =
          await candidateResponse.json();


        // -------------------------------------
        // 2. Select candidate
        // -------------------------------------

        const selectedCandidate =
          candidateData.candidates?.[0];


        if (!selectedCandidate) {
          throw new Error(
            "No candidate found in candidates.json"
          );
        }


        // -------------------------------------
        // 3. Store candidate
        // -------------------------------------

        setCandidate(selectedCandidate);


        // -------------------------------------
        // 4. Create session ID
        // -------------------------------------

        const newSessionId =
          crypto.randomUUID();

        setSessionId(newSessionId);


        // -------------------------------------
        // 5. Start interview
        // -------------------------------------

        const response =
          await startInterview(
            newSessionId,
            selectedCandidate
          );


        console.log(
          "Interview started:",
          response
        );


        // -------------------------------------
        // 6. Check resume stage
        // -------------------------------------

        checkForResumeStage(
          response.reply
        );


        // -------------------------------------
        // 7. Add AI message
        // -------------------------------------

        if (response.reply) {
          setMessages([
            {
              id: Date.now(),
              sender: "ai",
              text: response.reply,
            },
          ]);
        }

      } catch (error) {

        console.error(
          "Interview initialization failed:",
          error.response?.data ||
          error.message ||
          error
        );

        setError(
          "Unable to start the interview."
        );

      } finally {

        setLoading(false);

      }
    };


    initializeInterview();

  }, []);


  // =========================================
  // HANDLE SEND MESSAGE
  // =========================================

  const handleSend = async () => {

    // Do not send empty messages
    if (!message.trim()) {
      return;
    }


    // Session must exist
    if (!sessionId) {
      console.error(
        "Session ID is not available."
      );

      return;
    }


    // Prevent multiple requests
    if (sending) {
      return;
    }


    const userMessage =
      message.trim();


    // -------------------------------------
    // Show user message immediately
    // -------------------------------------

    setMessages(
      (previousMessages) => [
        ...previousMessages,

        {
          id: Date.now(),
          sender: "user",
          text: userMessage,
        },
      ]
    );


    // Clear input
    setMessage("");


    try {

      setSending(true);
      setError("");


      // -------------------------------------
      // Send message to backend
      // -------------------------------------

      const response =
        await sendInterviewMessage(
          sessionId,
          userMessage
        );


      console.log(
        "Interview response:",
        response
      );


      // -------------------------------------
      // Check if AI reached resume stage
      // -------------------------------------

      checkForResumeStage(
        response.reply
      );


      // -------------------------------------
      // Add AI response
      // -------------------------------------

      if (response.reply) {

        setMessages(
          (previousMessages) => [
            ...previousMessages,

            {
              id: Date.now() + 1,
              sender: "ai",
              text: response.reply,
            },
          ]
        );

      }

    } catch (error) {

      console.error(
        "Interview message failed:",
        error.response?.data ||
        error.message ||
        error
      );

      setError(
        "Unable to get a response from the interview agent."
      );

    } finally {

      setSending(false);

    }
  };


  // =========================================
  // HANDLE RESUME SELECTION
  // =========================================

  const handleResumeChange = (event) => {

    const file =
      event.target.files?.[0];


    if (!file) {
      return;
    }


    // Only PDF
    if (
      file.type !==
      "application/pdf"
    ) {

      setError(
        "Please upload a PDF resume."
      );

      setResumeFile(null);

      return;
    }


    // Optional size check
    const maxSize =
      10 * 1024 * 1024;


    if (file.size > maxSize) {

      setError(
        "Resume must be smaller than 10 MB."
      );

      setResumeFile(null);

      return;
    }


    setResumeFile(file);

    setError("");

    console.log(
      "Resume selected:",
      file.name
    );
  };


  // =========================================
  // LOADING SCREEN
  // =========================================

  if (loading) {

    return (
      <div
        className={`interview-app ${theme}`}
      >

        <div className="loading-screen">

          <div className="loading-spinner" />

          <p>
            Starting your interview...
          </p>

        </div>

      </div>
    );
  }


  // =========================================
  // MAIN UI
  // =========================================

  return (
    <div
      className={`interview-app ${theme}`}
    >

      {/* =====================================
          HEADER
      ====================================== */}

      <header className="topbar">

        {/* Candidate mini profile */}

        <div className="candidate-mini">

          <div className="candidate-avatar">

            {candidate?.member?.name
              ?.charAt(0)
              ?.toUpperCase() || "C"}

          </div>


          <div>

            <div className="candidate-name">

              {candidate?.member?.name ||
                "Candidate"}

            </div>


            <div className="candidate-status">

              Technical Interview

            </div>

          </div>

        </div>


        {/* Title */}

        <h1 className="app-title">

          AI Interview Agent

        </h1>


        {/* Theme */}

        <div className="topbar-actions">

          <button
            className="theme-toggle"
            onClick={() =>
              setTheme(
                theme === "light"
                  ? "dark"
                  : "light"
              )
            }
            aria-label="Toggle theme"
            title="Toggle theme"
          >

            {theme === "light"
              ? "☀"
              : "☾"}

          </button>

        </div>

      </header>


      {/* =====================================
          MAIN LAYOUT
      ====================================== */}

      <div className="main-layout">


        {/* ===================================
            SIDEBAR
        ==================================== */}

        <aside className="sidebar">

          {/* Profile */}

          <div className="profile-section">

            <div className="large-avatar">

              {candidate?.member?.name
                ?.charAt(0)
                ?.toUpperCase() || "C"}

            </div>


            <h2>

              {candidate?.member?.name ||
                "Candidate"}

            </h2>


            <span className="candidate-badge">

              Interview Candidate

            </span>

          </div>


          {/* Candidate Information */}

          <div className="candidate-info">


            {/* Role */}

            <div className="info-item">

              <span className="info-label">

                Role

              </span>


              <strong>

                {candidate?.member?.jobRole ||
                  "Not available"}

              </strong>

            </div>


            {/* Experience */}

            <div className="info-item">

              <span className="info-label">

                Experience

              </span>


              <strong>

                {candidate?.member
                  ?.yearsExperience ??
                  "Not available"}

                {candidate?.member
                  ?.yearsExperience !==
                  undefined &&
                  " years"}

              </strong>

            </div>


            {/* Education */}

            <div className="info-item">

              <span className="info-label">

                Education

              </span>


              <strong>

                {candidate?.member
                  ?.education ||
                  "Not available"}

              </strong>

            </div>


            {/* Status */}

            <div className="info-item">

              <span className="info-label">

                Status

              </span>


              <span className="status-active">

                ● In Progress

              </span>

            </div>

          </div>


          {/* =================================
              PROGRESS
          ================================== */}

          <div className="progress-section">

            <div className="progress-header">

              <span>

                Interview Progress

              </span>


              <strong>

                0 / 8

              </strong>

            </div>


            <div className="progress-bar">

              <div
                className="progress-fill"
                style={{
                  width: "0%",
                }}
              />

            </div>


            <p>

              Exactly 8 questions

            </p>

          </div>

        </aside>


        {/* ===================================
            CHAT SECTION
        ==================================== */}

        <section className="chat-section">


          {/* Chat Header */}

          <div className="chat-header">

            <div className="agent-avatar">

              AI

            </div>


            <div>

              <h2>

                Interview Agent

              </h2>


              <span>

                AI Technical Interview

              </span>

            </div>


            <div className="online-indicator">

              <span />

              Online

            </div>

          </div>


          {/* =================================
              CHAT MESSAGES
          ================================== */}

          <div className="chat-messages">

            <div className="messages-container">

              {messages.map((msg) => (

                <div
                  key={msg.id}
                  className={`chat-message ${msg.sender}`}
                >


                  {/* AI avatar */}

                  {msg.sender === "ai" && (

                    <div className="message-avatar">

                      AI

                    </div>

                  )}


                  {/* Message content */}

                  <div className="message-content">

                    {msg.sender === "ai" && (

                      <div className="message-name">

                        Interview Agent

                      </div>

                    )}


                    <div className="message-bubble">

                      {msg.text}

                    </div>

                  </div>


                  {/* User avatar */}

                  {msg.sender === "user" && (

                    <div className="message-avatar user-avatar">

                      You

                    </div>

                  )}

                </div>

              ))}


              {/* Thinking indicator */}

              {sending && (

                <div className="chat-message ai">

                  <div className="message-avatar">

                    AI

                  </div>


                  <div className="message-content">

                    <div className="message-name">

                      Interview Agent

                    </div>


                    <div className="message-bubble">

                      Thinking...

                    </div>

                  </div>

                </div>

              )}

            </div>

          </div>


          {/* =================================
              ERROR
          ================================== */}

          {error && (

            <div className="error-message">

              {error}

            </div>

          )}


          {/* =================================
              RESUME UPLOAD
          ================================== */}

          {showResumeUpload && (

            <div className="resume-upload-container">

              <label className="resume-upload-button">

                <span>
                  📄
                </span>

                Upload Resume


                <input
                  type="file"
                  accept=".pdf,application/pdf"
                  hidden
                  onChange={
                    handleResumeChange
                  }
                />

              </label>


              {/* Selected resume */}

              {resumeFile && (

                <div className="selected-resume">

                  <span className="resume-icon">

                    📄

                  </span>


                  <span className="resume-name">

                    {resumeFile.name}

                  </span>

                </div>

              )}

            </div>

          )}


          {/* =================================
              COMPOSER
          ================================== */}

          <div className="composer-area">

            <div className="composer">

              <input
                type="text"
                value={message}
                onChange={(e) =>
                  setMessage(e.target.value)
                }
                onKeyDown={(e) => {

                  if (
                    e.key === "Enter"
                  ) {

                    e.preventDefault();

                    handleSend();

                  }

                }}
                placeholder="Type your answer here..."
                disabled={sending}
              />


              <button
                className="send-button"
                onClick={handleSend}
                disabled={
                  !message.trim() ||
                  sending
                }
                aria-label="Send message"
              >

                ↑

              </button>

            </div>


            <p className="composer-hint">

              Press Enter to send

            </p>

          </div>

        </section>

      </div>


      {/* =====================================
          FOOTER
      ====================================== */}

      <footer className="footer">

        <span>

          AI Interview Agent

        </span>


        <span>

          Chat-based technical interview

        </span>


        <span>

          Session active

        </span>

      </footer>

    </div>
  );
}


export default App;