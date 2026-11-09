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
      resultTitle.innerText = "Curso de Educación Básica — el punto de partida ideal";
      resultDesc.innerText = "Tu perro necesita construir una base sólida de obediencia y comunicación contigo. Las sesiones de adiestramiento canino son el primer paso para transformar la convivencia diaria.";
      recDesc.innerText = "Trabajaremos la obediencia básica, el paseo con correa, el recall y la concentración. Resultados visibles desde las primeras sesiones con la metodología de Eduardo Mangas.";
      btnSelectResultPackage.setAttribute('data-target-package', 'basico');
    } else if (rec === 'psicologia') {
      resultTitle.innerText = "Clases de conducta — abordamos el origen del problema";
      resultDesc.innerText = "Tu perro muestra señales que requieren un trabajo más profundo sobre su estado emocional y conductual. La especialidad de Eduardo en psicología y etología está diseñada exactamente para esta situación.";
      recDesc.innerText = "Evaluación exhaustiva del perfil conductual, identificación de los desencadenantes y diseño de un protocolo personalizado. El cambio es profundo y duradero.";
      btnSelectResultPackage.setAttribute('data-target-package', 'clase');
    } else {
      resultTitle.innerText = "Curso de Educación Completa — saca el máximo potencial";
      resultDesc.innerText = "Tu perro ya tiene una buena base y estás listo para dar el siguiente paso. El curso completo te abrirá un mundo nuevo de comunicación y complicidad.";
      recDesc.innerText = "Obediencia completa sin correa: seguimiento, sentado, acostado, quieto y llamada, más control de ruidos y un comportamiento pacífico y amistoso con perros y personas.";
      btnSelectResultPackage.setAttribute('data-target-package', 'completo');
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
  // 4. Calculadora de presupuesto (tarifas de Eduardo, noviembre 2026)
  //    Clases de conducta 75 €/h · Pack de 6 clases a 75 €/clase ·
  //    Curso básico 1.000 € · Curso completo 1.500 € · desplazamiento aparte por zona y clase
  // ==========================================
  const packages = {
    clase:    { name: 'Clases de conducta (agresividad y trastornos)', type: 'hora', unit: 75, label: '75 €/hora' },
    pack:     { name: 'Pack de 6 clases', type: 'pack', unit: 75, classes: 6, label: '75 €/clase',
                note: '6 clases de 1 hora. El pack se paga por adelantado.' },
    basico:   { name: 'Curso de Educación Básica', type: 'curso', price: 1000, label: '1.000 €', count: '2-3 por semana, 1-2 meses',
                note: '2 o 3 clases por semana durante 1 a 2 meses. Seguimiento, sentado, acostado, quieto y llamada, con correa.' },
    completo: { name: 'Curso de Educación Completa', type: 'curso', price: 1500, label: '1.500 €', count: '2-3 por semana, 2-3 meses',
                note: '2 o 3 clases por semana durante 2 a 3 meses. Todo sin correa, más control de ruidos y comportamiento pacífico y amistoso.' }
  };

  const pkgEls = {};
  Object.keys(packages).forEach(k => { pkgEls[k] = document.getElementById(`pkg-${k}`); });
  const rangeSessions = document.getElementById('range-sessions');
  const sessionCountVal = document.getElementById('session-count-val');
  const sessionsSlider = document.getElementById('sessions-slider');
  const sessionsNote = document.getElementById('sessions-note');
  const zoneSelect = document.getElementById('calc-zona');

  const summaryPackageName = document.getElementById('summary-package-name');
  const summaryPackagePrice = document.getElementById('summary-package-price');
  const summarySessionsCount = document.getElementById('summary-sessions-count');
  const summarySessionsPrice = document.getElementById('summary-sessions-price');
  const summaryAddonsList = document.getElementById('summary-addons-list');
  const summaryAddonsPrice = document.getElementById('summary-addons-price');
  const summaryTotalPrice = document.getElementById('summary-total-price');
  const btnBookSession = document.getElementById('btn-book-session');

  // 1000 -> "1.000 €" (es-ES no agrupa los números de 4 cifras con toLocaleString)
  const eur = n => String(n).replace(/\B(?=(\d{3})+(?!\d))/g, '.') + ' €';

  let activePackage = Object.keys(pkgEls).find(k => pkgEls[k] && pkgEls[k].classList.contains('selected')) || 'pack';

  function currentZone() {
    if (!zoneSelect) return { name: 'Sitges', fee: 20 };
    const opt = zoneSelect.options[zoneSelect.selectedIndex];
    return { name: opt.getAttribute('data-zona') || opt.text, fee: parseInt(zoneSelect.value, 10) || 0 };
  }

  function selectPackage(pkgKey) {
    if (!packages[pkgKey]) return;
    activePackage = pkgKey;
    Object.keys(pkgEls).forEach(k => {
      const el = pkgEls[k];
      if (!el) return;
      el.classList.toggle('selected', k === pkgKey);
      el.setAttribute('aria-pressed', k === pkgKey ? 'true' : 'false');
    });
    const pkg = packages[pkgKey];
    const porHoras = pkg.type === 'hora';
    if (sessionsSlider) sessionsSlider.hidden = !porHoras;
    if (sessionsNote) { sessionsNote.hidden = porHoras; sessionsNote.textContent = pkg.note || ''; }
    if (sessionCountVal) sessionCountVal.textContent = porHoras ? rangeSessions.value : (pkg.type === 'pack' ? '6' : '');
    calculateCosts();
  }

  function calculateCosts() {
    if (!summaryTotalPrice) return;
    const pkg = packages[activePackage];
    const zone = currentZone();
    let classes = null;
    let serviceCost;
    let countText;

    if (pkg.type === 'hora') {
      classes = parseInt(rangeSessions.value, 10);
      serviceCost = pkg.unit * classes;
      countText = classes === 1 ? '1 hora' : `${classes} horas`;
    } else if (pkg.type === 'pack') {
      classes = pkg.classes;
      serviceCost = pkg.unit * classes;
      countText = `${classes} clases`;
    } else {
      serviceCost = pkg.price;
      countText = pkg.count;
    }

    let total;
    if (zone.fee > 0 && classes) {
      const travel = zone.fee * classes;
      summaryAddonsList.textContent = `${zone.name} · ${eur(zone.fee)} × ${classes}`;
      summaryAddonsPrice.textContent = '+' + eur(travel);
      total = eur(serviceCost + travel);
    } else if (zone.fee > 0) {
      summaryAddonsList.textContent = `${zone.name} · ${eur(zone.fee)} por clase`;
      summaryAddonsPrice.textContent = 'aparte';
      total = `${eur(serviceCost)} + desplazamiento`;
    } else {
      summaryAddonsList.textContent = 'Otra zona';
      summaryAddonsPrice.textContent = 'a consultar';
      total = `${eur(serviceCost)} + desplazamiento`;
    }

    summaryPackageName.textContent = pkg.name;
    summaryPackagePrice.textContent = pkg.label;
    summarySessionsCount.textContent = countText;
    summarySessionsPrice.textContent = eur(serviceCost);

    summaryTotalPrice.classList.remove('pulse');
    void summaryTotalPrice.offsetWidth;
    summaryTotalPrice.classList.add('pulse');
    summaryTotalPrice.textContent = total;
  }

  function setupCalculatorEvents() {
    if (!summaryTotalPrice) return;
    Object.keys(pkgEls).forEach(k => {
      const el = pkgEls[k];
      if (!el) return;
      el.addEventListener('click', () => selectPackage(k));
      el.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); selectPackage(k); }
      });
    });
    if (rangeSessions) {
      rangeSessions.addEventListener('input', (e) => {
        if (sessionCountVal) sessionCountVal.textContent = e.target.value;
        calculateCosts();
      });
    }
    if (zoneSelect) zoneSelect.addEventListener('change', calculateCosts);

    if (btnBookSession) {
      btnBookSession.addEventListener('click', () => {
        const pkg = packages[activePackage];
        const zone = currentZone();
        const horas = pkg.type === 'hora' ? ` (${rangeSessions.value} h)` : '';
        const msg = `Hola, me gustaría información sobre: *${pkg.name}*${horas}. Zona: ${zone.name}. Presupuesto estimado: *${summaryTotalPrice.textContent}*.`;
        const contactMessage = document.getElementById('message');
        if (contactMessage) contactMessage.value = msg;
        const contactSection = document.getElementById('contact') || document.getElementById('contacto');
        if (contactSection) contactSection.scrollIntoView({ behavior: 'smooth' });
      });
    }
  }

  setupCalculatorEvents();
  if (summaryTotalPrice) selectPackage(activePackage);

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

