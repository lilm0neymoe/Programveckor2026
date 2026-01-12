const sidebar = document.getElementById("sidebar");
const toggleContainer = document.getElementById("toggleContainer");

function toggleSidebar() {
  sidebar.classList.toggle("hidden");
  if (sidebar.classList.contains("hidden")) {
    toggleContainer.style.left = "12px";
  } else {
    toggleContainer.style.left = sidebar.offsetWidth + "px";
  }
}

toggleContainer.style.left = "12px";

const sendBtn = document.getElementById("sendBtn");
const textInput = document.getElementById("userInput");
const actionSelect = document.getElementById("actionSelect");
const outputBar = document.getElementById("outputBar");

sendBtn.addEventListener("click", solveProblem);

async function solveProblem() {
  const input = textInput.value.trim();
  const action = actionSelect.value;

  if (!input) {
    outputBar.textContent = "Skriv något först!";
    return;
  }

  const mode = (action === "forenkla") ? "simplify" : "solve";

  try {
    const response = await fetch("/solve", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ input, mode, variable: "x" })
    });

    const data = await response.json();

    if (!response.ok) {
      outputBar.textContent = data?.detail ?? "Något gick fel.";
      return;
    }

    let html = "";
    if (data.steps?.length) {
      for (const step of data.steps) {
        html += `
          <div class="step">
            <p><strong>Steg ${step.step_number}: ${step.operation}</strong></p>
            <p><em>${step.reason}</em></p>
            <p>Före: ${step.before}</p>
            <p>Efter: ${step.after}</p>
          </div>
        `;
      }
    }
    html += `<div class="final"><strong>Svar:</strong> ${data.final_answer}</div>`;

    outputBar.innerHTML = html;
    textInput.value = "";
  } catch (e) {
    outputBar.textContent = "Kunde inte nå servern. Är FastAPI igång?";
  }
}
