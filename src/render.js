// Canvas drawing. Everything is in logical coordinates (see layout.js).

import { W, H, PIC, STACK, picRect, slotRect, stackRect, stackRowH } from './layout.js';

const BG = '#3a2c24';
const BOARD = '#f2e6cc';
const INK = '#1d1512';

export function render(ctx, game, opts = {}) {
  ctx.fillStyle = BG;
  ctx.fillRect(0, 0, W, H);

  drawPicture(ctx, game, opts.debug);
  drawSlots(ctx, game);
  drawStacks(ctx, game);
  for (const ant of game.ants) drawAnt(ctx, game, ant);
  if (opts.debug) drawDebug(ctx, game);
  if (game.status !== 'playing') drawOverlay(ctx, game);
}

// The picture is drawn into an offscreen canvas at device resolution, and
// only cells whose state changed since the last frame are repainted. Large
// pictures (40x40 = 1600 cells) are otherwise thousands of draw calls a frame,
// which is slow on phones.
let picCache = null; // { game, key, canvas, ctx, dc, state }

function drawPicture(ctx, game) {
  const pr = picRect(game);
  roundRect(ctx, PIC.x - 4, PIC.y - 4, PIC.w + 8, PIC.h + 8, 10);
  ctx.fillStyle = BOARD;
  ctx.fill();

  // Whole device pixels per cell, so repainting one cell never touches its neighbours.
  const k = ctx.getTransform().a;
  const dc = Math.max(1, Math.round(pr.cell * k));
  const key = `${dc}`;
  if (!picCache || picCache.game !== game || picCache.key !== key) {
    const canvas = document.createElement('canvas');
    canvas.width = game.w * dc;
    canvas.height = game.h * dc;
    picCache = { game, key, canvas, ctx: canvas.getContext('2d'), dc,
      state: new Int16Array(game.cells.length).fill(-2) };
  }
  const { ctx: pc, state } = picCache;
  const bevel = Math.max(1, Math.round(2 * k));
  for (let i = 0; i < game.cells.length; i++) {
    const c = game.cells[i];
    const st = c < 0 ? -1 : c * 2 + (game.claimed[i] ? 1 : 0);
    if (st === state[i]) continue;
    state[i] = st;
    const x = (i % game.w) * dc;
    const y = Math.floor(i / game.w) * dc;
    pc.clearRect(x, y, dc, dc);
    if (c < 0) continue;
    pc.globalAlpha = game.claimed[i] ? 0.55 : 1;
    pc.fillStyle = game.colors[c];
    pc.fillRect(x, y, dc, dc);
    // Soft bevel so the big pixels read as blocks.
    pc.fillStyle = 'rgba(0,0,0,0.12)';
    pc.fillRect(x, y + dc - bevel, dc, bevel);
    pc.fillRect(x + dc - bevel, y, bevel, dc - bevel);
  }
  pc.globalAlpha = 1;
  const smooth = ctx.imageSmoothingEnabled;
  ctx.imageSmoothingEnabled = false;
  ctx.drawImage(picCache.canvas, pr.x, pr.y, pr.w, pr.h);
  ctx.imageSmoothingEnabled = smooth;
}

function drawSlots(ctx, game) {
  game.slots.forEach((box, i) => {
    const r = slotRect(i);
    if (!box) {
      ctx.save();
      ctx.setLineDash([5, 4]);
      ctx.strokeStyle = 'rgba(255,255,255,0.35)';
      ctx.lineWidth = 2;
      roundRect(ctx, r.x + 2, r.y + 2, r.w - 4, r.h - 4, 8);
      ctx.stroke();
      ctx.restore();
      return;
    }
    // Ants at home / ants still belonging to the box (home + out gathering).
    drawBox(ctx, game, box, r, { hole: true, value: `${box.remaining}/${box.remaining + box.out}` });
  });
}

// The stacks only change when a box is taken or the top boxes' highlight
// changes, so they're drawn into an offscreen layer (same device pixels as
// the main canvas, from the top of the stacks down) and copied each frame.
let stackCache = null; // { key, canvas, top }

