import { renderBulletList, renderScoreCard, renderSummaryCard } from "./render.js";

const raw = localStorage.getItem("latest-analysis-report");

if (!raw) {
  window.location.href = "./index.html";
}

const report = JSON.parse(raw);

document.getElementById("result-summary").innerHTML = renderSummaryCard(report);
document.getElementById("score-card").innerHTML = renderScoreCard(report.score_breakdown);
document.getElementById("opportunities-card").innerHTML = `
  <h3>Opportunities</h3>
  ${renderBulletList(report.opportunities)}
`;
document.getElementById("risks-card").innerHTML = `
  <h3>Risks</h3>
  ${renderBulletList(report.risks)}
`;
document.getElementById("assumptions-card").innerHTML = `
  <h3>Key Assumptions</h3>
  ${renderBulletList(report.key_assumptions)}
`;
document.getElementById("next-steps-card").innerHTML = `
  <h3>Next Steps</h3>
  ${renderBulletList(report.next_steps)}
`;
