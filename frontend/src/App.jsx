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

  // Controls the form: null hides it, "new" opens it in create mode, and
  // an application object opens it pre-filled in edit mode.
  const [formTarget, setFormTarget] = useState(null);

  // useEffect with an empty dependency array ([]) runs once, right after
  // the component first mounts — a good place to kick off a data fetch.
  useEffect(() => {
    getApplications()
      .then(setApplications)
      .catch((error) => console.error("Failed to load applications:", error));
  }, []);

  function handleFormSubmit(values) {
    if (formTarget === "new") {
      createApplication(values)
        .then((created) => setApplications((previous) => [...previous, created]))
        .catch((error) => console.error("Failed to create application:", error));
    } else {
      updateApplication(formTarget.id, values)
        .then((updated) =>
          setApplications((previous) => previous.map((application) => (application.id === updated.id ? updated : application)))
        )
        .catch((error) => console.error("Failed to update application:", error));
    }
    setFormTarget(null);
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

      {formTarget && (
        <ApplicationForm
          initialValues={formTarget === "new" ? undefined : formTarget}
          onSubmit={handleFormSubmit}
          onCancel={() => setFormTarget(null)}
        />
      )}

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
    </div>
  );
}

export default App;
