// "Use your own image" flow: pick a file, preview the pixelated version,
// generate a deal in a worker, then hand the finished level to the game.
// Finished levels are kept in localStorage (best effort).

import { levelFromSource, loadImageFile, nameFromFile } from './imageLoad.js';
import { parseLevel } from './image.js';

const STORE_KEY = 'antfeast.custom.v1';
const MAX_SAVED = 8;

export function loadSavedLevels() {
  try {
    const list = JSON.parse(localStorage.getItem(STORE_KEY) || '[]');
    return Array.isArray(list) ? list.filter((d) => d && d.rows && d.palette && d.deal) : [];
  } catch {
    return [];
  }
}

function saveLevels(list) {
  try {
    localStorage.setItem(STORE_KEY, JSON.stringify(list.slice(-MAX_SAVED)));
  } catch {
    // Storage unavailable or full: the level still works for this session.
  }
}

// onLevel(def) is called with each finished level.
export function setupCustomImages({ onLevel }) {
  const fileInput = document.getElementById('file');
  const dialog = document.getElementById('custom');
  const preview = document.getElementById('preview');
  const nameInput = document.getElementById('custom-name');
  const sizeSelect = document.getElementById('custom-size');
  const colorSelect = document.getElementById('custom-colors');
  const status = document.getElementById('custom-status');
  const progress = document.getElementById('custom-progress');
  const makeBtn = document.getElementById('custom-make');
  const playBtn = document.getElementById('custom-play');
  const cancelBtn = document.getElementById('custom-cancel');

  let bitmap = null;
  let def = null;
  let worker = null;

  document.getElementById('upload').addEventListener('click', () => fileInput.click());

  fileInput.addEventListener('change', async () => {
    const file = fileInput.files[0];
    fileInput.value = '';
    if (!file) return;
    try {
      bitmap = await loadImageFile(file);
    } catch (err) {
      alert(err.message);
      return;
    }
    nameInput.value = nameFromFile(file);
    setBusy(false);
    status.textContent = 'Pictures with clear outlines and nested shapes make trickier puzzles.';
    updatePreview();
    if (!dialog.open) dialog.showModal();
  });

  sizeSelect.addEventListener('change', updatePreview);
  colorSelect.addEventListener('change', updatePreview);

  function updatePreview() {
    if (!bitmap) return;
    def = levelFromSource(bitmap, bitmap.width, bitmap.height, {
      maxSide: +sizeSelect.value,
      colors: +colorSelect.value,
    });
    const gw = def.rows[0].length;
    const gh = def.rows.length;
    const cell = Math.floor(Math.min(240 / gw, 240 / gh));
    preview.width = gw * cell;
    preview.height = gh * cell;
    const ctx = preview.getContext('2d');
    def.rows.forEach((row, y) => {
      [...row].forEach((k, x) => {
        ctx.fillStyle = def.palette[k];
        ctx.fillRect(x * cell, y * cell, cell, cell);
      });
    });
  }

  function setBusy(busy) {
    for (const el of [nameInput, sizeSelect, colorSelect, makeBtn]) el.disabled = busy;
    makeBtn.hidden = busy;
    playBtn.hidden = !busy;
    playBtn.disabled = true;
    progress.hidden = !busy;
    progress.value = 0;
  }

  function stopWorker() {
    worker?.terminate();
    worker = null;
  }

  makeBtn.addEventListener('click', () => {
    if (!def) return;
    def.name = nameInput.value.trim() || 'My picture';
    setBusy(true);
    status.textContent = 'Shuffling the boxes into a tricky order…';
    stopWorker();
    worker = new Worker(new URL('./generateWorker.js', import.meta.url), { type: 'module' });
    worker.onmessage = (e) => {
      const msg = e.data;
      if (msg.type === 'progress') {
        progress.value = msg.phase === 'start' ? 0.02 : msg.it / msg.iterations;
        playBtn.disabled = !msg.ready;
        status.textContent = msg.ready
          ? `Finding a tricky box order… puzzle so far: ${msg.difficulty}.`
          : 'Looking for a solvable box order…';
      } else if (msg.type === 'done') {
        stopWorker();
        if (!msg.result) {
          setBusy(false);
          status.textContent = "Couldn't make a solvable puzzle from this picture. Try fewer colours or a smaller size.";
          return;
        }
        const level = {
          ...def,
          id: `${Date.now()}-${Math.floor(Math.random() * 1e6)}`,
          deal: msg.result.deal,
          solution: msg.result.solution,
          difficulty: msg.result.difficulty,
          custom: true,
        };
        const saved = loadSavedLevels();
        saved.push(level);
        saveLevels(saved);
        dialog.close();
        onLevel(level);
      }
    };
    worker.onerror = (e) => {
      stopWorker();
      setBusy(false);
      status.textContent = `Something went wrong: ${e.message}`;
    };
    worker.postMessage({
      type: 'start',
      image: parseLevel(def),
      options: { iterations: 250, patience: 60, trials: 12, maxNodes: 3000, target: 0.1, seed: 1 },
    });
  });

  playBtn.addEventListener('click', () => worker?.postMessage({ type: 'finish' }));

  cancelBtn.addEventListener('click', () => {
    stopWorker();
    dialog.close();
  });
  dialog.addEventListener('close', stopWorker);
}

export function removeSavedLevel(id) {
  saveLevels(loadSavedLevels().filter((d) => d.id !== id));
}
