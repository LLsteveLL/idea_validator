import {
  getLocalizedReport,
  getPreferredLanguage,
  renderBulletList,
  renderEvidenceCard,
  renderScoreCard,
  renderScoreExplanations,
  renderSummaryCard,
  setupLanguageToggle,
} from "./render.js";

const raw = localStorage.getItem("latest-analysis-report");

if (!raw) {
  window.location.href = "./index.html";
}

const report = JSON.parse(raw);

function render(language) {
  const localized = getLocalizedReport(report, language);
  document.getElementById("result-summary").innerHTML = renderSummaryCard(
    {
      ...report,
      summary: localized.summary,
    },
    language === "zh" ? "分析结果" : "Analysis Result",
    language,
  );
  document.getElementById("score-card").innerHTML = renderScoreCard(report.score_breakdown, language);
  document.getElementById("score-explanations-card").innerHTML = renderScoreExplanations(
    report.score_explanations,
    localized.score_explanations,
    language,
  );
  document.getElementById("opportunities-card").innerHTML = `
    <h3>${language === "zh" ? "机会点" : "Opportunities"}</h3>
    ${renderBulletList(localized.opportunities, language)}
  `;
  document.getElementById("risks-card").innerHTML = `
    <h3>${language === "zh" ? "风险" : "Risks"}</h3>
    ${renderBulletList(localized.risks, language)}
  `;
  document.getElementById("assumptions-card").innerHTML = `
    <h3>${language === "zh" ? "关键假设" : "Key Assumptions"}</h3>
    ${renderBulletList(localized.key_assumptions, language)}
  `;
  document.getElementById("next-steps-card").innerHTML = `
    <h3>${language === "zh" ? "下一步动作" : "Next Steps"}</h3>
    ${renderBulletList(localized.next_steps, language)}
  `;
  document.getElementById("market-evidence-card").innerHTML = renderEvidenceCard(
    language === "zh" ? "市场证据" : "Market Evidence",
    report.evidence?.market_search || [],
    language,
  );
  document.getElementById("competitor-evidence-card").innerHTML = renderEvidenceCard(
    language === "zh" ? "竞品证据" : "Competitor Evidence",
    report.evidence?.competitor_search || [],
    language,
  );
  document.getElementById("similar-analyses-card").innerHTML = renderEvidenceCard(
    language === "zh" ? "相似历史分析" : "Similar Historical Analyses",
    report.evidence?.similar_analyses || [],
    language,
  );
}

const toggle = document.getElementById("language-toggle");
const initialLanguage = setupLanguageToggle(toggle, render);
render(getPreferredLanguage() || initialLanguage);
