// Shared picture format used by the game:
//   { width, height, colors: ['#rrggbb', ...], keys: ['r', ...], cells: Int8Array }
// cells[y * width + x] is an index into colors. Pictures are complete
// rectangles, so every cell is filled. keys are short names for the colours,
// used to write box deals (see parseDeal).
//
// parseLevel() builds this from hand-made character grids. A future
// image loader (downscale + quantise a PNG to ~8 colours) only needs to
// return the same structure.

export function parseLevel(def) {
  const { rows, palette } = def;
  const height = rows.length;
  const width = rows[0].length;
  const colors = [];
  const keys = [];
  const indexOf = new Map();
  const cells = new Int8Array(width * height).fill(-1);

  rows.forEach((row, y) => {
    if (row.length !== width) {
      throw new Error(`${def.name}: row ${y} has length ${row.length}, expected ${width}`);
    }
    for (let x = 0; x < width; x++) {
      const ch = row[x];
      if (!(ch in palette)) throw new Error(`${def.name}: unknown colour '${ch}' at ${x},${y}`);
      if (!indexOf.has(ch)) {
        indexOf.set(ch, colors.length);
        colors.push(normalizeHex(palette[ch]));
        keys.push(ch);
      }
      cells[y * width + x] = indexOf.get(ch);
    }
  });

  return { width, height, colors, keys, cells };
}

// Deal strings, one per stack, top box first: e.g. ['c14 r22', 'G9 c11', ...]
// Each token is a colour key followed by an ant count.
export function parseDeal(stacks, image) {
  return stacks.map((str) => str.trim().split(/\s+/).filter(Boolean).map((tok) => {
    const color = image.keys.indexOf(tok[0]);
    const count = parseInt(tok.slice(1), 10);
    if (color < 0 || !(count > 0)) throw new Error(`bad box '${tok}'`);
    return { color, count };
  }));
}

export function formatDeal(stacks, image) {
  return stacks.map((s) => s.map((b) => image.keys[b.color] + b.count).join(' '));
}

export function normalizeHex(hex) {
  let h = hex.replace('#', '');
  if (h.length === 3) h = [...h].map((c) => c + c).join('');
  return '#' + h.toLowerCase();
}
