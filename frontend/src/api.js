// Talks to the FastAPI backend. Plain fetch — no axios, the backend only
// needs two calls right now and fetch is already built into the browser.
const API_BASE_URL = "http://localhost:8000";

// Fetch never rejects on a 4xx/5xx response, so we have to check
// response.ok ourselves and throw — that's what lets callers use try/catch.
async function handleResponse(response) {
  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new Error(body?.detail ? JSON.stringify(body.detail) : `Request failed: ${response.status}`);
  }
  return response.json();
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