function drawStacks(ctx, game) {
  const canPlace = game.freeSlot() >= 0 && game.status === 'playing';
  const t = ctx.getTransform();
  const main = ctx.canvas;
  const key = [main.width, main.height, t.a, t.d, canPlace, game.stacks.map((s) => s.length).join(',')].join('|');
  if (!stackCache || stackCache.game !== game || stackCache.key !== key) {
    const top = Math.max(0, Math.floor((STACK.y - 6) * t.d));
    const canvas = stackCache?.canvas ?? document.createElement('canvas');
    canvas.width = main.width;
    canvas.height = Math.max(1, main.height - top);
    const sc = canvas.getContext('2d');
    sc.setTransform(t.a, 0, 0, t.d, 0, -top);
    paintStacks(sc, game, canPlace);
    stackCache = { game, key, canvas, top };
  }
  ctx.save();
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  ctx.drawImage(stackCache.canvas, 0, stackCache.top);
  ctx.restore();
}

function paintStacks(ctx, game, canPlace) {
  const rowH = stackRowH(game.deepest);
  game.stacks.forEach((stack, si) => {
    if (!stack.length) {
      const r = stackRect(si, 0);
      ctx.save();
      ctx.setLineDash([5, 4]);
      ctx.strokeStyle = 'rgba(255,255,255,0.15)';
      ctx.lineWidth = 2;
      roundRect(ctx, r.x + 3, r.y + 3, r.w - 6, r.h - 6, 8);
      ctx.stroke();
      ctx.restore();
      return;
    }
    for (let d = stack.length - 1; d >= 0; d--) {
      drawBox(ctx, game, stack[d], stackRect(si, d, rowH), {
        value: stack[d].remaining,
        compact: d > 0,
        highlight: d === 0 && canPlace,
      });
    }
  });
}

function drawBox(ctx, game, box, r, { hole = false, value, compact = false, highlight = false }) {
  const color = game.colors[box.color];
  const inset = compact ? 6 : 3;
  const x = r.x + inset;
  const y = r.y + (compact ? 1 : 3);
  const w = r.w - inset * 2;
  const h = r.h - (compact ? 2 : 6);

  roundRect(ctx, x, y, w, h, compact ? 5 : 8);
  ctx.fillStyle = color;
  ctx.fill();
  ctx.lineWidth = highlight ? 3 : 2;
  ctx.strokeStyle = highlight ? '#ffffff' : shade(color, -0.45);
  ctx.stroke();

  if (!compact) {
    // Lid band.
    ctx.fillStyle = 'rgba(0,0,0,0.12)';
    ctx.fillRect(x + 2, y + h * 0.3, w - 4, 2);
  }

  let textY = y + h / 2 + 2;
  if (hole) {
    ctx.beginPath();
    ctx.ellipse(x + w / 2, r.y + 15, 11, 5, 0, 0, Math.PI * 2);
    ctx.fillStyle = INK;
    ctx.fill();
    textY = y + h * 0.66;
  }

  // Shrink the label if it's too wide for the box (e.g. "24/24").
  const weight = compact ? 700 : 800;
  let size = compact ? Math.min(14, h - 4) : 20;
  ctx.font = `${weight} ${size}px system-ui, sans-serif`;
  while (size > 10 && ctx.measureText(String(value)).width > w - 10) {
    size--;
    ctx.font = `${weight} ${size}px system-ui, sans-serif`;
  }
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.lineWidth = compact ? 3 : 4;
  ctx.strokeStyle = 'rgba(0,0,0,0.55)';
  ctx.strokeText(String(value), x + w / 2, textY);
  ctx.fillStyle = '#ffffff';
  ctx.fillText(String(value), x + w / 2, textY);
}

