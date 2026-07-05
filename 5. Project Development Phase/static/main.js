const form = document.querySelector('#predictionForm');
const riskChart = document.querySelector('#riskChart');
const safeChart = document.querySelector('#safeChart');
const riskValue = document.querySelector('#riskValue');
const safeValue = document.querySelector('#safeValue');
const statusPanel = document.querySelector('#predictionStatus strong');
const statusCopy = document.querySelector('#predictionStatus p');
const formMessage = document.querySelector('#formMessage');
const navButtons = document.querySelectorAll('.nav-btn');
const revealCards = document.querySelectorAll('.reveal-card');

const updateCharts = (risk, safe) => {
  const riskPercent = Math.min(100, Math.max(0, risk));
  const safePercent = Math.min(100, Math.max(0, safe));
  riskChart.style.background = `conic-gradient(#ff5e6c ${riskPercent * 3.6}deg, rgba(255,255,255,0.08) 0deg)`;
  safeChart.style.background = `conic-gradient(#28c39b ${safePercent * 3.6}deg, rgba(255,255,255,0.08) 0deg)`;
  riskValue.textContent = `${riskPercent}%`;
  safeValue.textContent = `${safePercent}%`;
};

const setStatus = (status) => {
  statusPanel.textContent = status;
  const statusText = {
    'High risk': 'Flood conditions are elevated. Share alerts and follow safety procedures.',
    'Moderate risk': 'Stay alert and keep monitoring weather updates.',
    'Safe': 'Conditions are currently stable, but continue checking local forecasts.'
  };
  statusCopy.textContent = statusText[status] || 'Awaiting input';
};

const smoothScrollTo = (targetId) => {
  const section = document.getElementById(targetId);
  if (section) {
    section.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
};

navButtons.forEach((button) => {
  button.addEventListener('click', () => {
    const target = button.dataset.target;
    if (target) smoothScrollTo(target);
  });
});

const revealOnScroll = () => {
  const trigger = window.innerHeight * 0.92;
  revealCards.forEach((card) => {
    const top = card.getBoundingClientRect().top;
    if (top < trigger) card.classList.add('visible');
  });
};

window.addEventListener('scroll', revealOnScroll);
window.addEventListener('load', revealOnScroll);

if (form) {
  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    formMessage.textContent = '';

    const data = {};
    const inputs = Array.from(form.querySelectorAll('input'));
    for (const input of inputs) {
      if (!input.value) {
        input.focus();
        formMessage.textContent = 'Please fill all fields to continue.';
        return;
      }
      data[input.name] = parseFloat(input.value);
    }

    try {
      const response = await fetch('/api/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      });

      const result = await response.json();
      if (!response.ok) {
        throw new Error(result.error || 'Prediction failed.');
      }

      updateCharts(result.risk, result.safe);
      setStatus(result.status);
      formMessage.textContent = `Predicted by ${result.model}.`;
      formMessage.style.color = '#cff7e8';
    } catch (error) {
      formMessage.textContent = error.message;
      formMessage.style.color = '#ff8fa7';
    }
  });
}