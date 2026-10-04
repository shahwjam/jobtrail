// Talks to the FastAPI backend. Plain fetch — no axios, it's already built
// into the browser and covers everything this app needs.
//
// VITE_API_URL is baked in at build time (Vite replaces import.meta.env.*
// when it bundles), so the Docker/cloud build can point at the real API.
const API_BASE_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

// Fetch never rejects on a 4xx/5xx response, so we have to check
// response.ok ourselves and throw — that's what lets callers use try/catch.
async function handleResponse(response) {
  if (!response.ok) {
    const body = await response.json().catch(() => null);
    // FastAPI sends a plain string for our own errors (404, 429...) and a
    // list of field errors for 422 validation failures.
    const detail = body?.detail;
    const message = typeof detail === "string" ? detail : detail ? JSON.stringify(detail) : null;
    throw new Error(message ?? `Request failed: ${response.status}`);
  }
  return response.json();
}

// All the JSON POSTs share the same shape.
async function postJson(path, body) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  return handleResponse(response);
}

export async function getApplications() {
  const response = await fetch(`${API_BASE_URL}/applications`);
  return handleResponse(response);
}

export async function createApplication(application) {
  const response = await fetch(`${API_BASE_URL}/applications`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(application),
  });
  return handleResponse(response);
}

export async function updateApplication(id, application) {
  const response = await fetch(`${API_BASE_URL}/applications/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(application),
  });
  return handleResponse(response);
}

export async function generateCoverLetter(id, resumeText, tone) {
  return postJson(`/applications/${id}/cover-letter`, { resume_text: resumeText, tone });
}

export async function scoreResumeMatch(id, resumeText) {
  return postJson(`/applications/${id}/match-score`, { resume_text: resumeText });
}

// Resolves to null (not an error) when no score has been run yet.
export async function getResumeMatch(id) {
  const response = await fetch(`${API_BASE_URL}/applications/${id}/match-score`);
  if (response.status === 404) return null;
  return handleResponse(response);
}
