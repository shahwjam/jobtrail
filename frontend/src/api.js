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
    throw new Error(body?.detail ? JSON.stringify(body.detail) : `Request failed: ${response.status}`);
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

export async function generateCoverLetter(id, resumeText) {
  return postJson(`/applications/${id}/cover-letter`, { resume_text: resumeText });
}