// Botón "volver arriba": aparece tras bajar 600px, por encima de los botones de llamar y WhatsApp
(function () {
  const topBtn = document.querySelector('.top-float');
  if (!topBtn) return;
  let ticking = false;
  const update = () => {
    topBtn.classList.toggle('is-visible', window.scrollY > 600);
    ticking = false;
  };
  window.addEventListener('scroll', () => {
    if (!ticking) { window.requestAnimationFrame(update); ticking = true; }
  }, { passive: true });
  update();
  topBtn.addEventListener('click', () => {
    const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    window.scrollTo({ top: 0, behavior: reduce ? 'auto' : 'smooth' });
    const navLink = document.querySelector('.navbar a');
    if (navLink) navLink.focus({ preventScroll: true });
  });
})();

/* ============================
   Seguimiento de clics en CTAs (llamar / WhatsApp / email / mapa / formulario)
   por página y sección. Sin cookies ni datos personales: envía solo tipo de CTA,
   sección, ruta y hora a /.netlify/functions/track (Netlify Blobs).
   ============================ */
(function(){
  function ctaOf(a){
    var h=(a.getAttribute('href')||'');
    if(h.indexOf('tel:')===0)return'llamar';
    if(/wa\.me|whatsapp|api\.whatsapp/i.test(h))return'whatsapp';
    if(h.indexOf('mailto:')===0)return'email';
    if(/google\.[a-z.]+\/maps|maps\.app\.goo/i.test(h))return'mapa';
    return a.getAttribute('data-cta')||null;
  }
  function sectionOf(el){
    var d=el.closest('[data-section]'); if(d)return d.getAttribute('data-section');
    if(el.closest('.whatsapp-float,.call-float'))return'flotante';
    if(el.closest('footer'))return'footer';
    if(el.closest('nav'))return'menu';
    if(el.closest('header'))return'cabecera';
    var s=el.closest('section,header,footer,nav,aside');
    return s?((s.getAttribute('id')||s.className||'').toString().trim().split(/\s+/)[0]||'seccion'):'otro';
  }
  function send(cta,section){
    try{
      var b=JSON.stringify({cta:cta,section:section,page:location.pathname,ts:new Date().toISOString()});
      if(navigator.sendBeacon){navigator.sendBeacon('/.netlify/functions/track',b);}
      else{fetch('/.netlify/functions/track',{method:'POST',body:b,keepalive:true});}
    }catch(e){}
  }
  document.addEventListener('click',function(e){
    var a=e.target.closest&&e.target.closest('a[href],[data-cta]'); if(!a)return;
    var c=ctaOf(a); if(!c)return; send(c,sectionOf(a));
  },true);
  document.addEventListener('submit',function(e){
    var f=e.target;
    if(f&&(f.getAttribute('data-cta-form')!=null||f.id==='leadform'||f.id==='contact-form')) send('formulario',sectionOf(f)||'formulario');
  },true);
})();

/* Publicaciones de Facebook (campeones): se cargan solo al pulsar, para no meter cookies de Facebook a todos los visitantes */
(function(){
  document.querySelectorAll('.fb-post').forEach(function(fig){
    var btn = fig.querySelector('.fb-load');
    if (!btn) return;
    btn.addEventListener('click', function(){
      var href = fig.getAttribute('data-fb-href');
      var h = fig.getAttribute('data-fb-height') || '600';
      var f = document.createElement('iframe');
      f.src = 'https://www.facebook.com/plugins/post.php?href=' + encodeURIComponent(href) + '&show_text=true&width=500';
      f.height = h;
      f.loading = 'lazy';
      f.title = 'Publicación de Facebook de Eduardo Mangas';
      f.setAttribute('allow', 'encrypted-media; picture-in-picture; web-share');
      var img = fig.querySelector('img');
      if (img) img.replaceWith(f);
      btn.remove();
    });
  });
})();
