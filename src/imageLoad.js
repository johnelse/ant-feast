// Turns a user-supplied image into a level definition (same shape as the
// entries in levels.js, minus the deal): reduce the colours with k-means on
// a supersampled copy, then give each grid cell its most common colour.

import { mulberry32 } from './state.js';

const KEYS = 'abcdefghij';
const SUPERSAMPLE = 6; // source pixels averaged per grid cell, per axis

// Grid dimensions keeping the aspect ratio, longest side = maxSide.
export function gridSize(w, h, maxSide) {
  const s = maxSide / Math.max(w, h);
  return {
    gw: Math.max(4, Math.round(w * s)),
    gh: Math.max(4, Math.round(h * s)),
  };
}

// RGBA -> RGB floats, compositing transparency over white.
export function toRGB(rgba) {
  const n = rgba.length / 4;
  const out = new Float32Array(n * 3);
  for (let i = 0; i < n; i++) {
    const a = rgba[i * 4 + 3] / 255;
    for (let j = 0; j < 3; j++) out[i * 3 + j] = rgba[i * 4 + j] * a + 255 * (1 - a);
  }
  return out;
}

// Each grid cell takes the most common cluster among the source pixels it
// covers. Keeps edges crisp, unlike averaging, which invents blend colours.
export function cellModes(assign, width, height, gw, gh, k) {
  const out = new Uint8Array(gw * gh);
  const counts = new Uint32Array(k);
  for (let cy = 0; cy < gh; cy++) {
    for (let cx = 0; cx < gw; cx++) {
      counts.fill(0);
      const x0 = Math.floor((cx * width) / gw);
      const x1 = Math.max(x0 + 1, Math.floor(((cx + 1) * width) / gw));
      const y0 = Math.floor((cy * height) / gh);
      const y1 = Math.max(y0 + 1, Math.floor(((cy + 1) * height) / gh));
      for (let y = y0; y < y1; y++) for (let x = x0; x < x1; x++) counts[assign[y * width + x]]++;
      let best = 0;
      for (let c = 1; c < k; c++) if (counts[c] > counts[best]) best = c;
      out[cy * gw + cx] = best;
    }
  }
  return out;
}

// Weighted RGB distance (roughly perceptual).
function dist(a, ai, b, bi) {
  const dr = a[ai] - b[bi];
  const dg = a[ai + 1] - b[bi + 1];
  const db = a[ai + 2] - b[bi + 2];
  return 2 * dr * dr + 4 * dg * dg + 3 * db * db;
}

// One k-means run with k-means++ seeding. Returns { centers, assign, error }.
function kmeans(rgb, k, rand) {
  const n = rgb.length / 3;
  let centers = new Float32Array(k * 3);
  const d2 = new Float64Array(n).fill(Infinity);

  const first = Math.floor(rand() * n);
  centers.set(rgb.subarray(first * 3, first * 3 + 3), 0);
  let used = 1;
  for (let c = 1; c < k; c++) {
    let total = 0;
    for (let i = 0; i < n; i++) {
      d2[i] = Math.min(d2[i], dist(rgb, i * 3, centers, (c - 1) * 3));
      total += d2[i];
    }
    if (total === 0) break; // every colour already has a centre
    let r = rand() * total;
    let pick = 0;
    while (pick < n - 1 && (r -= d2[pick]) > 0) pick++;
    centers.set(rgb.subarray(pick * 3, pick * 3 + 3), c * 3);
    used++;
  }
  k = used;
  centers = centers.slice(0, k * 3);

  const assign = new Uint8Array(n);
  let error = 0;
  for (let iter = 0; iter < 30; iter++) {
    let changed = false;
    error = 0;
    for (let i = 0; i < n; i++) {
      let best = 0;
      let bestD = Infinity;
      for (let c = 0; c < k; c++) {
        const d = dist(rgb, i * 3, centers, c * 3);
        if (d < bestD) { bestD = d; best = c; }
      }
      error += bestD;
      if (assign[i] !== best) {
        assign[i] = best;
        changed = true;
      }
    }
    if (!changed && iter > 0) break;
    const sums = new Float64Array(k * 3);
    const counts = new Uint32Array(k);
    for (let i = 0; i < n; i++) {
      const c = assign[i];
      counts[c]++;
      sums[c * 3] += rgb[i * 3];
      sums[c * 3 + 1] += rgb[i * 3 + 1];
      sums[c * 3 + 2] += rgb[i * 3 + 2];
    }
    for (let c = 0; c < k; c++) {
      if (counts[c]) for (let j = 0; j < 3; j++) centers[c * 3 + j] = sums[c * 3 + j] / counts[c];
    }
  }
  return { centers, assign, error };
}

