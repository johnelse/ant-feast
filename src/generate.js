// Building blocks for making box deals that need thought: solvable, but not
// by unthinking play. The search itself (hill-climbing over mutations: swap
// two boxes, move a box to another stack, shift ants between two boxes of the
// same colour) runs in parallel across workers; see parallel.js.

import { Game, mulberry32, randomDeal, STACK_COUNT } from './state.js';
import { evaluate, solve, settle, playout, winRateAfter, greedyChoice, randomGreedyChooser, randomChooser } from './solver.js';

const MAX_STACK = 16; // the stack layout squeezes rows to fit this many

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
export function sequenceDeal(image, pixels, rand, { boxMin, boxMax }) {
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

export const DEFAULT_CHECKPOINTS = [0, 0.2, 0.4, 0.6, 0.75];

// Score one deal. Lower values are harder. Returns null if the deal isn't
// solvable, or (to save time) as soon as it clearly can't beat `bestValue`.
//   objective 'start': unthinking win rates from the first move only.
//   objective 'sustained': averaged over several points through the solution
//     (`checkpoints`, as fractions of its length), so deals stay hard after
//     a sensible opening and into the late game.
// Greedy play winning adds a penalty of 1, so a climb can still make
// progress towards deals that beat it.
export function checkDeal(image, deal, bestValue = Infinity, {
  objective = 'start',
  trials = 16,
  maxNodes = 4000,
  checkpoints = DEFAULT_CHECKPOINTS,
} = {}) {
  const game = new Game(image, 0, { deal });
  const greedyWins = playout(game, greedyChoice);
  const penalty = greedyWins ? 1 : 0;
  if (objective === 'start') {
    const q = quickScore(game, trials);
    const value = q.value + penalty;
    if (value > bestValue) return null; // not an improvement, skip the solver
    const { solution, complete } = solve(game, { maxNodes });
    if (!solution || !complete) return null;
    return { ...q, value, greedyWins, solution };
  }
  const { solution, complete } = solve(game, { maxNodes });
  if (!solution || !complete) return null;
  const ks = [...new Set(checkpoints.map((f) => Math.floor(f * solution.length)))];
  const profile = [];
  let sum = 0;
  for (const k of ks) {
    const rg = winRateAfter(game, solution, k, randomGreedyChooser(mulberry32(777 + k)), trials);
    const rr = winRateAfter(game, solution, k, randomChooser(mulberry32(999 + k)), trials);
    profile.push({ k, rg, rr });
    sum += rg + 0.5 * rr;
    if (penalty + sum / ks.length > bestValue) return null; // can't beat the best any more
  }
  const value = penalty + sum / ks.length;
  return { value, rg: profile[0].rg, rr: profile[0].rr, profile, greedyWins, solution };
}

// One climbing step: a mutation, sometimes followed by a few more.
export function mutateChain(deal, rand, opts) {
  let d = mutate(deal, rand, opts);
  while (rand() < 0.3) d = mutate(d, rand, opts);
  return d;
}

export function pixelCounts(image) {
  const pixels = new Array(image.colors.length).fill(0);
  for (const c of image.cells) pixels[c]++;
  return pixels;
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
