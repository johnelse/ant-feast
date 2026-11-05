// Replays a level's stored solution (a string of stack numbers), waiting for
// everything to settle between moves. Used by ?auto and test/sim.html.
import { STEP } from './ants.js';

export function makeReplayer(solution) {
  const moves = [...solution].map(Number);
  let next = 0;
  let idle = 0;
  return function step(game) {
    if (game.status !== 'playing' || next >= moves.length) return;
    idle = game.isBusy() ? 0 : idle + STEP;
    if (idle >= 0.2) {
      game.placeBox(moves[next++]);
      idle = 0;
    }
  };
}
