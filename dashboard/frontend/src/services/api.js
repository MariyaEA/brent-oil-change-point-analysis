const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:5000/api";

async function fetchJson(path, options = {}) {
  const controller = new AbortController();
  const timeout = window.setTimeout(() => controller.abort(), 12000);

  try {
    const response = await fetch(`${API_BASE}${path}`, {
      ...options,
      signal: controller.signal,
      headers: {
        Accept: "application/json",
        ...(options.headers || {}),
      },
    });

    const payload = await response.json().catch(() => ({}));
    if (!response.ok) {
      throw new Error(payload.error || `Request failed with status ${response.status}`);
    }
    return payload;
  } catch (error) {
    if (error.name === "AbortError") {
      throw new Error("The API request timed out. Confirm the Flask server is running.");
    }
    throw error;
  } finally {
    window.clearTimeout(timeout);
  }
}

function queryString(params) {
  const search = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") {
      search.set(key, value);
    }
  });
  return `?${search.toString()}`;
}

export const api = {
  summary: () => fetchJson("/summary"),
  changePoints: () => fetchJson("/change-points"),
  prices: (params) => fetchJson(`/prices${queryString(params)}`),
  events: (params) => fetchJson(`/events${queryString(params)}`),
  correlations: (params) => fetchJson(`/event-correlations${queryString(params)}`),
};
