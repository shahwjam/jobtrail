import { useEffect, useState } from "react";
import { createApplication, getApplications, updateApplication } from "./api";
import AiPanel from "./AiPanel";
import ApplicationForm from "./ApplicationForm";
import { scoreBand } from "./score";
import "./App.css";


function ApplicationCard({ application, onEdit, onOpenAi }) {
  return (
    <div className="card">
      <div className="card-title">
        <h3>{application.company}</h3>
        {application.match_score != null && (
          <span className={`score-badge score-${scoreBand(application.match_score)}`} title="Resume match score">
            {application.match_score}
          </span>
        )}
      </div>
      <p>{application.position}</p>
      <div className="card-actions">
        <button type="button" className="card-edit" onClick={() => onEdit(application)}>
          Edit
        </button>
        <button type="button" className="card-edit" onClick={() => onOpenAi(application)}>
          AI tools
        </button>
      </div>
    </div>
  );
}

// The pipeline stages, left to right — Rejected sits at the end since it's
// a dead end rather than a step forward.
const PIPELINE_STATUSES = ["Applied", "Interview", "Offer", "Rejected"];

// Buckets applications by status so each pipeline column can render just
// its own cards.
function groupByStatus(applications) {
  const groups = Object.fromEntries(PIPELINE_STATUSES.map((status) => [status, []]));
  for (const application of applications) {
    groups[application.status]?.push(application);
  }
  return groups;
}

// === The dashboard page ===

function App() {
  // useState gives us: the current value (applications) and a
  // function to change it (setApplications). We start empty and fill it
  // in once the backend responds. When this state changes later, React
  // automatically re-renders the screen.
  const [applications, setApplications] = useState([]);

  // Tracks the initial GET /applications call, so we can show a loading
  // message instead of briefly flashing "0 applications", and an error
  // with a retry button if the backend is unreachable.
  const [isLoading, setIsLoading] = useState(true);
  const [loadError, setLoadError] = useState(null);

  // Surfaces a create/update failure (e.g. the API is down) without
  // crashing the page — the form stays open so the user can retry.
  const [actionError, setActionError] = useState(null);

  // Controls the form: null hides it, "new" opens it in create mode, and
  // an application object opens it pre-filled in edit mode.
  const [formTarget, setFormTarget] = useState(null);

  // The application whose AI panel is open (stored by id so the panel
  // always reads the latest version after an edit), or null.
  const [aiTargetId, setAiTargetId] = useState(null);
  const aiTarget = applications.find((application) => application.id === aiTargetId);

  // Only the .then/.catch/.finally callbacks call setState here — none of
  // it runs synchronously, so this is safe to call directly from an effect.
  function fetchApplications() {
    return getApplications()
      .then((data) => {
        setApplications(data);
        setLoadError(null);
      })
      .catch((error) => setLoadError(error.message))
      .finally(() => setIsLoading(false));
  }

  // useEffect with an empty dependency array ([]) runs once, right after
  // the component first mounts — a good place to kick off a data fetch.
  useEffect(() => {
    fetchApplications();
  }, []);

  // The retry button re-arms the loading/error state itself (from an
  // event handler, not an effect) before kicking off the fetch again.
  function handleRetry() {
    setIsLoading(true);
    setLoadError(null);
    fetchApplications();
  }

  function handleFormSubmit(values) {
    setActionError(null);
    const savedApplication =
      formTarget === "new" ? createApplication(values) : updateApplication(formTarget.id, values);

    savedApplication
      .then((saved) => {
        setApplications((previous) =>
          formTarget === "new"
            ? [...previous, saved]
            : previous.map((application) => (application.id === saved.id ? saved : application))
        );
        setFormTarget(null);
      })
      .catch((error) => setActionError(error.message));
  }

  // Keeps the badge on the card in sync after a new score, without refetching.
  function handleMatchScored(applicationId, score) {
    setApplications((previous) =>
      previous.map((application) =>
        application.id === applicationId ? { ...application, match_score: score } : application
      )
    );
  }

  const groupedApplications = groupByStatus(applications);

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <div>
          <h1>JobTrail</h1>
          <p className="subtitle">{applications.length} applications</p>
        </div>
        <button type="button" className="button-primary" onClick={() => setFormTarget("new")}>
          + Add Application
        </button>
      </div>

      {actionError && (
        <div className="error-banner">
          <p>Couldn't save that application: {actionError}</p>
          <button type="button" className="button-secondary" onClick={() => setActionError(null)}>
            Dismiss
          </button>
        </div>
      )}

      {formTarget && (
        <ApplicationForm
          // A new key remounts the form, so switching from editing one
          // application to another resets its fields instead of keeping stale ones.
          key={formTarget === "new" ? "new" : formTarget.id}
          initialValues={formTarget === "new" ? undefined : formTarget}
          onSubmit={handleFormSubmit}
          onCancel={() => setFormTarget(null)}
        />
      )}

      {aiTarget && (
        <AiPanel
          key={aiTarget.id}
          application={aiTarget}
          onClose={() => setAiTargetId(null)}
          onMatchScored={handleMatchScored}
        />
      )}

      {isLoading && <p className="status-message">Loading applications…</p>}

      {!isLoading && loadError && (
        <div className="error-banner">
          <p>Couldn't load applications: {loadError}</p>
          <button type="button" className="button-secondary" onClick={handleRetry}>
            Retry
          </button>
        </div>
      )}

      {!isLoading && !loadError && (
        <div className="pipeline">
          {/* One column per status — editing an application's status (via
              the form above) moves its card into a different column. */}
          {PIPELINE_STATUSES.map((status) => (
            <div key={status} className="pipeline-column">
              <div className="pipeline-column-header" data-status={status}>
                <h2>{status}</h2>
                <span className="pipeline-count">{groupedApplications[status].length}</span>
              </div>
              {groupedApplications[status].map((application) => (
                <ApplicationCard
                  key={application.id}
                  application={application}
                  onEdit={setFormTarget}
                  onOpenAi={(target) => setAiTargetId(target.id)}
                />
              ))}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default App;
