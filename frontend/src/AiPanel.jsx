import { useEffect, useState } from "react";
import { generateCoverLetter, getResumeMatch, scoreResumeMatch } from "./api";
import { scoreBand } from "./score";

const RESUME_STORAGE_KEY = "jobtrail.resume";

// Must match the tone presets in backend/prompts.py
const TONES = [
  { value: "professional", label: "Professional" },
  { value: "enthusiastic", label: "Enthusiastic" },
  { value: "concise", label: "Concise" },
];

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

function KeywordList({ title, keywords, variant }) {
  if (keywords.length === 0) return null;
  return (
    <div className="keyword-group">
      <h4>{title}</h4>
      <ul className="keyword-list">
        {keywords.map((keyword) => (
          <li key={keyword} className={`keyword keyword-${variant}`}>
            {keyword}
          </li>
        ))}
      </ul>
    </div>
  );
}

// AI tools for one application: paste your resume once, then generate a
// tailored cover letter or a keyword match score from the job description.
function AiPanel({ application, onClose, onMatchScored }) {
  const [resumeText, setResumeText] = useState(loadSavedResume);
  const [tone, setTone] = useState("professional");
  const [coverLetter, setCoverLetter] = useState(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState(null);

  const [match, setMatch] = useState(null);
  const [isScoring, setIsScoring] = useState(false);

  // Show the last saved score (if any) as soon as the panel opens.
  useEffect(() => {
    getResumeMatch(application.id)
      .then(setMatch)
      .catch(() => {}); // no saved score is fine — the user can run one
  }, [application.id]);

  const hasJobDescription = Boolean(application.job_description);
  const resumeTooShort = resumeText.trim().length < 50;

  function handleResumeChange(event) {
    setResumeText(event.target.value);
    saveResume(event.target.value);
  }

  function handleGenerate() {
    setIsGenerating(true);
    setError(null);
    generateCoverLetter(application.id, resumeText, tone)
      .then((data) => setCoverLetter(data.cover_letter))
      .catch((err) => setError(err.message))
      .finally(() => setIsGenerating(false));
  }

  function handleScore() {
    setIsScoring(true);
    setError(null);
    scoreResumeMatch(application.id, resumeText)
      .then((data) => {
        setMatch(data);
        onMatchScored(application.id, data.score);
      })
      .catch((err) => setError(err.message))
      .finally(() => setIsScoring(false));
  }

  const isBusy = isGenerating || isScoring;
  const cannotRun = !hasJobDescription || resumeTooShort;

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
        <select aria-label="Cover letter tone" className="ai-tone" value={tone} onChange={(event) => setTone(event.target.value)}>
          {TONES.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
        <button
          type="button"
          className="button-primary"
          onClick={handleGenerate}
          disabled={isBusy || cannotRun}
        >
          {isGenerating ? "Writing…" : "Generate cover letter"}
        </button>
        <button type="button" className="button-primary" onClick={handleScore} disabled={isBusy || cannotRun}>
          {isScoring ? "Scoring…" : "Score resume match"}
        </button>
      </div>

      {error && (
        <div className="error-banner">
          <p>{error}</p>
        </div>
      )}

      {match && (
        <div className="ai-result">
          <div className="ai-result-header">
            <h3>Resume match</h3>
            <span className={`score-badge score-${scoreBand(match.score)}`}>{match.score}/100</span>
          </div>
          <div
            className="score-meter"
            role="meter"
            aria-label="Resume match score"
            aria-valuemin={0}
            aria-valuemax={100}
            aria-valuenow={match.score}
          >
            <div className={`score-meter-fill score-${scoreBand(match.score)}`} style={{ width: `${match.score}%` }} />
          </div>
          {match.summary && <p className="match-summary">{match.summary}</p>}
          <KeywordList title="Matched" keywords={match.matched_keywords} variant="matched" />
          <KeywordList title="Missing" keywords={match.missing_keywords} variant="missing" />
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
