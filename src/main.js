import { LEVELS } from './levels.js';
import { parseLevel, parseDeal } from './image.js';
import { Game, hashString } from './state.js';
import { updateAnts, STEP } from './ants.js';
import { render } from './render.js';
import { makeReplayer } from './bot.js';
import { W, H, stackRect, contains } from './layout.js';
import { setupCustomImages, loadSavedLevels, removeSavedLevel } from './custom.js';

const params = new URLSearchParams(location.search);
const debug = params.has('debug');
const autoplay = params.has('auto'); // replay the stored solution

const canvas = document.getElementById('game');
const ctx = canvas.getContext('2d');
const levelSelect = document.getElementById('level');
const restartBtn = document.getElementById('restart');
const info = document.getElementById('info');
const removeBtn = document.getElementById('remove');

// Built-in levels followed by the player's own (saved in this browser).
let levels = [...LEVELS, ...loadSavedLevels()];

let levelIndex = clampLevel(parseInt(params.get('level') ?? '0', 10));
let game;
let bot = null;

function clampLevel(i) {
  return Number.isFinite(i) ? ((i % levels.length) + levels.length) % levels.length : 0;
}

function startLevel(i) {
  levelIndex = clampLevel(i);
  const def = levels[levelIndex];
  const image = parseLevel(def);
  const deal = def.deal ? parseDeal(def.deal, image) : undefined;
  game = new Game(image, hashString(def.name), { deal });
  bot = autoplay && def.solution ? makeReplayer(def.solution) : null;
  levelSelect.value = String(levelIndex);
  removeBtn.hidden = !def.custom;
  window.game = game;
}

function fillLevelSelect() {
  levelSelect.replaceChildren();
  const builtIn = document.createElement('optgroup');
  builtIn.label = 'Levels';
  const own = document.createElement('optgroup');
  own.label = 'Your images';
  levels.forEach((def, i) => {
    const opt = document.createElement('option');
    opt.value = String(i);
    opt.textContent = def.custom
      ? `${def.name}${def.difficulty ? ` (${def.difficulty})` : ''}`
      : `${i + 1}. ${def.name}`;
    (def.custom ? own : builtIn).append(opt);
  });
  levelSelect.append(builtIn);
  if (own.children.length) levelSelect.append(own);
}
fillLevelSelect();

setupCustomImages({
  onLevel(def) {
    levels.push(def);
    fillLevelSelect();
    startLevel(levels.length - 1);
  },
});

removeBtn.addEventListener('click', () => {
  const def = levels[levelIndex];
  if (!def.custom || !confirm(`Remove "${def.name}"?`)) return;
  removeSavedLevel(def.id);
  levels = [...LEVELS, ...loadSavedLevels()];
  fillLevelSelect();
  startLevel(0);
});
levelSelect.addEventListener('change', () => startLevel(parseInt(levelSelect.value, 10)));
restartBtn.addEventListener('click', () => startLevel(levelIndex));

// --- Sizing -------------------------------------------------------------
let scale = 1;
function resize() {
  const header = document.querySelector('header').offsetHeight;
  const availW = Math.min(window.innerWidth - 16, 640);
  const availH = window.innerHeight - header - 16;
  scale = Math.max(0.1, Math.min(availW / W, availH / H));
  const dpr = window.devicePixelRatio || 1;
  canvas.style.width = `${W * scale}px`;
  canvas.style.height = `${H * scale}px`;
  canvas.width = Math.round(W * scale * dpr);
  canvas.height = Math.round(H * scale * dpr);
  ctx.setTransform(scale * dpr, 0, 0, scale * dpr, 0, 0);
}
window.addEventListener('resize', resize);

// --- Input --------------------------------------------------------------
canvas.addEventListener('pointerdown', (e) => {
  const rect = canvas.getBoundingClientRect();
  const x = (e.clientX - rect.left) / scale;
  const y = (e.clientY - rect.top) / scale;
  if (game.status === 'won') return startLevel(levelIndex + 1);
  if (game.status === 'lost') return startLevel(levelIndex);
  for (let s = 0; s < game.stacks.length; s++) {
    if (contains(stackRect(s, 0), x, y)) {
      game.placeBox(s);
      return;
    }
  }
});

// --- Loop ---------------------------------------------------------------
let last = performance.now();
let acc = 0;
let lastInfo = '';

function frame(now) {
  acc += Math.min(0.1, (now - last) / 1000);
  last = now;
  while (acc >= STEP) {
    if (game.status === 'playing') {
      if (bot) bot(game);
      updateAnts(game, STEP);
      game.updateStatus();
    }
    acc -= STEP;
  }
  render(ctx, game, { debug });

  const text = `${game.pixelsLeft} / ${game.totalPixels} pixels left`;
  if (text !== lastInfo) {
    info.textContent = text;
    lastInfo = text;
  }
  requestAnimationFrame(frame);
}

startLevel(levelIndex);
resize();
requestAnimationFrame(frame);
