// Builds box deals that need thought: solvable, but not by unthinking play.
//
// Starts from a random deal and hill-climbs with small mutations (swap two
// boxes, move a box to another stack, shift ants between two boxes of the same
// colour). A candidate is kept if it stays fair (the solver wins it), the
// "take anything that can eat" player loses (penalised until it does), and
// unthinking players win it no more often than before.

import { Game, mulberry32, randomDeal, STACK_COUNT } from './state.js';
import { evaluate, solve, settle, playout, greedyChoice, randomGreedyChooser, randomChooser } from './solver.js';

const MAX_STACK = 9;

function cloneDeal(deal) {
  return deal.map((s) => s.map((b) => ({ ...b })));
}

function mutate(deal, rand, { boxMin, boxMax }) {
  const d = cloneDeal(deal);
  const pick = () => {
    const s = Math.floor(rand() * STACK_COUNT);
    return d[s].length ? [s, Math.floor(rand() * d[s].length)] : null;
  };
  const kind = rand();
  if (kind < 0.45) {
    const a = pick();
    const b = pick();
    if (a && b) [d[a[0]][a[1]], d[b[0]][b[1]]] = [d[b[0]][b[1]], d[a[0]][a[1]]];
  } else if (kind < 0.75) {
    const a = pick();
    const to = Math.floor(rand() * STACK_COUNT);
    if (a && to !== a[0] && d[to].length < MAX_STACK && d[a[0]].length > 2) {
      const [box] = d[a[0]].splice(a[1], 1);
      d[to].splice(Math.floor(rand() * (d[to].length + 1)), 0, box);
    }
  } else {
    // Move ants between two boxes of the same colour.
    const all = d.flat();
    const a = all[Math.floor(rand() * all.length)];
    const same = all.filter((b) => b !== a && b.color === a.color);
    if (same.length) {
      const b = same[Math.floor(rand() * same.length)];
      const k = 1 + Math.floor(rand() * 6);
      if (a.count - k >= boxMin && b.count + k <= boxMax) {
        a.count -= k;
        b.count += k;
      }
    }
  }
  return d;
}

function winRate(game, chooser, trials) {
  let wins = 0;
  for (let t = 0; t < trials; t++) if (playout(game, chooser)) wins++;
  return wins / trials;
}

// Lower is harder.
function quickScore(game, trials) {
  const rg = winRate(game, randomGreedyChooser(mulberry32(777)), trials);
  const rr = winRate(game, randomChooser(mulberry32(999)), trials);
  return { value: rg + 0.5 * rr, rg, rr };
}

// A deal that is certainly solvable: play from a pool of all the boxes,
// always picking one that can eat, and deal the boxes onto the stacks in the
// order they were used. Used when random starting deals don't work out.
function sequenceDeal(image, pixels, rand, { boxMin, boxMax }) {
  const boxes = randomDeal(pixels, Math.floor(rand() * 1e9), { boxMin, boxMax }).flat();
  const game = settle(new Game(image, 0, { deal: [boxes, [], [], []] }));
  const order = [];
  while (game.status === 'playing') {
    const pool = game.stacks[0];
    if (!pool.length || game.freeSlot() < 0) break;
    const eat = pool.map((_, i) => i).filter((i) => game.hasTarget(pool[i].color));
    const pick = eat.length ? eat[Math.floor(rand() * eat.length)] : Math.floor(rand() * pool.length);
    const [box] = pool.splice(pick, 1);
    pool.unshift(box);
    order.push({ color: box.color, count: box.count });
    game.placeBox(0);
    settle(game);
  }
  if (game.status !== 'won') return null;
  const stacks = Array.from({ length: STACK_COUNT }, () => []);
  order.forEach((b, i) => stacks[i % STACK_COUNT].push(b));
  return stacks;
}

// Generator version, so callers can time-slice it (see generateWorker.js).
// Yields { phase, it, iterations, deal, best } after each unit of work;
// returns { deal, ...best } or null if no solvable deal was found.
export function* generateDealSteps(image, {
  seed = 1,
  boxMin = 6,
  boxMax = 24,
  iterations = 200,
  trials = 16,
  maxNodes = 4000,
  target = 0, // stop early once the score reaches this
  patience = Infinity, // stop after this many steps without improvement
  startTries = 12,
} = {}) {
  const rand = mulberry32(seed);
  const pixels = new Array(image.colors.length).fill(0);
  for (const c of image.cells) pixels[c]++;

  // Score = unthinking win rates, plus a penalty while greedy play still
  // wins, so the climb can make progress towards deals that beat it.
  const check = (deal, bestValue) => {
    const game = new Game(image, 0, { deal });
    const q = quickScore(game, trials);
    const greedyWins = playout(game, greedyChoice);
    const value = q.value + (greedyWins ? 1 : 0);
    if (value > bestValue) return null; // not an improvement, skip the solver
    const { solution, complete } = solve(game, { maxNodes });
    if (!solution || !complete) return null;
    return { ...q, value, greedyWins, solution };
  };

  let deal = null;
  let best = null;
  for (let s = 0; s < startTries && !best; s++) {
    deal = randomDeal(pixels, seed + s * 7919, { boxMin, boxMax });
    best = check(deal, Infinity);
    yield { phase: 'start', it: 0, iterations, deal: best ? deal : null, best };
  }
  for (let s = 0; s < startTries && !best; s++) {
    deal = sequenceDeal(image, pixels, rand, { boxMin, boxMax });
    best = deal && check(deal, Infinity);
    yield { phase: 'start', it: 0, iterations, deal: best ? deal : null, best };
  }
  if (!best) return null;

  let lastGain = 0;
  for (let it = 0; it < iterations && best.value > target && it - lastGain < patience; it++) {
    let cand = mutate(deal, rand, { boxMin, boxMax });
    while (rand() < 0.3) cand = mutate(cand, rand, { boxMin, boxMax });
    const r = check(cand, best.value);
    if (r) {
      if (r.value < best.value) lastGain = it;
      deal = cand;
      best = r;
    }
    yield { phase: 'climb', it: it + 1, iterations, deal, best };
  }
  return { deal, ...best };
}

export function generateDeal(image, opts = {}) {
  const steps = generateDealSteps(image, opts);
  for (;;) {
    const r = steps.next();
    if (r.done) return r.value;
    opts.onProgress?.(r.value);
  }
}

// Rough difficulty label from a generator score.
export function difficultyLabel(best) {
  if (!best || best.greedyWins) return 'easy';
  if (best.rg > 0.5) return 'medium';
  if (best.rg > 0.2) return 'hard';
  return 'very hard';
}

export function fullReport(image, deal, trials = 100) {
  return evaluate(new Game(image, 0, { deal }), { trials, maxNodes: 20000 });
}
