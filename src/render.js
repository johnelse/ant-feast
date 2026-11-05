// Canvas drawing. Everything is in logical coordinates (see layout.js).

import { W, H, PIC, picRect, slotRect, stackRect } from './layout.js';
import { cellCenter } from './ants.js';

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

function drawPicture(ctx, game) {
  const pr = picRect(game);
  roundRect(ctx, PIC.x - 4, PIC.y - 4, PIC.w + 8, PIC.h + 8, 10);
  ctx.fillStyle = BOARD;
  ctx.fill();

  for (let i = 0; i < game.cells.length; i++) {
    const c = game.cells[i];
    if (c < 0) continue;
    const x = pr.x + (i % game.w) * pr.cell;
    const y = pr.y + Math.floor(i / game.w) * pr.cell;
    ctx.globalAlpha = game.claimed[i] ? 0.55 : 1;
    ctx.fillStyle = game.colors[c];
    ctx.fillRect(x, y, pr.cell, pr.cell);
    // Soft bevel so the big pixels read as blocks.
    ctx.fillStyle = 'rgba(0,0,0,0.12)';
    ctx.fillRect(x, y + pr.cell - 2, pr.cell, 2);
    ctx.fillRect(x + pr.cell - 2, y, 2, pr.cell - 2);
  }
  ctx.globalAlpha = 1;
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
    drawBox(ctx, game, box, r, { hole: true, value: box.remaining });
  });
}

function drawStacks(ctx, game) {
  const canPlace = game.freeSlot() >= 0 && game.status === 'playing';
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
      drawBox(ctx, game, stack[d], stackRect(si, d), {
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

  ctx.font = compact ? '700 14px system-ui, sans-serif' : '800 20px system-ui, sans-serif';
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
  ctx.strokeStyle = 'rgba(255,255,0,0.5)';
  for (const ant of game.ants) {
    if (ant.state !== 'out') continue;
    const c = cellCenter(game, pr, ant.target);
    ctx.beginPath();
    ctx.moveTo(ant.x, ant.y);
    ctx.lineTo(c.x, c.y);
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
