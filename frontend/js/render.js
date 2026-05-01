export function renderBulletList(items = [], language = "en") {
  const ui = getUiText(language);
  if (!items.length) {
    return `<p class="empty-state">${escapeHtml(ui.noItems)}</p>`;
  }

  return `
    <ul class="bullet-list">
      ${items.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}
    </ul>
  `;
}

const UI_TEXT = {
  en: {
    analysisNumber: "Analysis",
    latestRun: "Latest Run",
    overallScore: "Overall Score",
    market: "Market",
    competition: "Competition",
    business: "Business",
    riskAdjusted: "Risk-Adjusted",
    scoreBreakdown: "Score Breakdown",
    whyTheseScores: "Why These Scores",
    positiveSignals: "Positive Signals",
    negativeSignals: "Negative Signals",
    rawWeighted: (raw, weighted) => `Raw ${raw} / Weighted ${weighted}`,
    weighted: (value) => `Weighted: ${value}`,
    noItems: "No items available.",
    noEvidence: "No evidence available for this section.",
    openSource: "Open source",
    similarity: (value) => `Similarity: ${value}`,
    verdict: (value, score) => `Verdict: ${value}${score !== undefined && score !== null ? ` · Score ${score}` : ""}`,
    submissionTitle: "Your Submission",
    fields: {
      idea: "Idea",
      target_user: "Target User",
      problem: "Problem",
      monetization: "Monetization",
      resources: "Resources",
      stage: "Stage",
      geography: "Geography",
      notes: "Notes",
      notProvided: "Not provided",
    },
    verdictLabels: {
      go: "Go",
      narrow: "Narrow",
      "no-go": "No-go",
    },
  },
  zh: {
    analysisNumber: "分析",
    latestRun: "最近一次",
    overallScore: "总分",
    market: "市场",
    competition: "竞争",
    business: "商业",
    riskAdjusted: "风险调整后",
    scoreBreakdown: "评分拆解",
    whyTheseScores: "评分原因",
    positiveSignals: "加分信号",
    negativeSignals: "减分信号",
    rawWeighted: (raw, weighted) => `原始分 ${raw} / 加权分 ${weighted}`,
    weighted: (value) => `加权: ${value}`,
    noItems: "暂无内容。",
    noEvidence: "该部分暂无证据。",
    openSource: "打开来源",
    similarity: (value) => `相似度: ${value}`,
    verdict: (value, score) => `结论: ${value}${score !== undefined && score !== null ? ` · 分数 ${score}` : ""}`,
    submissionTitle: "你的提交内容",
    fields: {
      idea: "创业想法",
      target_user: "目标用户",
      problem: "核心问题",
      monetization: "变现方式",
      resources: "现有资源",
      stage: "当前阶段",
      geography: "目标地区",
      notes: "补充说明",
      notProvided: "未填写",
    },
    verdictLabels: {
      go: "值得做",
      narrow: "建议缩小切口",
      "no-go": "暂不建议做",
    },
  },
};

function getUiText(language) {
  return UI_TEXT[language] || UI_TEXT.en;
}

export function renderSubmissionCard(input, language = "en") {
  const ui = getUiText(language);
  const fields = [
    [ui.fields.idea, input.idea],
    [ui.fields.target_user, input.target_user],
    [ui.fields.problem, input.problem],
    [ui.fields.monetization, input.monetization],
    [ui.fields.resources, input.resources],
    [ui.fields.stage, input.stage],
    [ui.fields.geography, input.geography],
    [ui.fields.notes, input.notes],
  ];

  return `
    <h3>${escapeHtml(ui.submissionTitle)}</h3>
    <div class="info-grid">
      ${fields
        .map(
          ([label, value]) => `
            <div class="info-item">
              <p class="eyebrow">${escapeHtml(label)}</p>
              <p>${escapeHtml(value || ui.fields.notProvided)}</p>
            </div>
          `,
        )
        .join("")}
    </div>
  `;
}

export function getPreferredLanguage() {
  return localStorage.getItem("ui-language") || "en";
}

export function setPreferredLanguage(language) {
  localStorage.setItem("ui-language", language);
}

export function getLocalizedReport(report, language) {
  if (!report.translations) {
    return {
      summary: report.summary,
      opportunities: report.opportunities,
      risks: report.risks,
      key_assumptions: report.key_assumptions,
      next_steps: report.next_steps,
      score_explanations: report.score_explanations,
    };
  }
  return report.translations[language] || report.translations.en;
}

