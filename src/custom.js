// "Use your own image" flow: pick a file, preview the pixelated version,
// generate a deal across a pool of workers, then hand the finished level to
// the game.
// Finished levels are kept in localStorage (best effort).

import { levelFromSource, loadImageFile, nameFromFile } from './imageLoad.js';
import { parseLevel, formatDeal } from './image.js';
import { generateDealParallel } from './parallel.js';
import { difficultyLabel } from './generate.js';

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
  let job = null; // the running deal generator

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

  function stopJob() {
    job?.cancel();
    job = null;
  }

  makeBtn.addEventListener('click', async () => {
    if (!def) return;
    def.name = nameInput.value.trim() || 'My picture';
    setBusy(true);
    status.textContent = 'Shuffling the boxes into a tricky order…';
    stopJob();
    const thisJob = generateDealParallel(parseLevel(def), {
      objective: 'sustained',
      iterations: 400,
      patience: 120,
      trials: 8,
      maxNodes: 3000,
      target: 0.05,
      seed: 1,
      onProgress(p) {
        progress.value = p.phase === 'start' ? 0.02 : p.it / p.iterations;
        playBtn.disabled = !p.ready;
        status.textContent = p.ready
          ? `Finding a tricky box order… puzzle so far: ${difficultyLabel(p.best)}.`
          : 'Looking for a solvable box order…';
      },
    });
    job = thisJob;
    const result = await thisJob.promise;
    if (job !== thisJob) return; // cancelled or replaced
    job = null;
    if (!result) {
      setBusy(false);
      status.textContent = "Couldn't make a solvable puzzle from this picture. Try fewer colours or a smaller size.";
      return;
    }
    const image = parseLevel(def);
    const level = {
      ...def,
      id: `${Date.now()}-${Math.floor(Math.random() * 1e6)}`,
      deal: formatDeal(result.deal, image),
      solution: result.solution.join(''),
      difficulty: difficultyLabel(result),
      custom: true,
    };
    const saved = loadSavedLevels();
    saved.push(level);
    saveLevels(saved);
    dialog.close();
    onLevel(level);
  });

  playBtn.addEventListener('click', () => job?.finish());

  cancelBtn.addEventListener('click', () => {
    stopJob();
    dialog.close();
  });
  dialog.addEventListener('close', stopJob);
}

export function removeSavedLevel(id) {
  saveLevels(loadSavedLevels().filter((d) => d.id !== id));
}
