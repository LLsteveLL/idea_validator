import { getAnalysisById } from "./api.js";
import {
  escapeHtml,
  getLocalizedReport,
  getPreferredLanguage,
  getQueryParam,
  renderBulletList,
  renderEvidenceCard,
  renderScoreCard,
  renderScoreExplanations,
  renderSubmissionCard,
  renderSummaryCard,
  setupLanguageToggle,
} from "./render.js";

const analysisId = getQueryParam("id");

if (!analysisId) {
  window.location.href = "./history.html";
}

const summaryNode = document.getElementById("detail-summary");
const inputNode = document.getElementById("detail-input-card");
const scoreNode = document.getElementById("detail-score-card");
const scoreExplanationsNode = document.getElementById("detail-score-explanations-card");
const opportunitiesNode = document.getElementById("detail-opportunities-card");
const risksNode = document.getElementById("detail-risks-card");
const stepsNode = document.getElementById("detail-steps-card");
const marketEvidenceNode = document.getElementById("detail-market-evidence-card");
const competitorEvidenceNode = document.getElementById("detail-competitor-evidence-card");
const similarAnalysesNode = document.getElementById("detail-similar-analyses-card");
const toggle = document.getElementById("language-toggle");

async function loadDetail() {
  summaryNode.innerHTML = "<p>Loading analysis detail...</p>";

  try {
    const detail = await getAnalysisById(analysisId);
    const report = detail.final_report;
    function render(language) {
      const localized = getLocalizedReport(report, language);
      summaryNode.innerHTML = renderSummaryCard(
        {
          ...report,
          summary: localized.summary,
        },
        detail.idea_input.idea || (language === "zh" ? "已保存分析" : "Saved Analysis"),
        language,
      );
      inputNode.innerHTML = renderSubmissionCard(detail.idea_input, language);
      scoreNode.innerHTML = renderScoreCard(report.score_breakdown, language);
      scoreExplanationsNode.innerHTML = renderScoreExplanations(
        report.score_explanations,
        localized.score_explanations,
        language,
      );
      opportunitiesNode.innerHTML = `
        <h3>${language === "zh" ? "机会点" : "Opportunities"}</h3>
        ${renderBulletList(localized.opportunities, language)}
      `;
      risksNode.innerHTML = `
        <h3>${language === "zh" ? "风险" : "Risks"}</h3>
        ${renderBulletList(localized.risks, language)}
      `;
      stepsNode.innerHTML = `
        <h3>${language === "zh" ? "下一步动作" : "Next Steps"}</h3>
        ${renderBulletList(localized.next_steps, language)}
        <h3>${language === "zh" ? "关键假设" : "Key Assumptions"}</h3>
        ${renderBulletList(localized.key_assumptions, language)}
      `;
      marketEvidenceNode.innerHTML = renderEvidenceCard(
        language === "zh" ? "市场证据" : "Market Evidence",
        report.evidence?.market_search || [],
        language,
      );
      competitorEvidenceNode.innerHTML = renderEvidenceCard(
        language === "zh" ? "竞品证据" : "Competitor Evidence",
        report.evidence?.competitor_search || [],
        language,
      );
      similarAnalysesNode.innerHTML = renderEvidenceCard(
        language === "zh" ? "相似历史分析" : "Similar Historical Analyses",
        report.evidence?.similar_analyses || [],
        language,
      );
    }

    const initialLanguage = setupLanguageToggle(toggle, render);
    render(getPreferredLanguage() || initialLanguage);
  } catch (error) {
    summaryNode.innerHTML = `<p class="empty-state">${escapeHtml(error.message)}</p>`;
  }
}

loadDetail();
