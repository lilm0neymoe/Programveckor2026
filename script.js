console.log("script.js laddades!");

function renderLatex(el, latex, displayMode = true) {
  const s = (latex ?? "").toString().trim();
  if (!s) { el.textContent = ""; return; }

  try {
    katex.render(s, el, {
      displayMode,
      throwOnError: false,
      strict: "ignore"
    });
  } catch (e) {
    el.textContent = s; // fallback
  }
}


const sidebar = document.getElementById("sidebar");
const toggleContainer = document.getElementById("toggleContainer");
const toggleBtn = document.getElementById("toggleBtn");
toggleBtn.addEventListener("click", toggleSidebar);

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
  console.log("Klickade Skicka");
  console.log("katex är:", window.katex);
  if (!window.katex) {
    outputBar.textContent = "KaTeX är INTE laddat. Lägg in katex.min.js + katex.min.css i index.html.";
    return;
  }
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


outputBar.innerHTML = "";

if (data.steps?.length) {
  for (const step of data.steps) {
    const stepDiv = document.createElement("div");
    stepDiv.className = "step";

    const title = document.createElement("p");
    title.innerHTML = `<strong>Steg ${step.step_number}: ${step.operation}</strong>`;
    stepDiv.appendChild(title);

    const reason = document.createElement("p");
    reason.innerHTML = `<em>${step.reason}</em>`;
    stepDiv.appendChild(reason);

    // Före
    const beforeLabel = document.createElement("div");
    beforeLabel.textContent = "Före:";
    stepDiv.appendChild(beforeLabel);

    const beforeMath = document.createElement("div");
    renderLatex(beforeMath, step.before, true); 
    stepDiv.appendChild(beforeMath);

    // Efter
    const afterLabel = document.createElement("div");
    afterLabel.textContent = "Efter:";
    stepDiv.appendChild(afterLabel);

    const afterMath = document.createElement("div");
    renderLatex(afterMath, step.after, true); 
    stepDiv.appendChild(afterMath);

    outputBar.appendChild(stepDiv);
  }
}

    // Svar
    const finalDiv = document.createElement("div");
    finalDiv.className = "final";

    const finalLabel = document.createElement("strong");
    finalLabel.textContent = "Svar:";
    finalDiv.appendChild(finalLabel);

    const finalMath = document.createElement("div");
    renderLatex(finalMath, data.final_answer, true);
    finalDiv.appendChild(finalMath);

    outputBar.appendChild(finalDiv);

    textInput.value = "";
  } catch (e) {
    outputBar.textContent = "Kunde inte nå /solve. Öppna sidan via http://127.0.0.1:8000/ och se att uvicorn kör.";
  }
}
