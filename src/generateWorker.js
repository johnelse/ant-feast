// Runs the deal generator off the main thread, in short time slices so it
// can report progress and respond to "finish now" requests.
//
// in:  { type: 'start', image, options }   image as from parseLevel()
//      { type: 'finish' }                  stop and return the best so far
// out: { type: 'progress', it, iterations, phase, ready, difficulty }
//      { type: 'done', result }            result null if nothing was found

import { generateDealSteps, difficultyLabel } from './generate.js';
import { formatDeal } from './image.js';

let job = null;

self.onmessage = (e) => {
  const msg = e.data;
  if (msg.type === 'start') {
    job = { steps: generateDealSteps(msg.image, msg.options), image: msg.image, last: null, finish: false };
    setTimeout(pump, 0);
  } else if (msg.type === 'finish' && job) {
    job.finish = true;
  }
};

function pack(deal, best) {
  return {
    deal: formatDeal(deal, job.image),
    solution: best.solution.join(''),
    rg: best.rg,
    rr: best.rr,
    greedyWins: best.greedyWins,
    difficulty: difficultyLabel(best),
  };
}

function done(result) {
  self.postMessage({ type: 'done', result });
  job = null;
}

function pump() {
  if (!job) return;
  const until = performance.now() + 50;
  while (performance.now() < until) {
    const r = job.steps.next();
    if (r.done) return done(r.value ? pack(r.value.deal, r.value) : null);
    job.last = r.value;
    if (job.finish && r.value.best) return done(pack(r.value.deal, r.value.best));
  }
  const { phase, it, iterations, best } = job.last;
  self.postMessage({
    type: 'progress', phase, it, iterations,
    ready: !!best,
    difficulty: best ? difficultyLabel(best) : null,
  });
  setTimeout(pump, 0);
}
