# Ant Feast — notes for agents and developers

- A pixel picture sits at the top, 5 slots below it, and 4 stacks of coloured boxes below those.
  Each box shows an ant count.
- Tapping a stack's top box moves it into a free slot. Its ants walk out, collect *exposed*
  pixels of their colour (pixels touching empty space connected to the outside), and carry
  them home.
- **Win:** the picture is cleared.
- **Lose:** no slotted box can act, and either all slots are full or the stacks are empty.
- A box whose colour has run out while it still holds ants blocks its slot. That is the
  pressure that makes it a puzzle.

Plain HTML + ES modules on a `<canvas>`. No build step, no dependencies, no Node.

## Running

```sh
python3 -m http.server 8000          # from the repo root, then open http://localhost:8000
```

- ES modules need http, not file://.
- After changing JS, hard refresh (Ctrl+Shift+R). Browsers cache module scripts.
- URL options on `index.html`:
  - `?level=N` picks a level.
  - `?auto` replays the level's stored solution.
  - `?debug` shows exposed pixels and ant routes.

## Design decisions (agreed with the user)

- **Box ant totals exactly equal each colour's pixel count.** There is no slack. `Game` throws if
  a deal doesn't match.
- **Pictures are complete rectangles.** Every cell has a colour; the background is coloured too.
- **Levels must stay hard all the way through**, not just at the opening. A player who makes a
  sensible start should still have to think about which box to pick next.
- **The simulation is deterministic** (no `Math.random`, fixed step `STEP = 1/120`), so the
  solver's playouts reproduce the real game exactly.
- **Ants never walk straight to a pixel.** They walk round a one-cell track around the picture,
  enter from the side nearest the target, and route through already-cleared cells (BFS).
- **Slotted boxes show `n/m`**, where n = ants still in the box and m = n + ants out gathering.
- **Users can turn their own images into levels** (`Use your image…`). These are saved in
  localStorage (`antfeast.custom.v1`, at most 8).

## Code map (`src/`)

| File | Purpose |
|---|---|
| `main.js` | Entry point: level select (built-in plus saved custom levels), restart/remove buttons, pointer input, fixed-step loop. |
| `levels.js` | `LEVELS`: built-in levels, each `{name, palette, deal, solution, rows}`. Each `rows` string is one picture row of palette keys. `deal` is 4 strings (top box first, e.g. `'r14 c23'`). `solution` is a string of stack indices that wins. |
| `image.js` | `parseLevel(def)` → `{width, height, colors, keys, cells}`. `parseDeal` / `formatDeal` convert between deal strings and arrays. |
| `state.js` | `Game`: pure game state (slots, stacks, incremental exposure flood-fill, target claiming, routing BFS, win/lose). Also `randomDeal`, `mulberry32`, `hashString`, `SLOT_COUNT`, `STACK_COUNT`. |
| `ants.js` | Ant simulation (`updateAnts(game, dt)`): release timing, track-and-route path planning, carrying pixels home. |
| `layout.js` | Fixed logical layout (420×772): picture, slot and stack rectangles. Cell size = `floor(368 / (rows + 2))`. |
| `render.js` | Canvas drawing: board, picture, slots, stacks, ants, win/lose overlay, debug overlay. The picture and the stacks are cached in offscreen canvases and only repainted when they change; drawing everything each frame was too slow on phones for 40×40 pictures. |
| `bot.js` | `makeReplayer(solution)` plays a stored solution (used by `?auto` and tests). |
| `solver.js` | DFS solver on a "place a box, then settle" model (`solve`). Also scripted players (greedy, random among boxes that can eat, fully random) and `difficultyProfile`, which gives win rates after the first k moves of the solution. |
| `generate.js` | Building blocks for the deal generator: `checkDeal` (solvable? how hard?), the `mutate`/`mutateChain` hill-climb moves, `sequenceDeal` (always-solvable fallback start), `difficultyLabel`, `fullReport`. |
| `parallel.js` | `generateDealParallel(image, opts)`: steady-state hill climb across a pool of Web Workers. Returns `{promise, finish(), cancel()}`. |
| `evalWorker.js` | Worker that scores candidate deals for `parallel.js`. |
| `imageLoad.js` | Turns a user image into a level: downscale, then k-means++ colour quantisation on a supersampled image, then each cell takes its most common colour. |
| `custom.js` | The "Use your image…" dialog: preview, generation progress, "Play now", saving levels. |

## How difficulty is generated and measured

- **Generator** (`generateDealParallel`) hill-climbs over deals.
  - Mutations: swap two boxes, move a box to another stack, or shift ants between two boxes of
    the same colour.
  - Every accepted deal must be solved by `solve()` within `maxNodes`.
- **Objective `'sustained'`** (always use this): averages how often unthinking players win when
  starting from several points along the solution (0, 20, 40, 60 and 75% of the way through).
  There is a penalty if the greedy player wins. **Lower is harder.**
  - Current built-in levels score roughly 0.02–0.10.
  - Above about 0.15 a level feels easy.
- **What actually makes a level hard is colour topology, not resolution or box size.** Each
  colour should appear in many separate places at several depths: outlines, bands, thin lines,
  and shared background colours.
  - Big connected regions of one colour (a plain sky, broad stripes, spirals) make levels easy.
  - The final ~25% of any level is inherently easy.
