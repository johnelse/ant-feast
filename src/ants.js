// Ant simulation: release from boxes, walk to a pixel, carry it home.

import { picRect, holePos } from './layout.js';

// The simulation is fully deterministic (no Math.random) so the solver in
// solver.js reproduces exactly what happens in the real game.
export const STEP = 1 / 120; // fixed simulation step, seconds
const SPEED = 260; // logical px per second
const RELEASE_INTERVAL = 0.12; // seconds between ants from one box

export function updateAnts(game, dt) {
  const pr = picRect(game);

  game.slots.forEach((box, si) => {
    if (!box || box.remaining <= 0) return;
    box.releaseTimer = Math.max(0, box.releaseTimer - dt);
    if (box.releaseTimer > 0 || !game.hasTarget(box.color)) return;
    const hole = holePos(si);
    const target = game.findTarget(box.color, (hole.x - pr.x) / pr.cell, (hole.y - pr.y) / pr.cell);
    game.claim(target);
    box.remaining--;
    box.out++;
    box.releaseTimer = RELEASE_INTERVAL;
    const c = cellCenter(game, pr, target);
    const serial = game.antSerial++;
    game.ants.push({
      color: box.color,
      slot: si,
      target,
      carrying: -1,
      state: 'out',
      x: hole.x + ((serial * 5) % 7) - 3,
      y: hole.y,
      tx: c.x,
      ty: c.y,
      angle: -Math.PI / 2,
      phase: serial * 1.7,
    });
  });

  const step = SPEED * dt;
  for (let i = game.ants.length - 1; i >= 0; i--) {
    const ant = game.ants[i];
    ant.phase += dt * 22;
    const dx = ant.tx - ant.x;
    const dy = ant.ty - ant.y;
    const d = Math.hypot(dx, dy);
    if (d > step) {
      ant.x += (dx / d) * step;
      ant.y += (dy / d) * step;
      ant.angle = Math.atan2(dy, dx);
      continue;
    }
    ant.x = ant.tx;
    ant.y = ant.ty;
    if (ant.state === 'out') {
      ant.carrying = game.takePixel(ant.target);
      ant.state = 'back';
      const hole = holePos(ant.slot);
      ant.tx = hole.x;
      ant.ty = hole.y;
    } else {
      game.ants.splice(i, 1);
      const box = game.slots[ant.slot];
      box.out--;
      if (box.remaining === 0 && box.out === 0) game.slots[ant.slot] = null;
    }
  }
}

export function cellCenter(game, pr, i) {
  const x = i % game.w;
  const y = Math.floor(i / game.w);
  return { x: pr.x + (x + 0.5) * pr.cell, y: pr.y + (y + 0.5) * pr.cell };
}
