const box = document.getElementById('box'), go = document.getElementById('go');
const count = document.getElementById('count'), reset = document.getElementById('reset');
const wave = document.getElementById('wave'), ctx = wave.getContext('2d');
const result = document.getElementById('result'), err = document.getElementById('error');
let events = [], gaps = [];

function draw() {
  ctx.clearRect(0, 0, wave.width, wave.height);
  const shown = gaps.slice(-90), w = wave.width / 90;
  shown.forEach((g, i) => {
    const h = Math.min(100, 8 + Math.log2(1 + g) * 8);
    ctx.fillStyle = g >= 600 ? '#9AA3B8' : '#2438F0';
    ctx.fillRect(i * w + 2, (wave.height - h) / 2, w - 4, h);
  });
}

box.addEventListener('keydown', e => {
  if (e.key.length > 1 && e.key !== 'Backspace') return;
  const t = performance.now();
  if (events.length) gaps.push(t - events[events.length - 1].t);
  events.push({ k: e.key === 'Backspace' ? 'Backspace' : 'key', t }); // letters are never stored
  count.textContent = events.length + ' keys';
  go.disabled = events.length < 15;
  draw();
});

reset.onclick = () => {
  events = []; gaps = []; box.value = ''; count.textContent = '0 keys';
  go.disabled = true; result.hidden = true; err.textContent = ''; draw(); box.focus();
};

go.onclick = async () => {
  err.textContent = '';
  const res = await fetch('/api/analyze', {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ events })
  });
  const data = await res.json();
  if (!res.ok) { err.textContent = data.error; return; }
  show(data);
};

function show(d) {
  document.getElementById('name').textContent = 'The ' + d.archetype;
  document.getElementById('about').textContent = d.about;
  const pct = d.percentile === null ? 'You are the first run.' : `Faster than ${d.percentile}% of ${d.runs - 1} earlier runs.`;
  document.getElementById('stats').textContent = `${d.wpm} WPM. ${pct}`;
  const names = Object.keys(d.axes), n = names.length, R = 100, svg = document.getElementById('radar');
  const pt = (i, r) => [Math.sin(2 * Math.PI * i / n) * r, -Math.cos(2 * Math.PI * i / n) * r];
  let html = [25, 50, 75, 100].map(p =>
    `<polygon class="ring" points="${names.map((_, i) => pt(i, R * p / 100).join(',')).join(' ')}"/>`).join('');
  html += `<polygon class="shape" points="${names.map((k, i) => pt(i, R * d.axes[k] / 100).join(',')).join(' ')}"/>`;
  html += names.map((k, i) => { const [x, y] = pt(i, R + 16); return `<text x="${x}" y="${y + 4}">${k} ${d.axes[k]}</text>`; }).join('');
  svg.innerHTML = html;
  result.hidden = false;
  result.scrollIntoView({ behavior: 'smooth' });
}
draw();
