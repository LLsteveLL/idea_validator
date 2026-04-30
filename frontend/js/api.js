const API_BASE = "http://127.0.0.1:8000";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });

  if (!response.ok) {
    let message = `Request failed: ${response.status}`;
    try {
      const payload = await response.json();
      if (payload.detail) {
        message = payload.detail;
      }
    } catch (_) {
      // ignore parse failure
    }
    throw new Error(message);
  }

  return response.json();
}

export function analyzeIdea(payload) {
  return request("/analyze", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function getAnalyses() {
  return request("/analyses");
}

export function getAnalysisById(id) {
  return request(`/analyses/${id}`);
}
