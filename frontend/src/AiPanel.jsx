import { useState } from "react";
import { generateCoverLetter } from "./api";

const RESUME_STORAGE_KEY = "jobtrail.resume";

// The resume is remembered in this browser only, as a convenience so you
// don't re-paste it for every application. Storage can be blocked (private
// windows), so every access is wrapped — the panel works fine without it.
function loadSavedResume() {
  try {
    return localStorage.getItem(RESUME_STORAGE_KEY) ?? "";
  } catch {
    return "";
  }
}

function saveResume(text) {
  try {
    localStorage.setItem(RESUME_STORAGE_KEY, text);
  } catch {
    // Not fatal — the resume just won't be remembered next visit.
  }
}

// AI tools for one application: paste your resume once, then generate a
// tailored cover letter from the application's job description.
function AiPanel({ application, onClose }) {
  const [resumeText, setResumeText] = useState(loadSavedResume);
  const [coverLetter, setCoverLetter] = useState(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState(null);

  const hasJobDescription = Boolean(application.job_description);
  const resumeTooShort = resumeText.trim().length < 50;

  function handleResumeChange(event) {
    setResumeText(event.target.value);
    saveResume(event.target.value);
  }

  function handleGenerate() {
    setIsGenerating(true);
    setError(null);
    generateCoverLetter(application.id, resumeText)
      .then((data) => setCoverLetter(data.cover_letter))
      .catch((err) => setError(err.message))
      .finally(() => setIsGenerating(false));
  }

  return (
    <section className="ai-panel" aria-label={`AI tools for ${application.company}`}>
      <div className="ai-panel-header">
        <div>
          <h2>AI tools</h2>
          <p className="subtitle">
            {application.position} · {application.company}
          </p>
        </div>
        <button type="button" className="button-secondary" onClick={onClose}>
          Close
        </button>
      </div>

      {!hasJobDescription && (
        <p className="ai-hint">Edit this application and paste the job description first — the AI tailors everything to it.</p>
      )}

      <div className="form-field">
        <label htmlFor="resume_text">Your resume (plain text)</label>
        <textarea id="resume_text" rows={8} value={resumeText} onChange={handleResumeChange} />
        {resumeTooShort && <span className="ai-hint">At least 50 characters.</span>}
      </div>

      <div className="form-actions">
        <button
          type="button"
          className="button-primary"
          onClick={handleGenerate}
          disabled={isGenerating || !hasJobDescription || resumeTooShort}
        >
          {isGenerating ? "Writing…" : "Generate cover letter"}
        </button>
      </div>

      {error && (
        <div className="error-banner">
          <p>{error}</p>
        </div>
      )}

      {coverLetter && (
        <div className="ai-result">
          <div className="ai-result-header">
            <h3>Cover letter draft</h3>
            <button type="button" className="button-secondary" onClick={() => navigator.clipboard?.writeText(coverLetter)}>
              Copy
            </button>
          </div>
          <p className="cover-letter">{coverLetter}</p>
        </div>
      )}
    </section>
  );
}

export default AiPanel;
