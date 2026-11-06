// Parallel deal generator: hill-climbs box deals using a pool of workers
// (evalWorker.js), each scoring candidates independently.
//
// Steady-state, not lock-step: whenever a worker finishes, its candidate is
// compared with the best so far, and the worker immediately gets a fresh
// mutation of the current best. Because results arrive in whatever order the
// workers finish, runs aren't exactly repeatable, but every returned deal is
// verified solvable by the solver.
//
//   const job = generateDealParallel(image, { iterations: 300, onProgress });
//   job.finish();  // stop now and resolve with the best so far
//   job.cancel();  // stop now and resolve with null
//   const result = await job.promise;  // { deal, value, rg, rr, greedyWins, solution, ... } or null

import { mutateChain, DEFAULT_CHECKPOINTS } from './generate.js';
import { mulberry32 } from './state.js';

export function defaultWorkerCount() {
  const cores = (typeof navigator !== 'undefined' && navigator.hardwareConcurrency) || 4;
  return Math.max(1, Math.min(16, cores - 1));
}

export function generateDealParallel(image, {
  seed = 1,
  boxMin = 6,
  boxMax = 24,
  iterations = 200, // candidate deals to score while climbing
  trials = 16,
  maxNodes = 4000,
  target = 0, // stop early once the score reaches this
  patience = Infinity, // stop after this many scored candidates without improvement
  startTries = 12,
  objective = 'start',
  checkpoints = DEFAULT_CHECKPOINTS,
  startDeal = null, // e.g. a level's current deal, to keep improving it
  workers = defaultWorkerCount(),
  onProgress = () => {},
} = {}) {
  const pool = Array.from({ length: workers },
    () => new Worker(new URL('./evalWorker.js', import.meta.url), { type: 'module' }));
  const checkOpts = { boxMin, boxMax, trials, maxNodes, objective, checkpoints };
  for (const w of pool) w.postMessage({ type: 'init', image, opts: checkOpts });

  let deal = null;
  let best = null;
  let finished = false;
  let wantFinish = false;
  let resolveJob;
  const promise = new Promise((r) => { resolveJob = r; });

  const end = (result) => {
    if (finished) return;
    finished = true;
    for (const w of pool) w.terminate();
    resolveJob(result);
  };
  const bestResult = () => (best ? { deal, ...best } : null);

  // Request/response over each worker.
  let nextId = 0;
  const pending = new Map();
  for (const w of pool) {
    w.onmessage = (e) => {
      const done = pending.get(e.data.id);
      pending.delete(e.data.id);
      done?.(e.data);
    };
    w.onerror = (e) => {
      console.error('deal worker failed:', e.message);
      end(bestResult());
    };
  }
  const run = (w, msg) => new Promise((resolve) => {
    const id = nextId++;
    pending.set(id, resolve);
    w.postMessage({ ...msg, id });
  });

  // Run a list of tasks across the pool; resolves with all replies.
  const runAll = (tasks) => new Promise((resolve) => {
    const replies = [];
    let next = 0;
    let active = 0;
    const feed = (w) => {
      if (finished || next >= tasks.length) {
        if (active === 0) resolve(replies);
        return;
      }
      const task = tasks[next++];
      active++;
      run(w, task).then((reply) => {
        active--;
        replies.push(reply);
        feed(w);
      });
    };
    pool.forEach(feed);
  });

  const adoptBest = (replies) => {
    for (const r of replies) {
      if (r.result && (!best || r.result.value < best.value)) {
        deal = r.deal;
        best = r.result;
      }
    }
  };

  const progress = (phase, it) =>
    onProgress({ phase, it, iterations, ready: !!best, deal, best });

  (async () => {
    // Starting point: the given deal, else random deals, else deals built
    // from a winning play order (always solvable, but usually easy).
    if (startDeal) adoptBest(await runAll([{ type: 'check', deal: startDeal }]));
    progress('start', 0);
    if (!best) {
      adoptBest(await runAll(Array.from({ length: startTries }, (_, s) => ({ type: 'random', seed: seed + s * 7919 }))));
      progress('start', 0);
    }
    if (!best) {
      adoptBest(await runAll(Array.from({ length: startTries }, (_, s) => ({ type: 'sequence', seed: seed * 1000 + s }))));
      progress('start', 0);
    }
    if (!best || finished) return end(bestResult());
    if (wantFinish) return end(bestResult());

    // Climb.
    const rand = mulberry32(seed);
    let dispatched = 0;
    let scored = 0;
    let lastGain = 0;
    let active = 0;
    const stop = () => wantFinish || dispatched >= iterations || best.value <= target || scored - lastGain >= patience;
    const feed = (w) => {
      if (finished) return;
      if (stop()) {
        if (active === 0) end(bestResult());
        return;
      }
      const cand = mutateChain(deal, rand, { boxMin, boxMax });
      dispatched++;
      active++;
      run(w, { type: 'check', deal: cand, bestValue: best.value }).then((reply) => {
        active--;
        scored++;
        const r = reply.result;
        if (r && r.value <= best.value) {
          if (r.value < best.value) lastGain = scored;
          deal = cand;
          best = r;
        }
        progress('climb', scored);
        feed(w);
      });
    };
    pool.forEach(feed);
  })();

  return {
    promise,
    // Stop and return the best deal so far (waits for a first solvable deal
    // if none has been found yet).
    finish() {
      wantFinish = true;
      if (best) end(bestResult());
    },
    cancel() {
      end(null);
    },
  };
}
