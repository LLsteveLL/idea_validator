import { analyzeIdea } from "./api.js";

const form = document.getElementById("idea-form");
const panels = Array.from(document.querySelectorAll(".wizard-panel"));
const stepLabel = document.getElementById("wizard-step-label");
const questionNode = document.getElementById("wizard-question");
const hintNode = document.getElementById("wizard-hint");
const exampleNode = document.getElementById("wizard-example");
const progressBar = document.getElementById("progress-bar");
const backButton = document.getElementById("back-button");
const nextButton = document.getElementById("next-button");
const submitButton = document.getElementById("submit-button");
const statusNode = document.getElementById("form-status");
const reviewList = document.getElementById("review-list");

const steps = [
  {
    field: "idea",
    question: "What exactly are you trying to build?",
    hint: "Describe the product or service in one simple sentence.",
    example: "Example: An AI fitness coach app for busy office workers.",
    required: true,
  },
  {
    field: "target_user",
    question: "Who is this for?",
    hint: "Name the most specific user group you want to serve first.",
    example: "Example: Busy office workers who want to stay fit but lack routine.",
    required: true,
  },
  {
    field: "problem",
    question: "What painful problem are they dealing with?",
    hint: "Focus on a real frustration, not a feature request.",
    example: "Example: They do not know how to plan workouts or stay consistent.",
    required: true,
  },
  {
    field: "monetization",
    question: "How do you expect this to make money?",
    hint: "Subscription, one-time payment, usage pricing, service fee, or leave it blank.",
    example: "Example: Monthly subscription with a free 7-day trial.",
    required: false,
  },
  {
    field: "resources",
    question: "What resources do you already have?",
    hint: "Mention technical skill, domain knowledge, audience, or distribution advantages.",
    example: "Example: Product design skills, AI engineering ability, and app-building experience.",
    required: false,
  },
  {
    field: "stage",
    question: "What stage are you in right now?",
    hint: "For example: idea, prototype, early users.",
    example: "Example: Idea.",
    required: false,
  },
  {
    field: "geography",
    question: "Which market are you targeting first?",
    hint: "Examples: US, China, Southeast Asia, Global.",
    example: "Example: US.",
    required: false,
  },
  {
    field: "notes",
    question: "Anything else the analysis should know?",
    hint: "Optional. Add nuance, constraints, assumptions, or context.",
    example: "Example: The first version focuses on short home workouts and habit consistency.",
    required: false,
  },
  {
    field: "review",
    question: "Review your answers before analysis",
    hint: "Make sure the core positioning is clear before running the workflow.",
    example: "Tip: Tighter answers usually produce better analysis quality.",
    required: false,
  },
];

let currentStep = 0;

function getField(stepIndex) {
  return form.elements[steps[stepIndex].field];
}

function validateStep(stepIndex) {
  const step = steps[stepIndex];
  if (step.field === "review") {
    return true;
  }
  const field = getField(stepIndex);
  if (!step.required) {
    return true;
  }

  const value = String(field.value || "").trim();
  if (!value) {
    statusNode.textContent = "Please complete this field before continuing.";
    field.focus();
    return false;
  }

  statusNode.textContent = "";
  return true;
}

function buildPayload() {
  const formData = new FormData(form);
  return Object.fromEntries(formData.entries());
}

function renderReview(payload) {
  reviewList.innerHTML = steps
    .filter((step) => !["review"].includes(step.field))
    .map((step) => {
      const value = String(payload[step.field] || "").trim() || "Not provided";
      return `
        <article class="review-item">
          <p class="eyebrow">${step.field.replaceAll("_", " ")}</p>
          <p>${value}</p>
        </article>
      `;
    })
    .join("");
}

function renderStep() {
  const step = steps[currentStep];
  panels.forEach((panel, index) => {
    panel.classList.toggle("active", index === currentStep);
  });

  stepLabel.textContent = `Step ${currentStep + 1} of ${steps.length}`;
  questionNode.textContent = step.question;
  hintNode.textContent = step.hint;
  exampleNode.textContent = step.example;
  progressBar.style.width = `${((currentStep + 1) / steps.length) * 100}%`;

  backButton.disabled = currentStep === 0;
  nextButton.classList.toggle("hidden", currentStep === steps.length - 1);
  submitButton.classList.toggle("hidden", currentStep !== steps.length - 1);

  if (step.field === "review") {
    renderReview(buildPayload());
  } else {
    getField(currentStep).focus();
  }
}

backButton.addEventListener("click", () => {
  if (currentStep === 0) {
    return;
  }
  currentStep -= 1;
  statusNode.textContent = "";
  renderStep();
});

nextButton.addEventListener("click", () => {
  if (!validateStep(currentStep)) {
    return;
  }
  currentStep += 1;
  renderStep();
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (!validateStep(currentStep)) {
    return;
  }
  const payload = buildPayload();
  localStorage.setItem("pending-analysis-payload", JSON.stringify(payload));
  statusNode.textContent = "Opening analysis workflow...";
  window.location.href = "./loading.html";
});

renderStep();
