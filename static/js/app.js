// Configuración de sliders

const SLIDERS = [
  { id: 'alt',   display: v => v + ' cm' },
  { id: 'pes',   display: v => v + ' kg' },
  { id: 'vel',   display: v => parseFloat(v).toFixed(1) },
  { id: 'slong', display: v => v + ' cm' },
  { id: 'salt',  display: v => v + ' cm' },
  { id: 'reac',  display: v => v + ' ms' },
  { id: 'tiro',  display: v => v + ' km/h' },
  { id: 'dist',  display: v => v + ' cm' },  // sólo para el convertidor
];

SLIDERS.forEach(({ id, display }) => {
  const slider = document.getElementById('sl-' + id);
  const valueEl = document.getElementById('val-' + id);
  if (!slider || !valueEl) return;

  const update = () => {
    valueEl.textContent = display ? display(slider.value) : slider.value;
  };

  update();
  slider.addEventListener('input', () => {
    update();
    if (id === 'dist') actualizarConvertidor();
  });
});


// Convertidor: distancia caída de regla → tiempo de reacción

function actualizarConvertidor() {
  const distCm = parseFloat(document.getElementById('sl-dist').value);
  const distM  = distCm / 100;
  const g = 9.81;
  const ms = Math.round(Math.sqrt(2 * distM / g) * 1000);

  document.getElementById('tiempo-calculado').textContent = ms + ' ms';

  // Copiar automáticamente al slider de reacción
  const slReac = document.getElementById('sl-reac');
  const valReac = document.getElementById('val-reac');
  slReac.value  = Math.min(Math.max(ms, parseInt(slReac.min)), parseInt(slReac.max));
  valReac.textContent = slReac.value + ' ms';
}

// Inicializar al cargar
actualizarConvertidor();


// Función principal: analizar jugador

async function analizar() {
  const btn  = document.getElementById('btn-analizar');
  const nota = document.getElementById('loading-note');

  btn.disabled = true;
  btn.querySelector('.btn-text').textContent = '⏳ PROCESANDO…';
  nota.style.display = 'flex';

  const datos = {
    altura_cm:     parseInt(document.getElementById('sl-alt').value),
    peso_kg:       parseInt(document.getElementById('sl-pes').value),
    velocidad_ms:  parseFloat(document.getElementById('sl-vel').value),
    salto_long_cm: parseInt(document.getElementById('sl-slong').value),
    salto_alt_cm:  parseInt(document.getElementById('sl-salt').value),
    reaccion_ms:   parseInt(document.getElementById('sl-reac').value),
    potencia_tiro: parseInt(document.getElementById('sl-tiro').value),
  };

  try {
    const response = await fetch('/analizar', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(datos),
    });

    const resultado = await response.json();

    if (resultado.error) {
      alert('Error del sistema experto: ' + resultado.error);
    } else {
      pintarResultado(resultado);
      mostrarEnCampo(resultado.ranking);
    }

  } catch (err) {
    console.error('Error:', err);
    alert('No se pudo conectar con el servidor. ¿Está en ejecución app.py?');
  } finally {
    btn.disabled = false;
    btn.querySelector('.btn-text').textContent = '⚡ ANALIZAR POSICIÓN';
    nota.style.display = 'none';
  }
}


// Pintar resultado 

function pintarResultado(resultado) {
  const card = document.getElementById('result-card');

  if (!resultado) {
    card.innerHTML = '<p>Error en el sistema experto</p>';
    return;
  }

  card.innerHTML = `
    <div class="panel-title">🏆 POSICIÓN RECOMENDADA</div>
    <div class="pos-badge">${resultado.posicion_recomendada}</div>
    <div class="pos-name">${resultado.nombre_posicion}</div>
    <div class="confidence-section">
      ${crearRankingHTML(resultado.ranking)}
    </div>
  `;

  // Reglas activadas
  const rulesSection = document.getElementById('rules-section');
  const rulesList    = document.getElementById('rules-list');

  rulesSection.style.display = 'block';
  rulesList.innerHTML = resultado.reglas_activadas.map(r => `
    <div class="rule-item">
      <span class="rule-icon">▸</span>
      <span class="rule-text">${r}</span>
    </div>
  `).join('');
}


// Barras de ranking 

function crearRankingHTML(ranking) {
  if (!ranking) return '';

  return ranking.slice(0, 5).map((item, i) => {
    const pct  = Math.round(item.confianza_relativa);
    const clase = i === 0 ? 'first' : i === 1 ? 'second' : 'other';

    return `
      <div class="conf-row">
        <span class="conf-pos">${item.posicion}</span>
        <div class="conf-bar-bg">
          <div class="conf-bar ${clase}" style="width:${pct}%"></div>
        </div>
        <span class="conf-pct">${pct}%</span>
      </div>
    `;
  }).join('');
}


// Resaltar dot en campo

function resaltarPos(pos) {
  const el = document.getElementById('dot-' + pos);
  if (!el) return;
  el.style.transform = 'scale(1.4)';
  setTimeout(() => { el.style.transform = ''; }, 350);
}


// Mostrar posiciones en el campo SVG

function mostrarEnCampo(ranking) {
  document.querySelectorAll('.pos-dot').forEach(el => {
    el.style.display = 'none';
    el.style.opacity = '1';
    el.style.filter  = '';
    const circle = el.querySelector('circle');
    if (circle) circle.setAttribute('r', '11');
  });

  if (!ranking || ranking.length === 0) return;

  const maxScore = ranking[0].score;

  ranking.slice(0, 5).forEach((item, i) => {
    const dot = document.getElementById('dot-' + item.posicion);
    if (!dot) return;

    dot.style.display = 'block';
    dot.style.opacity = i === 0 ? '1' : String(Math.max(0.25, item.score / maxScore));

    if (i === 0) {
      const circle = dot.querySelector('circle');
      if (circle) circle.setAttribute('r', '14');
      dot.style.filter = 'drop-shadow(0 0 10px rgba(61,255,160,0.8))';
      dot.classList.add('flash');
      setTimeout(() => dot.classList.remove('flash'), 450);
    }
  });
}