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
  - Most built-in levels score 0.000–0.075.
  - Above about 0.15 a level feels easy.
  - Known weaker levels:
    - **Snail** (0.525): its last 40% is easy, and it may need a new composition.
    - **Lighthouse** (0.525): kept for its looks; a busier sky was judged too messy
      (`tools/out/lighthouse_v3.py` on the original machine).
    - **Mushroom** (0.300): only its last quarter is easy.
- **What actually makes a level hard is colour topology, not resolution or box size.** Each
  colour should appear in many separate places at several depths: outlines, bands, thin lines,
  and shared background colours.
  - Big connected regions of one colour (a plain sky, broad stripes, spirals) make levels easy.
  - The final ~25% of any level is inherently easy.
- **Art direction:** get that topology from *detail that belongs to the picture*: outlines,
  shading bands, patterns on the subject, thin overlapping features, and scenery. Avoid random
  speckle, which hides the subject. All 18 levels are now drawn this way at 40×40, each by its
  own script in `tools/art/`.
  - **Jellyfish (40×40, `tools/art/jelly.py`) is the reference example.** It has an outlined
    bell with a highlight, a shadow and patterns, frilly arms, crossing tentacles, bubbles,
    and wavy "current" streaks in a second water colour. It scores 0.000: careless play loses
    from 20% to 75% of the way through.
  - **Background texture matters a lot.** For the same jellyfish, diagonal light shafts scored
    0.29, an organic caustic net 0.025, and current streaks 0.000. Many small, separate pockets
    of the background colour at different depths are what make it hard.
  - **Larger grids** (40×40, 8 px cells) give room for meaningful detail. They cost about 2–3×
    in play time (about 8 minutes) and up to 2–3× in generation time (4–11 minutes).
- **Lessons from redrawing all the levels:**
  - **Break up big open backgrounds** with things that belong in the scene. Big clouds and
    plain shapes don't help. What worked:
    - wavy streaks: water currents, sky wisps, cirrus, nebulae, moonlit cloud
    - foliage framing the picture: trees, big veined leaves, ferns, blossom branches, kelp
    - structure on large surfaces: timber framing, leaf veins that reach the leaf's edge,
      rock streaks on mountains, wallpaper stripes
  - **Some examples:**
    - Apple: 0.94 in an open orchard, 0.037 inside a leafy tree.
    - House: 0.68 with plain walls and sky, 0.025 with framing and trees.
    - Penguin: 0.65 with a plain sky, 0.037 with a sun halo, cirrus and seabirds.
  - **The middle of the picture is eaten last**, so it needs interleaved colours too. Large
    plain subject areas, or long connected bands (for example a spiral shell's whorls), make the
    endgame easy.
  - **Keep additions purposeful.** The user rejects pictures that get messy, even if they are
    harder.
  - **Generator luck matters.** Another 600-candidate climb with a new seed sometimes drops the
    score sharply (Watermelon went from 0.325 to 0.000, Ladybird from 0.175 to 0.075). Try that
    before changing the art. A score still above about 0.3 after three climbs needs art changes.

## Testing and regenerating (headless)

The test pages run in any browser at `http://localhost:8000/test/<page>.html`. To run them
headless:

```sh
python3 tools/serve.py &      # serves the repo on :8766 and saves POSTed output to tools/out/
```

- **`test/sim.html`**: checks every level (deal totals match, the stored solution wins through
  the real game loop, the greedy player loses).
  - `?only=Parrot,Apple` checks just those levels, in seconds.
  - `?level=N&t=SECONDS&debug` draws a mid-game snapshot.
  - The page sets a `DONE …` title with the results, so use `tools/runpage.sh`, or
    `--dump-dom` since the page is synchronous:
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
  - On a 4-core laptop, 300 iterations take about 2 minutes for a 28×28 level and 4–8 minutes
    for 40×40.
  - Only about 6% of a run is single-threaded, so it scales almost linearly with cores. Workers
    are capped at 16 by `defaultWorkerCount()` in `src/parallel.js`.
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

Each script also runs on its own to write a preview: `python3 tools/art/owl.py /tmp/owl.png`
(`jelly.py` and `parrot.py` take a size first: `python3 tools/art/jelly.py 40 /tmp/j.png`).
Shared shapes and scenery (ellipses, polygons, leaves, ferns, clouds, streaks, grass, flowers,
`curve_in` for curves clipped to a shape) are in `tools/art/shapes.py`.

Workflow:

```sh
python3 tools/serve.py &      # once, in the background

# Draw, generate and check in one go (level index = position in LEVELS, counting from 0).
# Installs the picture, generates a deal, keeps climbing while the score is above 0.06, installs
# the best deal, then replays the solution with sim.html. Takes about 5-25 minutes.
tools/pipeline.sh "Jellyfish" tools/art/jelly.py 6

# Commit one level without its neighbours' unfinished changes in levels.js:
python3 tools/stage_level.py "Jellyfish"
git add tools/art/jelly.py
git commit
```

The steps it runs can also be done by hand:

```sh
# 1. draw and install the picture (replaces a level of that name in place, dropping its stale
#    deal; otherwise adds it after --after, or at the end). --png writes a preview to look at.
python3 tools/art/install.py picture tools/art/jelly.py 40 "Jellyfish" --after "Mushroom" --png /tmp/j.png

# 2. generate a deal for it
tools/runpage.sh "http://127.0.0.1:8766/test/generate.html?level=6&iterations=300&objective=sustained&trials=8&report=40&min=10&max=40&post=/gen6"

# 3. install the deal and solution it found
python3 tools/art/install.py deal "Jellyfish" tools/out/gen6
```

Then look at the level in the game. If the score is weak, back up the script and the deal
output in `tools/out/` before changing the art, so you can go back.

Rules for pictures:

- Use at most 8 colours. Pictures must be complete rectangles. `install.py` checks both.
- Any change to a picture invalidates its deal, so always regenerate one after reinstalling.
- `src/levels.js` is the source of truth for what ships. Every built-in level has its drawing
  script in `tools/art/`; keep it in step when a picture changes.

## Conventions

- **Commits:** only when asked. Never add `Co-Authored-By` / `Co-authored-by` lines. The user
  likes work split into a few logical commits. Don't push.
- **The user's game server:** they often run their own `python -m http.server` on port 8000.
  Leave it alone. Use port 8766 (`tools/serve.py`) for automated runs.
