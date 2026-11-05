// Ant simulation: release from boxes, walk round the picture to the side
// nearest the target pixel, wind in through the cleared gaps, and carry the
// pixel home the same way.

import { picRect, holePos } from './layout.js';

// The simulation is fully deterministic (no Math.random) so the solver in
// solver.js reproduces exactly what happens in the real game.
export const STEP = 1 / 120; // fixed simulation step, seconds
const SPEED = 320; // logical px per second
const RELEASE_INTERVAL = 0.12; // seconds between ants from one box
const TURN_RATE = 18; // how quickly the drawn heading follows the path

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
    const serial = game.antSerial++;
    const x = hole.x + ((serial * 5) % 7) - 3;
    const path = planPath(game, pr, hole, target);
    game.ants.push({
      color: box.color,
      slot: si,
      target,
      carrying: -1,
      state: 'out',
      x,
      y: hole.y,
      path,
      k: 0, // index of the next waypoint
      home: { x, y: hole.y },
      angle: -Math.PI / 2,
      phase: serial * 1.7,
    });
  });

  for (let i = game.ants.length - 1; i >= 0; i--) {
    const ant = game.ants[i];
    ant.phase += dt * 22;
    if (!advance(ant, SPEED * dt, dt)) continue;
    if (ant.state === 'out') {
      ant.carrying = game.takePixel(ant.target);
      ant.state = 'back';
      // Retrace the route, then drop back down the hole.
      ant.path = ant.path.slice(0, -1).reverse();
      ant.path.push(ant.home);
      ant.k = 0;
    } else {
      game.ants.splice(i, 1);
      const box = game.slots[ant.slot];
      box.out--;
      if (box.remaining === 0 && box.out === 0) game.slots[ant.slot] = null;
    }
  }
}

// Move along the waypoints by `dist`. Returns true on reaching the last one.
function advance(ant, dist, dt) {
  while (ant.k < ant.path.length) {
    const p = ant.path[ant.k];
    const dx = p.x - ant.x;
    const dy = p.y - ant.y;
    const d = Math.hypot(dx, dy);
    if (d > 0) turnTowards(ant, Math.atan2(dy, dx), dt);
    if (d > dist) {
      ant.x += (dx / d) * dist;
      ant.y += (dy / d) * dist;
      return false;
    }
    ant.x = p.x;
    ant.y = p.y;
    dist -= d;
    ant.k++;
  }
  return true;
}

function turnTowards(ant, heading, dt) {
  let diff = heading - ant.angle;
  diff = Math.atan2(Math.sin(diff), Math.cos(diff));
  ant.angle += diff * Math.min(1, dt * TURN_RATE);
}

// Waypoints from the hole to the target: up onto the track round the
// picture, along it (the shorter way) to the entry point nearest the target,
// then through cleared cells to the target itself.
function planPath(game, pr, hole, target) {
  const { w, h } = game;
  const route = game.routeTo(target);
  const [ex, ey] = route[0];
  const sx = Math.max(-1, Math.min(w, Math.floor((hole.x - pr.x) / pr.cell)));
  const cells = trackWalk(w, h, sx, h, ex, ey);
  for (let j = 1; j < route.length; j++) cells.push(route[j]);
  return cells.map(([x, y]) => ({ x: pr.x + (x + 0.5) * pr.cell, y: pr.y + (y + 0.5) * pr.cell }));
}

// Position of a track cell, counting clockwise from the top-left corner.
function trackPos(w, h, x, y) {
  if (y === -1) return x + 1;
  if (x === w) return w + 1 + (y + 1);
  if (y === h) return 2 * (w + 1) + (h + 1) - (x + 1);
  return 2 * (w + 1) + 2 * (h + 1) - (y + 1);
}

function trackCell(w, h, t) {
  const L = 2 * (w + 1) + 2 * (h + 1);
  t = ((t % L) + L) % L;
  if (t <= w + 1) return [t - 1, -1];
  if (t <= w + 1 + h + 1) return [w, t - (w + 1) - 1];
  if (t <= 2 * (w + 1) + h + 1) return [w - (t - (w + 1) - (h + 1)), h];
  return [-1, h - (t - 2 * (w + 1) - (h + 1))];
}

// Track cells from (ax, ay) to (bx, by) inclusive, going the shorter way.
function trackWalk(w, h, ax, ay, bx, by) {
  const L = 2 * (w + 1) + 2 * (h + 1);
  const a = trackPos(w, h, ax, ay);
  const b = trackPos(w, h, bx, by);
  const fwd = (b - a + L) % L;
  const dir = fwd <= L - fwd ? 1 : -1;
  const steps = dir === 1 ? fwd : L - fwd;
  const cells = [];
  for (let s = 0; s <= steps; s++) cells.push(trackCell(w, h, a + dir * s));
  return cells;
}

export function cellCenter(game, pr, i) {
  const x = i % game.w;
  const y = Math.floor(i / game.w);
  return { x: pr.x + (x + 0.5) * pr.cell, y: pr.y + (y + 0.5) * pr.cell };
}
