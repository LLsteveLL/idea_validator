import { analyzeIdea } from "./api.js";

const statusNode = document.getElementById("loading-status");
const rawPayload = localStorage.getItem("pending-analysis-payload");

if (!rawPayload) {
  window.location.href = "./index.html";
}

const payload = JSON.parse(rawPayload);

async function runAnalysis() {
  try {
    statusNode.textContent = "Calling the backend analysis workflow...";
    const report = await analyzeIdea(payload);
    localStorage.removeItem("pending-analysis-payload");
    localStorage.setItem("latest-analysis-report", JSON.stringify(report));

    if (report.analysis_id) {
      window.location.href = `./detail.html?id=${report.analysis_id}`;
      return;
    }

    window.location.href = "./result.html";
  } catch (error) {
    statusNode.textContent = error.message;
  }
}

runAnalysis();
