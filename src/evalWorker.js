// Scores box deals for the parallel generator (see parallel.js).
//
// in:  { type: 'init', image, opts }               once, before any tasks
//      { id, type: 'check', deal, bestValue }      score this deal
//      { id, type: 'random', seed, bestValue }     make a random deal and score it
//      { id, type: 'sequence', seed, bestValue }   make a certainly-solvable deal and score it
// out: { id, deal, result }   result is checkDeal()'s, or null

import { checkDeal, sequenceDeal, pixelCounts } from './generate.js';
import { randomDeal, mulberry32 } from './state.js';

let image = null;
let opts = null;
let pixels = null;

self.onmessage = (e) => {
  const msg = e.data;
  if (msg.type === 'init') {
    image = msg.image;
    opts = msg.opts;
    pixels = pixelCounts(image);
    return;
  }
  let deal = msg.deal ?? null;
  if (msg.type === 'random') deal = randomDeal(pixels, msg.seed, opts);
  if (msg.type === 'sequence') deal = sequenceDeal(image, pixels, mulberry32(msg.seed), opts);
  const result = deal ? checkDeal(image, deal, msg.bestValue ?? Infinity, opts) : null;
  self.postMessage({ id: msg.id, deal, result });
};