- **Art direction:** get that topology from *detail that belongs to the picture*: outlines,
  shading bands, patterns on the subject, thin overlapping features, and scenery. Avoid random
  speckle, which hides the subject. Most levels before Jellyfish still lean on speckle and
  are candidates for redrawing.
  - **Jellyfish (40×40, `tools/art/jelly.py`) is the reference example.** It has an outlined
    bell with a highlight, a shadow and patterns, frilly arms, crossing tentacles, bubbles,
    and wavy "current" streaks in a second water colour. It scores 0.000: careless play loses
    from 20% to 75% of the way through.
  - **Background texture matters a lot.** For the same jellyfish, diagonal light shafts scored
    0.29, an organic caustic net 0.025, and current streaks 0.000. Many small, separate pockets
    of the background colour at different depths are what make it hard.
  - **Larger grids** (40×40, 8 px cells) give room for meaningful detail. They cost about 2–3×
    in play time (about 8 minutes) and up to 2–3× in generation time (4–11 minutes).

## Testing and regenerating (headless)

The test pages run in any browser at `http://localhost:8000/test/<page>.html`. To run them
headless:

```sh
python3 tools/serve.py &      # serves the repo on :8766 and saves POSTed output to tools/out/
```

- **`test/sim.html`**: checks every level (deal totals match, the stored solution wins through
  the real game loop, the greedy player loses). `?level=N&t=SECONDS&debug` draws a mid-game
  snapshot. It's synchronous, so `--dump-dom` works:
  `chromium --headless --dump-dom http://127.0.0.1:8766/test/sim.html`
- **`test/difficulty.html`**: difficulty profile per level. Options:
  - `?trials=40`
  - `&only=Pizza,Apple`
  - `&checkpoints=0,5,10`
- **`test/generate.html`**: generates a deal for one level and prints `deal:` and `solution:`
  lines to paste into `src/levels.js`, plus a difficulty report. It uses workers, so run it with
  the title-polling runner:

  ```sh
  tools/runpage.sh "http://127.0.0.1:8766/test/generate.html?level=6&iterations=300&objective=sustained&trials=8&report=40&post=/gen6" 9301 3600
  cat tools/out/gen6
  ```

  - Box size: `min=6&max=24` (default). For about 40×40 pictures use `min=10&max=40`.
  - `continue=1` keeps improving the level's current deal.
  - `seed=`, `workers=`.
  - About 2 minutes per 28×28 level on a 4-core laptop at 300 iterations. Scales roughly with
    cores.
- **`test/custom.html`, `test/ui.html`**: user-image pipeline and the dialog flow. Both set a
  `DONE` title, so use `tools/runpage.sh`.

### Notes on headless Chromium

- `--dump-dom`, `--virtual-time-budget` and `--timeout` don't wait for Web Workers. That's why
  worker pages set `document.title = "DONE …"` and `runpage.sh` polls `/json/list` on the
  remote-debugging port.
- Snap Chromium can only write under `~/snap/chromium/common`, which `runpage.sh` handles. Set
  `CHROME=` to use another browser binary.

## Drawing new pictures

Pictures are drawn procedurally in Python (needs Pillow) with `tools/art/pix.py`:

- **Drawing:** `Pic(w, h, bg, palette)` gives `fill(pred, key)`, `line`, `curve(fn, t0, t1, key)`
  (4-connected), and `outline(inside, key, where=)`.
- **Output:** `rows()` returns the strings for `levels.js`, `counts()` gives pixels per colour,
  and `png(path)` writes a preview.

A drawing script lives in `tools/art/`. It defines `PAL` (key → `#hex`) and `draw(size)`,
which returns a `Pic` (see `jelly.py`; its `WATER` styles show several background textures).

Workflow:

```sh
# 1. draw and install the picture (replaces a level of that name in place, dropping its stale
#    deal; otherwise adds it after --after, or at the end). --png writes a preview to look at.
python3 tools/art/install.py picture tools/art/jelly.py 40 "Jellyfish" --after "Mushroom" --png /tmp/j.png

# 2. generate a deal for it (level index = its position in LEVELS, counting from 0)
python3 tools/serve.py &
tools/runpage.sh "http://127.0.0.1:8766/test/generate.html?level=6&iterations=300&objective=sustained&trials=8&report=40&min=10&max=40&post=/gen6"

# 3. install the deal and solution it found
python3 tools/art/install.py deal "Jellyfish" tools/out/gen6
```

Then check the level with `sim.html` and `difficulty.html`, and look at it in the game.

Rules for pictures:

- Use at most 8 colours. Pictures must be complete rectangles. `install.py` checks both.
- Any change to a picture invalidates its deal, so always regenerate one after reinstalling.
- `src/levels.js` is the source of truth for what ships. The scripts for most existing levels
  were not kept. Keep the script for any new or redrawn level in `tools/art/`.

## Conventions

- **Commits:** only when asked. Never add `Co-Authored-By` / `Co-authored-by` lines. The user
  likes work split into a few logical commits. Don't push.
- **The user's game server:** they often run their own `python -m http.server` on port 8000.
  Leave it alone. Use port 8766 (`tools/serve.py`) for automated runs.
