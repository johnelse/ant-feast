// Fixed logical layout; the canvas is scaled to fit the window.

export const W = 420;
export const H = 772;

export const PIC = { x: 16, y: 14, w: 388, h: 368 };

export const SLOT = { y: 400, w: 68, h: 66, gap: 8, count: 5 };
SLOT.x0 = (W - (SLOT.count * SLOT.w + (SLOT.count - 1) * SLOT.gap)) / 2;

// Top box is full size; the boxes beneath it are compact rows.
export const STACK = { y: 494, w: 84, h: 52, gap: 12, rowH: 26, count: 4 };
STACK.x0 = (W - (STACK.count * STACK.w + (STACK.count - 1) * STACK.gap)) / 2;

// The picture leaves one cell of board all round it: the track ants walk on.
export function picRect(game) {
  const cell = Math.floor(Math.min(PIC.w / (game.w + 2), PIC.h / (game.h + 2)));
  const w = cell * game.w;
  const h = cell * game.h;
  return {
    cell, w, h,
    x: Math.round(PIC.x + (PIC.w - w) / 2),
    y: Math.round(PIC.y + (PIC.h - h) / 2),
  };
}

export function slotRect(i) {
  return { x: SLOT.x0 + i * (SLOT.w + SLOT.gap), y: SLOT.y, w: SLOT.w, h: SLOT.h };
}

export function holePos(i) {
  const r = slotRect(i);
  return { x: r.x + r.w / 2, y: r.y + 15 };
}

export function stackRect(i, depth = 0) {
  const x = STACK.x0 + i * (STACK.w + STACK.gap);
  if (depth === 0) return { x, y: STACK.y, w: STACK.w, h: STACK.h };
  return { x, y: STACK.y + STACK.h + 2 + (depth - 1) * STACK.rowH, w: STACK.w, h: STACK.rowH };
}

export function contains(r, x, y) {
  return x >= r.x && x <= r.x + r.w && y >= r.y && y <= r.y + r.h;
}