export function renderSummaryCard(report, title = "Analysis Result", language = "en") {
  const ui = getUiText(language);
  const verdictClass = `verdict-${report.verdict}`;
  const verdictLabel = ui.verdictLabels[report.verdict] || report.verdict;
  return `
    <div class="summary-head">
      <div>
        <p class="eyebrow">${report.analysis_id ? `${ui.analysisNumber} #${report.analysis_id}` : ui.latestRun}</p>
        <h1>${escapeHtml(title)}</h1>
        <p class="lede">${escapeHtml(report.summary)}</p>
      </div>
      <div class="pill-stack">
        <span class="verdict-badge ${verdictClass}">${escapeHtml(verdictLabel)}</span>
      </div>
    </div>
    <div class="summary-meta">
      <span class="pill">${ui.overallScore}: ${report.overall_score}</span>
      <span class="pill">${ui.market}: ${report.score_breakdown.market}</span>
      <span class="pill">${ui.competition}: ${report.score_breakdown.competition}</span>
      <span class="pill">${ui.business}: ${report.score_breakdown.business}</span>
      <span class="pill">${ui.riskAdjusted}: ${report.score_breakdown.risk}</span>
    </div>
  `;
}

export function renderScoreCard(scoreBreakdown, language = "en") {
  const ui = getUiText(language);
  return `
    <h3>${escapeHtml(ui.scoreBreakdown)}</h3>
    <div class="score-grid">
      ${renderScoreTile(ui.market, scoreBreakdown.market, scoreBreakdown.weighted_market, language)}
      ${renderScoreTile(ui.competition, scoreBreakdown.competition, scoreBreakdown.weighted_competition, language)}
      ${renderScoreTile(ui.business, scoreBreakdown.business, scoreBreakdown.weighted_business, language)}
      ${renderScoreTile(language === "zh" ? "风险" : "Risk", scoreBreakdown.risk, scoreBreakdown.weighted_risk, language)}
    </div>
  `;
}

export function renderScoreExplanations(scoreExplanations, localizedTexts = null, language = "en") {
  const ui = getUiText(language);
  const items = [
    [ui.market, scoreExplanations.market, "market"],
    [ui.competition, scoreExplanations.competition, "competition"],
    [ui.business, scoreExplanations.business, "business"],
    [language === "zh" ? "风险" : "Risk", scoreExplanations.risk, "risk"],
  ];

  return `
    <h3>${escapeHtml(ui.whyTheseScores)}</h3>
    <div class="explanation-stack">
      ${items
        .map(
          ([label, item, key]) => {
            const localized = localizedTexts?.[key];
            return `
            <section class="explanation-item">
              <div class="explanation-head">
                <strong>${escapeHtml(label)}</strong>
                <span class="pill">${escapeHtml(ui.rawWeighted(item.score, item.weighted_score))}</span>
              </div>
              <p>${escapeHtml(localized?.rationale || item.rationale)}</p>
              <div class="explanation-columns">
                <div>
                  <p class="eyebrow">${escapeHtml(ui.positiveSignals)}</p>
                  ${renderBulletList(localized?.positive_signals || item.positive_signals, language)}
                </div>
                <div>
                  <p class="eyebrow">${escapeHtml(ui.negativeSignals)}</p>
                  ${renderBulletList(localized?.negative_signals || item.negative_signals, language)}
                </div>
              </div>
            </section>
          `;
          },
        )
        .join("")}
    </div>
  `;
}

export function renderEvidenceCard(title, items = [], language = "en") {
  const ui = getUiText(language);
  if (!items.length) {
    return `
      <h3>${escapeHtml(title)}</h3>
      <p class="empty-state">${escapeHtml(ui.noEvidence)}</p>
    `;
  }

  return `
    <h3>${escapeHtml(title)}</h3>
    <div class="evidence-list">
      ${items
        .map(
          (item) => `
            <article class="evidence-item">
              <strong>${escapeHtml(item.title || item.idea || "Untitled")}</strong>
              ${item.url ? `<p><a class="evidence-link" href="${escapeHtml(item.url)}" target="_blank" rel="noreferrer">${escapeHtml(ui.openSource)}</a></p>` : ""}
              ${item.similarity !== undefined ? `<p class="evidence-meta">${escapeHtml(ui.similarity(item.similarity))}</p>` : ""}
              ${item.verdict ? `<p class="evidence-meta">${escapeHtml(ui.verdict(item.verdict, item.overall_score))}</p>` : ""}
              <p>${escapeHtml(item.summary || "")}</p>
            </article>
          `,
        )
        .join("")}
    </div>
  `;
}

export function setupLanguageToggle(button, onChange) {
  let language = getPreferredLanguage();
  button.textContent = language === "en" ? "中文" : "EN";
  button.addEventListener("click", () => {
    language = language === "en" ? "zh" : "en";
    setPreferredLanguage(language);
    button.textContent = language === "en" ? "中文" : "EN";
    onChange(language);
  });
  return language;
}

function renderScoreTile(label, raw, weighted, language = "en") {
  const ui = getUiText(language);
  return `
    <div class="score-tile">
      <span>${escapeHtml(label)}</span>
      <strong>${raw}</strong>
      <small>${escapeHtml(ui.weighted(weighted))}</small>
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
