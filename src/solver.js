// Solver and difficulty measurement for box deals.
//
// The model is "place a box, then wait until everything settles". That's a
// restriction on the player (a real player may act sooner), so any deal the
// solver wins is winnable in the real game by playing the same moves and
// waiting between them.

import { updateAnts, STEP } from './ants.js';
import { mulberry32 } from './state.js';

const MAX_SETTLE_STEPS = 120 * 120; // two minutes of game time, a safety net

// Run the simulation until nothing more can happen without the player.
export function settle(game) {
  for (let n = 0; n < MAX_SETTLE_STEPS && game.isBusy(); n++) updateAnts(game, STEP);
  // A player who waits has let every release timer run down.
  for (const b of game.slots) if (b) b.releaseTimer = 0;
  game.updateStatus();
  return game;
}

export function legalMoves(game) {
  if (game.status !== 'playing' || game.freeSlot() < 0) return [];
  const moves = [];
  game.stacks.forEach((s, i) => { if (s.length) moves.push(i); });
  return moves;
}

function stateKey(game) {
  let h = 2166136261;
  for (let i = 0; i < game.cells.length; i++) h = Math.imul(h ^ (game.cells[i] + 1), 16777619);
  return game.stacks.map((s) => s.length).join(',') + '|' +
    game.slots.map((b) => (b ? `${b.id}:${b.remaining}` : '-')).join(',') + '|' + (h >>> 0);
}

// Depth-first search for a winning sequence of stack indices.
// Returns { solution: number[] | null, nodes, complete } where complete=false
// means the node budget ran out before the search finished.
export function solve(start, { maxNodes = 20000 } = {}) {
  let nodes = 0;
  const seen = new Set();

  function dfs(game) {
    if (game.status === 'won') return [];
    if (game.status !== 'playing' || nodes >= maxNodes) return null;
    const key = stateKey(game);
    if (seen.has(key)) return null;
    seen.add(key);
    nodes++;
    // Try boxes that can start eating straight away first.
    const moves = legalMoves(game).sort((a, b) =>
      game.hasTarget(game.stacks[b][0].color) - game.hasTarget(game.stacks[a][0].color));
    for (const m of moves) {
      const next = game.clone();
      next.placeBox(m);
      settle(next);
      const rest = dfs(next);
      if (rest) return [m, ...rest];
    }
    return null;
  }

  const solution = dfs(settle(start.clone()));
  return { solution, nodes, complete: solution !== null || nodes < maxNodes };
}

export function playout(start, choose) {
  const game = settle(start.clone());
  while (game.status === 'playing') {
    const moves = legalMoves(game);
    if (!moves.length) break;
    game.placeBox(choose(game, moves));
    settle(game);
  }
  return game.status === 'won';
}

// "Take anything that can eat right now, else the first stack."
export function greedyChoice(game, moves) {
  return moves.find((m) => game.hasTarget(game.stacks[m][0].color)) ?? moves[0];
}

// Same preference, but picks randomly among the boxes that can eat.
export function randomGreedyChooser(rand) {
  return (game, moves) => {
    const eat = moves.filter((m) => game.hasTarget(game.stacks[m][0].color));
    const pool = eat.length ? eat : moves;
    return pool[Math.floor(rand() * pool.length)];
  };
}

export function randomChooser(rand) {
  return (game, moves) => moves[Math.floor(rand() * moves.length)];
}

// Difficulty report for a deal. Win rates are for unthinking players: lower
// means more planning is needed. solvable must be true for a fair level.
export function evaluate(game, { trials = 40, maxNodes = 20000 } = {}) {
  const rand = mulberry32(12345);
  const greedyWins = playout(game, greedyChoice);
  let rg = 0;
  let rr = 0;
  const rgChoose = randomGreedyChooser(rand);
  const rrChoose = randomChooser(rand);
  for (let t = 0; t < trials; t++) {
    if (playout(game, rgChoose)) rg++;
    if (playout(game, rrChoose)) rr++;
  }
  return {
    greedyWins,
    randomGreedyRate: rg / trials,
    randomRate: rr / trials,
    ...(() => {
      const r = solve(game, { maxNodes });
      return { solvable: !!r.solution, solution: r.solution, nodes: r.nodes, complete: r.complete };
    })(),
  };
}

// Win rate of `chooser` starting after the first k moves of a known
// solution, or null if the game is already over by then.
export function winRateAfter(start, solution, k, chooser, trials) {
  const game = settle(start.clone());
  for (let i = 0; i < k && game.status === 'playing'; i++) {
    game.placeBox(solution[i]);
    settle(game);
  }
  if (game.status !== 'playing') return null;
  let wins = 0;
  for (let t = 0; t < trials; t++) if (playout(game, chooser)) wins++;
  return wins / trials;
}

// How hard a deal stays as it goes on: unthinking win rates from the start
// and after the first k moves of a solution (sensible play up to that point).
// A deal that's only hard in the opening shows low rates at k=0 and high
// rates later.
export function difficultyProfile(start, solution, { checkpoints = [0, 5, 10, 15], trials = 40, seed = 4242 } = {}) {
  return checkpoints.filter((k) => k < solution.length).map((k) => ({
    k,
    rg: winRateAfter(start, solution, k, randomGreedyChooser(mulberry32(seed + k)), trials),
    rr: winRateAfter(start, solution, k, randomChooser(mulberry32(seed + 1000 + k)), trials),
  }));
}
