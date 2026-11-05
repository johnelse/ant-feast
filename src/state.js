// Pure game state and rules (no drawing).

export const SLOT_COUNT = 5;
export const STACK_COUNT = 4;
export const DEFAULT_BOX_MIN = 10;
export const DEFAULT_BOX_MAX = 30;

export function mulberry32(seed) {
  return function () {
    seed = (seed + 0x6d2b79f5) | 0;
    let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

export function hashString(s) {
  let h = 2166136261;
  for (let i = 0; i < s.length; i++) {
    h ^= s.charCodeAt(i);
    h = Math.imul(h, 16777619);
  }
  return h >>> 0;
}

// Split n ants into boxes of min..max (a colour with fewer than min pixels
// gets one small box). Sizes always sum to exactly n.
function splitCount(n, rand, min, max) {
  const out = [];
  while (n > 0) {
    if (n <= max) {
      out.push(n);
      break;
    }
    const hi = Math.min(max, n - min);
    const k = min + Math.floor(rand() * (hi - min + 1));
    out.push(k);
    n -= k;
  }
  return out;
}

// Random deal: each colour's pixel count split into boxes, shuffled and dealt
// round-robin onto the stacks.
export function randomDeal(pixelsByColor, seed, { boxMin = DEFAULT_BOX_MIN, boxMax = DEFAULT_BOX_MAX } = {}) {
  const rand = mulberry32(seed);
  const boxes = [];
  pixelsByColor.forEach((count, color) => {
    for (const k of splitCount(count, rand, boxMin, boxMax)) boxes.push({ color, count: k });
  });
  for (let i = boxes.length - 1; i > 0; i--) {
    const j = Math.floor(rand() * (i + 1));
    [boxes[i], boxes[j]] = [boxes[j], boxes[i]];
  }
  const stacks = Array.from({ length: STACK_COUNT }, () => []);
  boxes.forEach((b, i) => stacks[i % STACK_COUNT].push(b));
  return stacks;
}

export class Game {
  // opts.deal: explicit stacks [[{color, count}, ...] x4], top box first.
  // Without it, a random deal is made from `seed`.
  constructor(image, seed, opts = {}) {
    if (!image) return; // used by clone()
    this.w = image.width;
    this.h = image.height;
    this.colors = image.colors;
    const n = image.cells.length;
    this.cells = Int8Array.from(image.cells);
    this.claimed = new Uint8Array(n);
    this.outside = new Uint8Array(n); // empty cell connected to the edge
    this.exposed = new Uint8Array(n); // filled cell touching the outside
    this.avail = new Int32Array(this.colors.length); // exposed & unclaimed, per colour
    this.pixelsByColor = new Array(this.colors.length).fill(0);
    for (const c of this.cells) if (c >= 0) this.pixelsByColor[c]++;
    this.totalPixels = this.pixelsByColor.reduce((a, b) => a + b, 0);
    this.pixelsLeft = this.totalPixels;
    this.antSerial = 0;

    // Anything beyond the grid counts as outside, so edge pixels are exposed.
    for (let y = 0; y < this.h; y++) {
      for (let x = 0; x < this.w; x++) {
        if (x === 0 || y === 0 || x === this.w - 1 || y === this.h - 1) {
          const i = y * this.w + x;
          if (this.cells[i] >= 0) this.expose(i);
          else this.flood(i);
        }
      }
    }

    // stacks[s][0] is the top (pickable) box. Boxes in stacks are never
    // mutated, so clones can share them.
    const deal = opts.deal ?? randomDeal(this.pixelsByColor, seed, opts);
    let id = 0;
    this.stacks = deal.map((stack) => stack.map(({ color, count }) =>
      ({ id: id++, color, count, remaining: count, out: 0, releaseTimer: 0 })));
    const totals = new Array(this.colors.length).fill(0);
    for (const b of this.stacks.flat()) totals[b.color] += b.count;
    totals.forEach((t, c) => {
      if (t !== this.pixelsByColor[c]) {
        throw new Error(`deal has ${t} ants of colour ${c} but the picture has ${this.pixelsByColor[c]} pixels`);
      }
    });

    this.slots = new Array(SLOT_COUNT).fill(null);
    this.ants = [];
    this.status = 'playing'; // 'playing' | 'won' | 'lost'
  }

  clone() {
    const g = new Game();
    Object.assign(g, this);
    g.cells = this.cells.slice();
    g.claimed = this.claimed.slice();
    g.outside = this.outside.slice();
    g.exposed = this.exposed.slice();
    g.avail = this.avail.slice();
    g.pixelsByColor = this.pixelsByColor.slice();
    g.stacks = this.stacks.map((s) => s.slice());
    g.slots = this.slots.map((b) => (b ? { ...b } : null));
    g.ants = this.ants.map((a) => ({ ...a }));
    return g;
  }

  expose(i) {
    if (this.exposed[i]) return;
    this.exposed[i] = 1;
    if (!this.claimed[i]) this.avail[this.cells[i]]++;
  }

  // Flood "outside" from empty cell `start`, exposing filled neighbours.
  flood(start) {
    if (this.cells[start] >= 0 || this.outside[start]) return;
    const stack = [start];
    this.outside[start] = 1;
    while (stack.length) {
      const i = stack.pop();
      const x = i % this.w;
      const y = (i - x) / this.w;
      const visit = (nx, ny) => {
        if (nx < 0 || ny < 0 || nx >= this.w || ny >= this.h) return;
        const n = ny * this.w + nx;
        if (this.cells[n] >= 0) this.expose(n);
        else if (!this.outside[n]) {
          this.outside[n] = 1;
          stack.push(n);
        }
      };
      visit(x - 1, y);
      visit(x + 1, y);
      visit(x, y - 1);
      visit(x, y + 1);
    }
  }

  isExposed(i) {
    return this.exposed[i] === 1;
  }

  hasTarget(color) {
    return this.avail[color] > 0;
  }

  // Nearest unclaimed exposed pixel of a colour to grid point (gx, gy), or -1.
  findTarget(color, gx, gy) {
    if (!this.avail[color]) return -1;
    let best = -1;
    let bestD = Infinity;
    for (let i = 0; i < this.cells.length; i++) {
      if (this.cells[i] !== color || this.claimed[i] || !this.exposed[i]) continue;
      const x = i % this.w + 0.5;
      const y = Math.floor(i / this.w) + 0.5;
      const d = (x - gx) ** 2 + (y - gy) ** 2;
      if (d < bestD) {
        bestD = d;
        best = i;
      }
    }
    return best;
  }

  claim(i) {
    this.claimed[i] = 1;
    this.avail[this.cells[i]]--;
  }

  // Only exposed (and claimed) pixels are taken, so the new gap joins the
  // outside and may open up enclosed areas behind it.
  takePixel(i) {
    const c = this.cells[i];
    this.cells[i] = -1;
    this.claimed[i] = 0;
    this.exposed[i] = 0;
    this.pixelsByColor[c]--;
    this.pixelsLeft--;
    this.flood(i);
    return c;
  }

  freeSlot() {
    return this.slots.indexOf(null);
  }

  placeBox(stackIdx) {
    if (this.status !== 'playing') return -1;
    const stack = this.stacks[stackIdx];
    const slot = this.freeSlot();
    if (!stack || !stack.length || slot < 0) return -1;
    this.slots[slot] = { ...stack.shift(), releaseTimer: 0.15 };
    return slot;
  }

  // True while anything can still happen without the player acting.
  isBusy() {
    return this.ants.length > 0 ||
      this.slots.some((b) => b && b.remaining > 0 && this.avail[b.color] > 0);
  }

  updateStatus() {
    if (this.status !== 'playing') return;
    if (this.pixelsLeft === 0) {
      this.status = 'won';
      return;
    }
    if (this.isBusy()) return;
    const canPlace = this.freeSlot() >= 0 && this.stacks.some((s) => s.length);
    if (!canPlace) this.status = 'lost';
  }
}