// Reduce colours to at most k with k-means (best of a few deterministic
// restarts). Returns { centers: Float32Array(k*3), assign: Uint8Array(n) }.
export function quantize(rgb, k, { seed = 1, restarts = 4 } = {}) {
  const rand = mulberry32(seed);
  k = Math.min(k, rgb.length / 3);
  let best = null;
  for (let r = 0; r < restarts; r++) {
    const run = kmeans(rgb, k, rand);
    if (!best || run.error < best.error) best = run;
  }
  return { centers: best.centers, assign: best.assign };
}

// Drop colours no cell uses and renumber the rest.
export function compact({ centers, assign }) {
  const used = [...new Set(assign)].sort((a, b) => a - b);
  const remap = new Map(used.map((c, i) => [c, i]));
  const outCenters = new Float32Array(used.length * 3);
  used.forEach((c, i) => outCenters.set(centers.subarray(c * 3, c * 3 + 3), i * 3));
  return { centers: outCenters, assign: assign.map((c) => remap.get(c)) };
}

function hex(v) {
  return Math.round(Math.max(0, Math.min(255, v))).toString(16).padStart(2, '0');
}

// Build a level definition ({ name, palette, rows }) from a quantised grid.
export function levelDef(name, gw, gh, { centers, assign }) {
  const palette = {};
  for (let c = 0; c < centers.length / 3; c++) {
    palette[KEYS[c]] = '#' + hex(centers[c * 3]) + hex(centers[c * 3 + 1]) + hex(centers[c * 3 + 2]);
  }
  const rows = [];
  for (let y = 0; y < gh; y++) {
    let row = '';
    for (let x = 0; x < gw; x++) row += KEYS[assign[y * gw + x]];
    rows.push(row);
  }
  return { name, palette, rows };
}

// Draw any canvas image source and convert it. Browser only.
export function levelFromSource(source, srcW, srcH, { name = 'My picture', maxSide = 24, colors = 6 } = {}) {
  const { gw, gh } = gridSize(srcW, srcH, maxSide);
  const cw = gw * SUPERSAMPLE;
  const ch = gh * SUPERSAMPLE;
  const canvas = document.createElement('canvas');
  canvas.width = cw;
  canvas.height = ch;
  const ctx = canvas.getContext('2d', { willReadFrequently: true });
  ctx.imageSmoothingQuality = 'high';
  ctx.drawImage(source, 0, 0, cw, ch);
  const rgb = toRGB(ctx.getImageData(0, 0, cw, ch).data);
  const { centers, assign } = quantize(rgb, colors);
  const cells = cellModes(assign, cw, ch, gw, gh, centers.length / 3);
  return levelDef(name, gw, gh, compact({ centers, assign: cells }));
}

export async function loadImageFile(file) {
  try {
    return await createImageBitmap(file);
  } catch {
    throw new Error("That file couldn't be read as an image.");
  }
}

export function nameFromFile(file) {
  const base = file.name.replace(/\.[^.]+$/, '').replace(/[_-]+/g, ' ').trim();
  return (base || 'My picture').slice(0, 24);
}
