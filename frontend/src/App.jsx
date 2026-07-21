import { useEffect, useState } from "react";
import { createApplication, getApplications, updateApplication } from "./api";
import ApplicationForm from "./ApplicationForm";
import "./App.css";


function ApplicationCard({ application, onEdit }) {
  return (
    <div className="card">
      <h3>{application.company}</h3>
      <p>{application.position}</p>
      <span className="status">{application.status}</span>
      <button type="button" className="card-edit" onClick={() => onEdit(application)}>
        Edit
      </button>
    </div>
  );
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

      <div className="card-list">
        {/* Take the array and turn EACH application into a card.
            .map() is how React renders lists. The "key" helps React
            track each item — always give it a unique id. */}
        {applications.map((application) => (
          <ApplicationCard key={application.id} application={application} onEdit={setFormTarget} />
        ))}
      </div>
    </div>
  );
}

export default App;
