import { getAnalyses } from "./api.js";
import { escapeHtml } from "./render.js";

const root = document.getElementById("history-list");

async function loadHistory() {
  root.innerHTML = `<article class="card">Loading history...</article>`;

  try {
    const analyses = await getAnalyses();
    if (!analyses.length) {
      root.innerHTML = `<article class="card empty-state">No saved analyses yet.</article>`;
      return;
    }

    root.innerHTML = analyses
      .map(
        (item) => `
          <a class="card history-card" href="./detail.html?id=${item.id}">
            <p class="eyebrow">Analysis #${item.id}</p>
            <h3>${escapeHtml(item.idea)}</h3>
            <p>${escapeHtml(item.summary || "No summary available.")}</p>
            <div class="summary-meta">
              <span class="pill">Verdict: ${escapeHtml(item.verdict || "unknown")}</span>
              <span class="pill">Score: ${item.overall_score ?? "-"}</span>
              <span class="pill">Target: ${escapeHtml(item.target_user || "n/a")}</span>
            </div>
          </a>
        `,
      )
      .join("");
  } catch (error) {
    root.innerHTML = `<article class="card empty-state">${escapeHtml(error.message)}</article>`;
  }
}

loadHistory();
