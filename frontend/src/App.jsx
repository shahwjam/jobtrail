import { useEffect, useState } from "react";
import { createApplication, getApplications, updateApplication } from "./api";
import ApplicationForm from "./ApplicationForm";
import "./App.css";


function ApplicationCard({ application, onEdit }) {
  return (
    <div className="card">
      <h3>{application.company}</h3>
      <p>{application.position}</p>
      <button type="button" className="card-edit" onClick={() => onEdit(application)}>
        Edit
      </button>
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
          initialValues={formTarget === "new" ? undefined : formTarget}
          onSubmit={handleFormSubmit}
          onCancel={() => setFormTarget(null)}
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
                <ApplicationCard key={application.id} application={application} onEdit={setFormTarget} />
              ))}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default App;
