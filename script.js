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
    el.textContent = s; 
  }
}


const sidebar = document.getElementById("sidebar");
const toggleContainer = document.getElementById("toggleContainer");

function toggleSidebar() {
  sidebar.classList.toggle("hidden");
}

const sendBtn = document.getElementById("sendBtn");
const textInput = document.getElementById("userInput");
const actionSelect = document.getElementById("actionSelect");
const outputBar = document.getElementById("outputBar");

sendBtn.addEventListener("click", solveProblem);

async function solveProblem() {
  outputBar.style.display = "block";
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
     body: JSON.stringify({
       input: input,
       mode: mode,
       variable: "x",
       lang: currentLang 
     })
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

let currentLang = "sv";

const HERO_IMAGES = {
  en: {
    light: "images/SolveyLightEN.png",
    dark: "images/SolveyDarkEN.png",
  },
  sv: {
    light: "images/SolveyLightEN.png",
    dark: "images/SolveyDarkEN.png",
  },
  zh: {
    light: "images/SolveyLightCN.png",
    dark: "images/SolveyDarkCN.png",
  },
  yue: {
    light: "images/SolveyLightCN.png",
    dark: "images/SolveyDarkCN.png",
  },
};
const I18N = {
  sv: {
    inputPlaceholder: "Skriv din fråga",
    outputPlaceholder: "Resultatet visas här…",
    actionSolve: "Lös",
    actionSimplify: "Förenkla",
  },
  en: {
    inputPlaceholder: "Type your question",
    outputPlaceholder: "Result will appear here…",
    actionSolve: "Solve",
    actionSimplify: "Simplify",
  },
  zh: {
    inputPlaceholder: "输入你的问题",
    outputPlaceholder: "结果会显示在这里…",
    actionSolve: "求解",
    actionSimplify: "化简",
  },
  yue: {
    inputPlaceholder: "輸入你嘅問題",
    outputPlaceholder: "結果會喺呢度顯示…",
    actionSolve: "求解",
    actionSimplify: "化簡",
  },
};

const heroImg = document.getElementById("heroImg");

function isDarkMode() {
  return document.body.classList.contains("darkmode");
}

function updateHeroImage() {
  const themeKey = isDarkMode() ? "dark" : "light";
  const pack = HERO_IMAGES[currentLang] || HERO_IMAGES.sv;

  if (heroImg && pack && pack[themeKey]) {
    heroImg.src = pack[themeKey];
  }
}

function applyLanguage(lang) {
  currentLang = lang;

  document.querySelectorAll("[data-i18n]").forEach(el => {
    const key = el.getAttribute("data-i18n");
    const val = I18N?.[lang]?.[key];
    if (val != null) el.textContent = val;
  });

  document.querySelectorAll("[data-i18n-placeholder]").forEach(el => {
    const key = el.getAttribute("data-i18n-placeholder");
    const val = I18N?.[lang]?.[key];
    if (val != null) el.setAttribute("placeholder", val);
  });

  updateHeroImage();
}

const shadeBtn = document.getElementById("shade");
const shadeIcon = document.getElementById("shadeIcon");

function updateShadeIcon() {
  if (!shadeIcon) return;
  shadeIcon.textContent = isDarkMode() ? "☀️" : "🌙";
}

shadeBtn.addEventListener("click", () => {
  document.body.classList.toggle("darkmode");
  updateShadeIcon();
  updateHeroImage();
});

const langMenu = document.getElementById("langMenu");
const langSelectedImg = document.getElementById("langSelectedImg");
const langList = document.getElementById("langList");

document.getElementById("langSelected").addEventListener("click", (e) => {
  e.stopPropagation();
  langMenu.classList.toggle("open");
});

document.addEventListener("click", () => {
  langMenu.classList.remove("open");
});

langList.querySelectorAll("li").forEach(li => {
  li.addEventListener("click", (e) => {
    e.stopPropagation();
    const lang = li.getAttribute("data-lang");
    const img = li.querySelector("img");

    if (img && langSelectedImg) {
      langSelectedImg.src = img.src;
      langSelectedImg.alt = img.alt;
    }

    applyLanguage(lang);
    langMenu.classList.remove("open");
  });
});


updateShadeIcon();
applyLanguage(currentLang);
updateHeroImage();
