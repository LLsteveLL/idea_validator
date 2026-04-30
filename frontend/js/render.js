export function renderBulletList(items = []) {
  if (!items.length) {
    return `<p class="empty-state">No items available.</p>`;
  }

  return `
    <ul class="bullet-list">
      ${items.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}
    </ul>
  `;
}

export function renderSummaryCard(report, title = "Analysis Result") {
  const verdictClass = `verdict-${report.verdict}`;
  return `
    <div class="summary-head">
      <div>
        <p class="eyebrow">${report.analysis_id ? `Analysis #${report.analysis_id}` : "Latest Run"}</p>
        <h1>${escapeHtml(title)}</h1>
        <p class="lede">${escapeHtml(report.summary)}</p>
      </div>
      <div class="pill-stack">
        <span class="verdict-badge ${verdictClass}">${escapeHtml(report.verdict)}</span>
      </div>
    </div>
    <div class="summary-meta">
      <span class="pill">Overall Score: ${report.overall_score}</span>
      <span class="pill">Market: ${report.score_breakdown.market}</span>
      <span class="pill">Competition: ${report.score_breakdown.competition}</span>
      <span class="pill">Business: ${report.score_breakdown.business}</span>
      <span class="pill">Risk-Adjusted: ${report.score_breakdown.risk}</span>
    </div>
  `;
}

export function renderScoreCard(scoreBreakdown) {
  return `
    <h3>Score Breakdown</h3>
    <div class="score-grid">
      ${renderScoreTile("Market", scoreBreakdown.market, scoreBreakdown.weighted_market)}
      ${renderScoreTile("Competition", scoreBreakdown.competition, scoreBreakdown.weighted_competition)}
      ${renderScoreTile("Business", scoreBreakdown.business, scoreBreakdown.weighted_business)}
      ${renderScoreTile("Risk", scoreBreakdown.risk, scoreBreakdown.weighted_risk)}
    </div>
  `;
}

function renderScoreTile(label, raw, weighted) {
  return `
    <div class="score-tile">
      <span>${escapeHtml(label)}</span>
      <strong>${raw}</strong>
      <small>Weighted: ${weighted}</small>
    </div>
  `;
}

export function getQueryParam(name) {
  return new URLSearchParams(window.location.search).get(name);
}

export function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}
