const { mod } = require("three/tsl");

async function SolveProblem() {
  const input = document.getElementById('user-input').value;
  const mode = document.getElementById('mode').value;

  if (!input.trim()) {
    alert('Inget problem in skrivet!');
    return;
  }

  const payload = {
    input: input,
    mode: mode
  };

  const response = await fetch('/solve', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });

  if (data.steps && data.steps.length > 0) {
    data.steps.forEach(step => {
      const stepDiv = document.createElement('div');
      stepDiv.className = 'step';
      stepDiv.innerHTML =
        `<p>Step ${step.step_number}: ${step.operation}</p>` +
        `<p>${step.reason}</p>` +
        `<p>Before: \\(${step.before}\\)</p>` +
        `<p>After: \\(${step.after}\\)</p>`;
      resultsDiv.appendChild(stepDiv);
    });
  }

  const finalDiv = document.createElement('div');
  finalDiv.innerHTML =
    `<p><strong>Final Answer:</strong> \\(${data.final_answer}\\)</p>`;
  resultsDiv.appendChild(finalDiv);

  if (typeof renderMathInElement === 'function') {
    renderMathInElement(resultsDiv, {
      delimiters: [
        { left: "\\(", right: "\\)", display: false },
        { left: "\\[", right: "\\]", display: true }
      ],
      throwOnError: false
    });
  }
}
