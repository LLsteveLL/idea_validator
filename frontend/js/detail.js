import { getAnalysisById } from "./api.js";
import {
  escapeHtml,
  getQueryParam,
  renderBulletList,
  renderScoreCard,
  renderSummaryCard,
} from "./render.js";

const analysisId = getQueryParam("id");

if (!analysisId) {
  window.location.href = "./history.html";
}

const summaryNode = document.getElementById("detail-summary");
const inputNode = document.getElementById("detail-input-card");
const scoreNode = document.getElementById("detail-score-card");
const opportunitiesNode = document.getElementById("detail-opportunities-card");
const risksNode = document.getElementById("detail-risks-card");
const stepsNode = document.getElementById("detail-steps-card");

async function loadDetail() {
  summaryNode.innerHTML = "<p>Loading analysis detail...</p>";

  try {
    const detail = await getAnalysisById(analysisId);
    const report = detail.final_report;
    summaryNode.innerHTML = renderSummaryCard(report, detail.idea_input.idea || "Saved Analysis");
    inputNode.innerHTML = `
      <h3>Original Input</h3>
      <pre class="json-block">${escapeHtml(JSON.stringify(detail.idea_input, null, 2))}</pre>
    `;
    scoreNode.innerHTML = renderScoreCard(report.score_breakdown);
    opportunitiesNode.innerHTML = `
      <h3>Opportunities</h3>
      ${renderBulletList(report.opportunities)}
    `;
    risksNode.innerHTML = `
      <h3>Risks</h3>
      ${renderBulletList(report.risks)}
    `;
    stepsNode.innerHTML = `
      <h3>Next Steps</h3>
      ${renderBulletList(report.next_steps)}
      <h3>Key Assumptions</h3>
      ${renderBulletList(report.key_assumptions)}
    `;
  } catch (error) {
    summaryNode.innerHTML = `<p class="empty-state">${escapeHtml(error.message)}</p>`;
  }
}

loadDetail();