function drawAnt(ctx, game, ant) {
  const color = game.colors[ant.color];
  const body = shade(color, -0.1);
  const wob = Math.sin(ant.phase * 0.5) * 1.2;
  const px = -Math.sin(ant.angle) * wob;
  const py = Math.cos(ant.angle) * wob;

  ctx.save();
  ctx.translate(ant.x + px, ant.y + py);
  ctx.rotate(ant.angle);
  ctx.scale(1.15, 1.15);

  // Legs: three pairs, alternating swing.
  ctx.strokeStyle = INK;
  ctx.lineWidth = 1;
  ctx.beginPath();
  for (let k = -1; k <= 1; k++) {
    const swing = Math.sin(ant.phase + k * 2) * 1.6;
    ctx.moveTo(k * 2, 0);
    ctx.lineTo(k * 2.5 + swing, -5);
    ctx.moveTo(k * 2, 0);
    ctx.lineTo(k * 2.5 - swing, 5);
  }
  // Antennae.
  ctx.moveTo(5.5, -1);
  ctx.lineTo(8.5, -3.5);
  ctx.moveTo(5.5, 1);
  ctx.lineTo(8.5, 3.5);
  ctx.stroke();

  ctx.fillStyle = body;
  ctx.strokeStyle = INK;
  ctx.lineWidth = 1;
  for (const [cx, rx, ry] of [[-5, 3.6, 2.8], [0, 2.2, 1.8], [4.2, 2.2, 2.1]]) {
    ctx.beginPath();
    ctx.ellipse(cx, 0, rx, ry, 0, 0, Math.PI * 2);
    ctx.fill();
    ctx.stroke();
  }

  if (ant.carrying >= 0) {
    ctx.fillStyle = game.colors[ant.carrying];
    ctx.fillRect(7, -3.5, 7, 7);
    ctx.strokeRect(7, -3.5, 7, 7);
  }
  ctx.restore();
}

function drawDebug(ctx, game) {
  const pr = picRect(game);
  ctx.strokeStyle = '#00e5ff';
  ctx.lineWidth = 1;
  for (let i = 0; i < game.cells.length; i++) {
    if (!game.isExposed(i)) continue;
    const x = pr.x + (i % game.w) * pr.cell;
    const y = pr.y + Math.floor(i / game.w) * pr.cell;
    ctx.strokeRect(x + 1.5, y + 1.5, pr.cell - 3, pr.cell - 3);
  }
  // Remaining route of each ant on its way out.
  ctx.strokeStyle = 'rgba(255,255,0,0.5)';
  for (const ant of game.ants) {
    if (ant.state !== 'out') continue;
    ctx.beginPath();
    ctx.moveTo(ant.x, ant.y);
    for (let k = ant.k; k < ant.path.length; k++) ctx.lineTo(ant.path[k].x, ant.path[k].y);
    ctx.stroke();
  }
}

function drawOverlay(ctx, game) {
  ctx.fillStyle = 'rgba(20,12,8,0.7)';
  ctx.fillRect(0, 0, W, H);
  const won = game.status === 'won';
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.fillStyle = won ? '#ffe082' : '#ff8a80';
  ctx.font = '800 34px system-ui, sans-serif';
  ctx.fillText(won ? 'Picture cleared!' : 'No moves left', W / 2, H / 2 - 24);
  ctx.fillStyle = '#ffffff';
  ctx.font = '500 18px system-ui, sans-serif';
  ctx.fillText(won ? 'Tap for the next picture' : 'Tap to try again', W / 2, H / 2 + 20);
}

function roundRect(ctx, x, y, w, h, r) {
  ctx.beginPath();
  ctx.moveTo(x + r, y);
  ctx.arcTo(x + w, y, x + w, y + h, r);
  ctx.arcTo(x + w, y + h, x, y + h, r);
  ctx.arcTo(x, y + h, x, y, r);
  ctx.arcTo(x, y, x + w, y, r);
  ctx.closePath();
}

// Lighten (amt > 0) or darken (amt < 0) a #rrggbb colour.
function shade(hex, amt) {
  const n = parseInt(hex.slice(1), 16);
  const ch = [(n >> 16) & 255, (n >> 8) & 255, n & 255].map((v) =>
    Math.round(amt < 0 ? v * (1 + amt) : v + (255 - v) * amt));
  return `rgb(${ch[0]},${ch[1]},${ch[2]})`;
}
