/*
   Casa del Ermitaño - Interactive Client Logic
   Adiestramiento y Psicología Canina en Sitges, Barcelona
*/

document.addEventListener('DOMContentLoaded', () => {

  // ==========================================
  // 1. Navigation & Theme Toggle
  // ==========================================
  const navbar = document.querySelector('.navbar');
  const menuToggle = document.querySelector('.menu-toggle');
  const navMenu = document.querySelector('.nav-menu');
  const themeToggle = document.querySelector('.theme-toggle');

  window.addEventListener('scroll', () => {
    if (window.scrollY > 50) {
      navbar.classList.add('scrolled');
    } else {
      navbar.classList.remove('scrolled');
    }
  });

  menuToggle.addEventListener('click', () => {
    menuToggle.classList.toggle('active');
    navMenu.classList.toggle('active');
  });

  document.querySelectorAll('.nav-link').forEach(link => {
    link.addEventListener('click', () => {
      menuToggle.classList.remove('active');
      navMenu.classList.remove('active');
    });
  });

  // Servicios dropdown: en móvil funciona como acordeón (clic); en desktop se abre con hover (CSS)
  document.querySelectorAll('.nav-dropdown-toggle').forEach(toggle => {
    toggle.addEventListener('click', (e) => {
      if (window.matchMedia('(max-width: 768px)').matches) {
        e.preventDefault();
        const dropdown = toggle.closest('.nav-dropdown');
        const isOpen = dropdown.classList.toggle('open');
        toggle.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
      }
    });
  });

  const savedTheme = localStorage.getItem('theme');
  const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

  if (savedTheme === 'dark' || (!savedTheme && systemPrefersDark)) {
    document.documentElement.setAttribute('data-theme', 'dark');
  } else {
    document.documentElement.setAttribute('data-theme', 'light');
  }

  themeToggle.addEventListener('click', () => {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
  });

  // ==========================================
  // 2. Before / After Image Slider
  // ==========================================
  const sliderContainer = document.querySelector('.comparison-slider');
  const afterImage = document.querySelector('.image-after');
  const handle = document.querySelector('.slider-handle');

  if (sliderContainer && afterImage && handle) {
    let isDragging = false;

    const moveSlider = (clientX) => {
      const rect = sliderContainer.getBoundingClientRect();
      let percentage = ((clientX - rect.left) / rect.width) * 100;
      if (percentage < 0) percentage = 0;
      if (percentage > 100) percentage = 100;
      afterImage.style.clipPath = `polygon(0 0, ${percentage}% 0, ${percentage}% 100%, 0 100%)`;
      handle.style.left = `${percentage}%`;
    };

    sliderContainer.addEventListener('mousedown', (e) => { isDragging = true; moveSlider(e.clientX); });
    window.addEventListener('mouseup', () => { isDragging = false; });
    sliderContainer.addEventListener('mousemove', (e) => { if (isDragging) moveSlider(e.clientX); });

    sliderContainer.addEventListener('touchstart', (e) => { isDragging = true; if (e.touches[0]) moveSlider(e.touches[0].clientX); });
    window.addEventListener('touchend', () => { isDragging = false; });
    sliderContainer.addEventListener('touchmove', (e) => { if (isDragging && e.touches[0]) moveSlider(e.touches[0].clientX); });
  }

  // ==========================================
  // 3. Needs Assessment Quiz
  // ==========================================
  const quizData = [
    {
      question: "¿Cuál es el principal reto de comportamiento de tu perro?",
      options: [
        { text: "Tira de la correa, no acude a la llamada o ignora los comandos básicos", score: "basico" },
        { text: "Reactividad, miedo o agresividad ante personas u otros perros", score: "psicologia" },
        { text: "Ya tiene la base pero quiero llevarlo a un nivel superior", score: "avanzado" },
        { text: "No sé bien cuál es el problema — necesito una evaluación profesional", score: "psicologia" }
      ]
    },
    {
      question: "¿Qué edad tiene tu perro?",
      options: [
        { text: "Cachorro (menos de 6 meses) — quiero empezar desde cero bien", score: "basico" },
        { text: "Joven (6 meses – 2 años) — tiene mucha energía y le cuesta concentrarse", score: "basico" },
        { text: "Adulto (2 – 7 años) — tiene hábitos ya instaurados", score: "psicologia" },
        { text: "Senior (más de 7 años) — quiero mejorar su calidad de vida", score: "avanzado" }
      ]
    },
    {
      question: "¿Cómo reacciona tu perro ante estímulos externos (coches, personas, otros perros)?",
      options: [
        { text: "Se pone muy nervioso, ladra o tira con fuerza hacia ellos", score: "psicologia" },
        { text: "Se distrae mucho pero no agrede ni tiene miedo", score: "basico" },
        { text: "Reacciona con miedo — se esconde o se queda bloqueado", score: "psicologia" },
        { text: "Responde bastante bien — solo necesito pulir detalles", score: "avanzado" }
      ]
    },
    {
      question: "¿Cuándo te gustaría empezar a trabajar con Eduardo?",
      options: [
        { text: "Lo antes posible — el problema es urgente o me está afectando mucho", score: "psicologia" },
        { text: "En las próximas semanas — me lo estoy organizando", score: "basico" },
        { text: "Quiero explorar opciones antes de decidirme", score: "avanzado" }
      ]
    }
  ];

  let currentStep = 0;
  const userAnswers = [];

  const quizStep = document.getElementById('quiz-step');
  const quizQuestion = document.getElementById('quiz-question');
  const quizOptions = document.getElementById('quiz-options');
  const btnPrev = document.getElementById('btn-prev');
  const btnNext = document.getElementById('btn-next');
  const progressFill = document.getElementById('progress-fill');
  const stepCount = document.getElementById('step-count');
  const quizResult = document.getElementById('quiz-result');
  const resultTitle = document.getElementById('result-title');
  const resultDesc = document.getElementById('result-desc');
  const recDesc = document.getElementById('rec-desc');
  const btnRestart = document.getElementById('btn-restart');
  const btnSelectResultPackage = document.getElementById('btn-select-result-package');

  function initQuiz() {
    if (!quizStep) return;
    currentStep = 0;
    userAnswers.length = 0;
    quizResult.classList.remove('active');
    quizStep.classList.add('active');
    btnPrev.style.visibility = 'hidden';
    btnNext.innerText = 'Siguiente';
    showQuestion();
  }

  function showQuestion() {
    const questionInfo = quizData[currentStep];
    quizQuestion.innerText = questionInfo.question;
    quizOptions.innerHTML = '';

    const progressPercent = (currentStep / quizData.length) * 100;
    progressFill.style.width = `${progressPercent}%`;
    stepCount.innerText = `Paso ${currentStep + 1} de ${quizData.length}`;

    questionInfo.options.forEach((option, idx) => {
      const optionEl = document.createElement('div');
      optionEl.classList.add('quiz-option');
      if (userAnswers[currentStep] === idx) optionEl.classList.add('selected');

      optionEl.innerHTML = `
        <div class="quiz-radio"></div>
        <div class="quiz-option-text">${option.text}</div>
      `;

      optionEl.addEventListener('click', () => {
        document.querySelectorAll('.quiz-option').forEach(el => el.classList.remove('selected'));
        optionEl.classList.add('selected');
        userAnswers[currentStep] = idx;
        btnNext.disabled = false;
      });

      quizOptions.appendChild(optionEl);
    });

    btnNext.disabled = userAnswers[currentStep] === undefined;
    btnPrev.style.visibility = currentStep === 0 ? 'hidden' : 'visible';
    btnNext.innerText = currentStep === quizData.length - 1 ? 'Ver Resultado' : 'Siguiente';
  }

  if (btnNext) {
    btnNext.addEventListener('click', () => {
      if (currentStep < quizData.length - 1) {
        currentStep++;
        showQuestion();
      } else {
        showResults();
      }
    });
  }

  if (btnPrev) {
    btnPrev.addEventListener('click', () => {
      if (currentStep > 0) { currentStep--; showQuestion(); }
    });
  }

  if (btnRestart) {
    btnRestart.addEventListener('click', initQuiz);
  }

  function showResults() {
    quizStep.classList.remove('active');
    quizResult.classList.add('active');
    progressFill.style.width = '100%';
    stepCount.innerText = 'Resultado';

    const scores = { basico: 0, avanzado: 0, psicologia: 0 };
    userAnswers.forEach((ansIdx, qIdx) => {
      const scoreType = quizData[qIdx].options[ansIdx].score;
      scores[scoreType]++;
    });

    let rec = 'basico';
    if (scores.psicologia >= scores.basico && scores.psicologia >= scores.avanzado) {
      rec = 'psicologia';
    } else if (scores.avanzado >= scores.basico && scores.avanzado >= scores.psicologia) {
      rec = 'avanzado';
    }

    if (rec === 'basico') {
      resultTitle.innerText = "Adiestramiento Básico — el punto de partida ideal";
      resultDesc.innerText = "Tu perro necesita construir una base sólida de obediencia y comunicación contigo. Las sesiones de adiestramiento canino son el primer paso para transformar la convivencia diaria.";
      recDesc.innerText = "Trabajaremos la obediencia básica, el paseo con correa, el recall y la concentración. Resultados visibles desde las primeras sesiones con la metodología de Eduardo Mangas.";
      btnSelectResultPackage.setAttribute('data-target-package', 'basico');
    } else if (rec === 'psicologia') {
      resultTitle.innerText = "Psicología Canina — abordamos el origen del problema";
      resultDesc.innerText = "Tu perro muestra señales que requieren un trabajo más profundo sobre su estado emocional y conductual. La especialidad de Eduardo en psicología y etología está diseñada exactamente para esta situación.";
      recDesc.innerText = "Evaluación exhaustiva del perfil conductual, identificación de los desencadenantes y diseño de un protocolo personalizado. El cambio es profundo y duradero.";
      btnSelectResultPackage.setAttribute('data-target-package', 'psicologia');
    } else {
      resultTitle.innerText = "Adiestramiento Avanzado — saca el máximo potencial";
      resultDesc.innerText = "Tu perro ya tiene una buena base y estás listo para dar el siguiente paso. El programa avanzado te abrirá un mundo nuevo de comunicación y complicidad.";
      recDesc.innerText = "Obediencia de alta precisión, órdenes a distancia, trabajo en entornos con distracciones y un nivel de respuesta que sorprenderá a quienes os rodeen.";
      btnSelectResultPackage.setAttribute('data-target-package', 'avanzado');
    }
  }

  if (btnSelectResultPackage) {
    btnSelectResultPackage.addEventListener('click', () => {
      const targetPkg = btnSelectResultPackage.getAttribute('data-target-package');
      selectPackage(targetPkg);
      document.getElementById('calculator').scrollIntoView({ behavior: 'smooth' });
    });
  }

  initQuiz();

  // ==========================================
  // 4. Pricing Calculator
  // ==========================================
  const pkgBasico = document.getElementById('pkg-basico');
  const pkgAvanzado = document.getElementById('pkg-avanzado');
  const pkgPsicologia = document.getElementById('pkg-psicologia');
  const rangeSessions = document.getElementById('range-sessions');
  const sessionCountVal = document.getElementById('session-count-val');
  const sessionsLabel = document.getElementById('sessions-label');

  const addonHome = document.getElementById('addon-home');
  const addonSupport = document.getElementById('addon-support');
  const addonMaterials = document.getElementById('addon-materials');

  const summaryPackageName = document.getElementById('summary-package-name');
  const summaryPackagePrice = document.getElementById('summary-package-price');
  const summarySessionsCount = document.getElementById('summary-sessions-count');
  const summarySessionsPrice = document.getElementById('summary-sessions-price');
  const summaryAddonsList = document.getElementById('summary-addons-list');
  const summaryAddonsPrice = document.getElementById('summary-addons-price');
  const summaryTotalPrice = document.getElementById('summary-total-price');
  const btnBookSession = document.getElementById('btn-book-session');

  const packages = {
    basico:    { name: "Adiestramiento Básico",    unitPrice: 45, unitLabel: "sesiones", sliderMin: 1, sliderMax: 10, sliderDefault: 5, priceLabel: "45€/sesión" },
    avanzado:  { name: "Adiestramiento Avanzado",  unitPrice: 55, unitLabel: "sesiones", sliderMin: 1, sliderMax: 10, sliderDefault: 5, priceLabel: "55€/sesión" },
    psicologia:{ name: "Psicología Canina",        unitPrice: 65, unitLabel: "sesiones", sliderMin: 1, sliderMax: 10, sliderDefault: 5, priceLabel: "65€/sesión" }
  };

  let activePackage = 'basico';

  function selectPackage(pkgKey) {
    if (!packages[pkgKey]) return;
    activePackage = pkgKey;

    [pkgBasico, pkgAvanzado, pkgPsicologia].forEach(el => { if (el) el.classList.remove('selected'); });
    const targetEl = document.getElementById(`pkg-${pkgKey}`);
    if (targetEl) targetEl.classList.add('selected');

    const pkg = packages[pkgKey];
    rangeSessions.min = pkg.sliderMin;
    rangeSessions.max = pkg.sliderMax;
    rangeSessions.value = pkg.sliderDefault;
    sessionCountVal.innerText = pkg.sliderDefault;

    if (sessionsLabel) {
      sessionsLabel.innerText = "2. Número de Sesiones";
    }

    calculateCosts();
  }

  function setupCalculatorEvents() {
    if (!pkgBasico) return;

    pkgBasico.addEventListener('click', () => selectPackage('basico'));
    pkgAvanzado.addEventListener('click', () => selectPackage('avanzado'));
    pkgPsicologia.addEventListener('click', () => selectPackage('psicologia'));

    rangeSessions.addEventListener('input', (e) => {
      sessionCountVal.innerText = e.target.value;
      calculateCosts();
    });

    [addonHome, addonSupport, addonMaterials].forEach(addon => {
      if (addon) addon.addEventListener('click', () => { addon.classList.toggle('selected'); calculateCosts(); });
    });

    if (btnBookSession) {
      btnBookSession.addEventListener('click', () => {
        const pkg = packages[activePackage];
        const qty = rangeSessions.value;
        const total = summaryTotalPrice.innerText;
        const msg = `Hola, me gustaría información sobre: *${pkg.name}* — ${qty} ${pkg.unitLabel}. Presupuesto estimado: *${total}*.`;
        const contactMessage = document.getElementById('message');
        if (contactMessage) contactMessage.value = msg;
        document.getElementById('contact').scrollIntoView({ behavior: 'smooth' });
      });
    }
  }

  function calculateCosts() {
    if (!rangeSessions) return;

    const pkg = packages[activePackage];
    const qty = parseInt(rangeSessions.value);
    const baseCost = pkg.unitPrice * qty;

    let addonsTotal = 0;
    const activeAddonsNames = [];

    if (addonHome && addonHome.classList.contains('selected')) {
      const homeCost = qty * 20;
      addonsTotal += homeCost;
      activeAddonsNames.push(`A domicilio (+${homeCost}€)`);
    }
    if (addonSupport && addonSupport.classList.contains('selected')) {
      addonsTotal += 30;
      activeAddonsNames.push("Soporte WhatsApp (+30€)");
    }
    if (addonMaterials && addonMaterials.classList.contains('selected')) {
      addonsTotal += 25;
      activeAddonsNames.push("Informe evaluación (+25€)");
    }

    const grandTotal = baseCost + addonsTotal;

    if (summaryPackageName) {
      summaryPackageName.innerText = pkg.name;
      summaryPackagePrice.innerText = pkg.priceLabel;
      summarySessionsCount.innerText = `${qty} ${pkg.unitLabel}`;
      summarySessionsPrice.innerText = `${baseCost}€`;
      summaryAddonsList.innerText = activeAddonsNames.length > 0 ? activeAddonsNames.join(', ') : 'Ninguno';
      summaryAddonsPrice.innerText = `+${addonsTotal}€`;

      summaryTotalPrice.classList.remove('pulse');
      void summaryTotalPrice.offsetWidth;
      summaryTotalPrice.classList.add('pulse');
      summaryTotalPrice.innerText = `${grandTotal}€`;
    }
  }

  setupCalculatorEvents();
  calculateCosts();

  // ==========================================
  // 5. Testimonial Carousel
  // ==========================================
  const track = document.querySelector('.reviews-track');
  const slides = Array.from(document.querySelectorAll('.review-slide'));
  const dotsContainer = document.querySelector('.reviews-nav');

  if (track && slides.length > 0 && dotsContainer) {
    let currentSlideIdx = 0;

    slides.forEach((_, idx) => {
      const dot = document.createElement('div');
      dot.classList.add('review-dot');
      if (idx === 0) dot.classList.add('active');
      dot.addEventListener('click', () => {
        goToSlide(idx);
        clearInterval(autoPlayInterval);
      });
      dotsContainer.appendChild(dot);
    });

    const dots = Array.from(document.querySelectorAll('.review-dot'));

    function goToSlide(idx) {
      currentSlideIdx = idx;
      track.style.transform = `translateX(-${idx * 100}%)`;
      dots.forEach(d => d.classList.remove('active'));
      dots[idx].classList.add('active');
    }

    let autoPlayInterval = setInterval(() => {
      goToSlide((currentSlideIdx + 1) % slides.length);
    }, 5000);
  }

  // ==========================================
  // 6. FAQ Accordion
  // ==========================================
  document.querySelectorAll('.faq-header').forEach(header => {
    header.addEventListener('click', () => {
      const item = header.parentElement;
      const isActive = item.classList.contains('active');

      document.querySelectorAll('.faq-item').forEach(el => {
        el.classList.remove('active');
        el.querySelector('.faq-body').style.maxHeight = null;
      });

      if (!isActive) {
        item.classList.add('active');
        const body = item.querySelector('.faq-body');
        body.style.maxHeight = body.scrollHeight + 'px';
      }
    });
  });

  // ==========================================
  // 7. Contact Form
  // ==========================================
  const contactForm = document.getElementById('contact-form');
  const formStatus = document.getElementById('form-status');

  if (contactForm && formStatus) {
    contactForm.addEventListener('submit', (e) => {
      e.preventDefault();

      const name = document.getElementById('name').value.trim();
      const email = document.getElementById('email').value.trim();
      const message = document.getElementById('message').value.trim();

      if (!name || !email || !message) {
        formStatus.innerText = "Por favor, rellena los campos obligatorios (Nombre, Email y Mensaje).";
        formStatus.className = "form-status error";
        return;
      }

      formStatus.innerText = "¡Gracias por contactar con Casa del Ermitaño! Eduardo te responderá lo antes posible.";
      formStatus.className = "form-status success";
      contactForm.reset();

      setTimeout(() => { formStatus.style.display = 'none'; }, 5000);
    });
  }

});
