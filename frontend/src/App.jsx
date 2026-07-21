import { useState } from "react";


const SAMPLE_APPLICATIONS = [
  { id: 1, company: "Acme Corp", position: "Backend Engineer", status: "Applied" },
  { id: 2, company: "Globex", position: "Frontend Developer", status: "Interview" },
  { id: 3, company: "Initech", position: "Full Stack Engineer", status: "Offer" },
];


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
  // function to change it (setApplications). We start it with our
  // placeholder data. When this state changes later, React
  // automatically re-renders the screen.
  const [applications, setApplications] = useState(SAMPLE_APPLICATIONS);

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
