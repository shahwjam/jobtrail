import { useEffect, useState } from "react";
import { getApplications } from "./api";


function ApplicationCard({ application }) {
  return (
    <div className="card">
      <h3>{application.company}</h3>
      <p>{application.position}</p>
      <span className="status">{application.status}</span>
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

  // useEffect with an empty dependency array ([]) runs once, right after
  // the component first mounts — a good place to kick off a data fetch.
  useEffect(() => {
    getApplications()
      .then(setApplications)
      .catch((error) => console.error("Failed to load applications:", error));
  }, []);

  return (
    <div className="dashboard">
      <h1>JobTrail</h1>
      <p className="subtitle">{applications.length} applications</p>

      <div className="card-list">
        {/* Take the array and turn EACH application into a card.
            .map() is how React renders lists. The "key" helps React
            track each item — always give it a unique id. */}
        {applications.map((application) => (
          <ApplicationCard key={application.id} application={application} />
        ))}
      </div>
    </div>
  );
}

export default App;
