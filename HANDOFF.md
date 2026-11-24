# HANDOFF — zf-approx

**Where to take off:** read §1 (design principles) and §8 (the outside API, frozen and
implemented). Current status is §2, git is §3, optional next items are §4, closed questions §5,
the owner-rulings archive §6, pointers §7. Round 17 (2026-11-24) consolidated this file and
REPORT.md; earlier versions are in git. Everything is local; nothing is pushed.

---

## 1. Design principles (owner rulings — carry these forward)

- **Mathematical origin, not software engineering.** Implement the algorithm; no correctness
  proofs or complexity analysis in the deliverables (AGENTS.md rule 1).
- **One interface with the outside.** Internally, minimal `try`/`except` — only where necessary.
  The core trusts that the inputs are suitable; it does not check or clean them.
- **Core only:** the input/output objects and the main loop. No unasked extras (tests, README,
  etc.) without offering first.
- **Confirm scope before building.** When unsure of a requirement, ask the owner one concise
  question with a stated default (skipping must be safe).
- **Report style:** four buckets (owner knows / decided / to-decide / agent findings), reading
  guide at the top, plain self-contained items, no verification busywork. The owner is the
  paper's author — never ask him to confirm facts from his own paper; resolve and record them.

## 2. Current status (round 17, 2026-11-24)

**Package `zf/` — 7 modules, 528 lines, stdlib-only; one export.**

| module | lines | role |
|---|---|---|
| [zf/__init__.py](zf/__init__.py) | 19 | exports only `zf_via_path_decomp` (v0.3.0) |
| [zf/api.py](zf/api.py) | 171 | layer: gates `_is_connected` + `_is_path_decomp`, `_to_nice`, names-based `ZFResult` |
| [zf/alg_core.py](zf/alg_core.py) | 118 | `zf_core`: loop L1–L8 with the three tricks; internal `ZFResult` (indices) |
| [zf/zf_closure.py](zf/zf_closure.py) | 67 | `closure`: B-F-H white counts, min-index canon, stale-entry guard |
| [zf/arcs.py](zf/arcs.py) | 62 | `Arcs`: out/in arrays, add/delete(heads)/reverse/extend/sources(vertices) |
| [zf/graph.py](zf/graph.py) | 47 | `Graph`: static, sorted name↔index bijection, `to_names`/`arcs_to_names` |
| [zf/path_decomp.py](zf/path_decomp.py) | 44 | `NicePathDecomposition`: ops=(v,±1), bags, k, width; no validation |

The five core modules contain **zero** `try`/`except`/`raise`; the only two raises in the
package are the layer's gates. Tricks: [L3] introduce steps and forgets inside `X_t` skip
closure; [L6b] `S = A.sources()` once at the end; [L6c] closure on the FULL graph with outside
vertices blued (no induced subgraph ever built). Canon: smallest eligible index (tex:L621),
arc-for-arc parity with the parallel project verified.

**Around the package:** [examples.py](examples.py) (8 blocks, internal core, all pass);
[SPEC-v1.md](SPEC-v1.md) (living contract); [docs/definitions.md](docs/definitions.md);
[docs/closure-review.md](docs/closure-review.md); [docs/pipeline-demo.html](docs/pipeline-demo.html)
(traced one-way figure); [docs/presentation_snippets.py](docs/presentation_snippets.py) (4 cells:
setup, house, C5, H) and [docs/standalone_H.py](docs/standalone_H.py) (one paste); figures
`docs/demo_house.png`, `docs/demo_c5.png`, `docs/demo_H.png`;
[zf-round2-backup.zip](zf-round2-backup.zip) (round-2 defensive core + 112 tests, verbatim).
Status and history: [REPORT.md](REPORT.md).

**Key math facts (do not re-derive):**
- Indexing: `ops` length `2n`; `k = 2n−1`; 0-based op `z−1` produces `X_z`; signs exactly
  `{+1, −1}` (no `0` op). Audited correct.
- `sources(vertices)` = `sources ∩ mask`: [L6c] blues outside vertices, which otherwise appear
  as spurious sources; the main algorithm needs no mid-loop mask (S once at the end over V).
- Core suitability = D1–D4 + every vertex in some bag (caller's responsibility; disconnected and
  edgeless graphs work internally). Outside API additionally requires connected (round 16).
- Paper: arXiv:2402.08866v1. Algorithm box tex:L623–665; canon tex:L621; "S once at end"
  tex:L685; connectedness assumption tex:L822; closure = Brimkov–Fast–Hicks, EJOR 273(3):889–903
  (2019), Algorithm 1; nicification = Bodlaender–Kloks Lemma 13.1.3, tex:L580–581. Local tex:
  `resources/paper/arXiv-2402.08866v1/2024-02-13-Zero_Forcing_Approx_Alg.tex`.

## 3. Git state

- Chain (all local, nothing pushed, no remote changes): `67e8008` baseline → `e965858` chore →
  `76700f8` core rounds 1–5 → `aa5d70c` handoff → `b53242d` round-8 API design → `88d1196`
  round 9 → `22aadf0` round 10 → `fa1e848` round 11 → `18edf22` round 12 → `c4d093b` round 13 →
  `55ddf70` round 14 → `2f8afc4` round 15 → `868b23f` round 16 → round 17 (this consolidation).
- Left as-is, never committed by the agent: your [AGENTS.md](AGENTS.md) edit; untracked
  `SPEC.md` (your v0), `resources/` (the papers), `spec2`, and your `demo.ipynb` (owner ruling,
  round 18: keep untracked — local working file, not a repo deliverable);
  `.ipynb_checkpoints/` ignored since round 18.
- No push and no remote change (AGENTS.md rule 7).

## 4. Optional next items (defaults stand; only on your word)

1. **Pathwidth / building bags from a graph** — your API point 2. *Default: out of scope.*
2. **Notebook-phase extras** — more worked examples; further guarantee-display polish.
   *The line-by-line aligned bound print landed in round 20; the rest stays deferred by you
   to your Jupyter presentation of the paper.*
3. **Public release** — packaging (README/pyproject/license) and the SPEC-v1 §4 name proposal.
   *Default: keep the names; `graph.py`/`arcs.py` stay generic unless you want a `zf_` prefix.*
4. **Disconnected graphs at the API** — e.g. per-component runs unioned. *Default: rejected
   (round 16 ruling); a layer feature if ever wanted, never a core change.*

## 5. Closed questions (resolution recorded)

- One function outside? **Yes** — implemented round 9, renamed round 11 (§8).
- Add `SPEC.md` / `resources/` / `spec2` to git? **No** — default applied, they stay out.
- Numbering mistake? **None** — round-5 audit stands (`k=2n−1`, op `z−1` → `X_z`, signs ±1).
- API point 3? **None** — never stated; owner does not recognize it; closed round 11.

## 6. Owner rulings archive (recorded by the agent from chat; key quotes verbatim)

**2026-11-21 (round 9).** Return shape: "a result object in the original vertex names"
(`zf_set`, `forts`, `arcs` all in names). On trust vs checking: "No, in fact, the translation
(transition) layer should involve a function that making a path decomposition into a nice p-d"
— read then as: no checking, but an explicit nicification function (`_to_nice`). API point 2
(verbatim): "Where the decomposition comes from. … Building one from a graph is a separate
algorithm (pathwidth). *Default: not part of this project unless you ask.*"

**2026-11-23 (round 11).** Naming: `zero_forcing_set` is "way too general as a noun … does not
say anything about the pd part"; requested `decomposition.py` → "path decomp.py" (agent applied
Python identifier rules: `path_decomp.py`), `closure.py` → `zf_closure.py`, `algorithm.py` →
`alg_core.py`, and a public name saying "via path decomposition" (agent chose
`zf_via_path_decomp`; internal `zf_core`). Validation (supersedes the round-9 trust default for
the layer): "we will force the user to enter a path decomposition and nic-ify it … something
like `_is_path_decomp` returning true or false, and halt immediately when it is not." And:
"leave the core as it is, and make sure the math part is understood by mathematicians."
Extras: "leave it for now" (notebook phase). Tree-decomposition question answered: path-specific
object and algorithm; a tree decomposition would be a different algorithm.

**2026-11-23 (rounds 13–15).** Make the demo-HTML examples copy-pasteable; "one cell per case";
"only print the forts but highlight the arc sets and the zero forcing set"; the old demo
(`resources/CJMZ_ZF_demo.html`) "has factual error about zero forcing sets, do not mind but only
care about the presentation"; "make a commit before proceed" (checkpoint `18edf22` verified);
then his graph H (11 vertices, bags already nice) as a case, and one complete self-contained
snippet for it.

**2026-11-23 (round 16).** "What happen when the input graph is disconnected? … I do not want
that, should we rule out the case (again, of course, outside of the core) of disconnected
graph" — implemented: `_is_connected` gate, `ValueError` halt, core untouched; disconnected
examples removed from snippets and demo.

**2026-11-24 (round 17).** "we now reach another point of cleaning up REPORT, HANDOFF, and
commit" — this consolidation.

**2026-11-24 (round 20).** Make the guarantee explicit in the notebook: print line by line
(S / forts / arcs, then |S|, w, |F|, (w+1)|F| and the checked inequality, aligned), then the
picture with the explanation in a legend — implemented as `report(r, bags)` + legend outside
the axes in `present`, in the snippets and the standalone H file.

## 7. Pointers

- Presentation: [docs/presentation_snippets.py](docs/presentation_snippets.py) (4 cells),
  [docs/standalone_H.py](docs/standalone_H.py); figures `docs/demo_house.png`,
  `docs/demo_c5.png`, `docs/demo_H.png`.
- Visual demo: [docs/pipeline-demo.html](docs/pipeline-demo.html) — open in a browser.
- Spec: [SPEC-v1.md](SPEC-v1.md) · definitions: [docs/definitions.md](docs/definitions.md) ·
  closure review: [docs/closure-review.md](docs/closure-review.md) · status: [REPORT.md](REPORT.md).
- Examples: [examples.py](examples.py) (`python3 examples.py`).
- Prior work + tests: [zf-round2-backup.zip](zf-round2-backup.zip).
- Paper: `resources/paper/arXiv-2402.08866v1/` · Brimkov PDFs: `resources/brimkov*.pdf`.

## 8. Outside API — frozen contract (current)

**`zf.zf_via_path_decomp(graph, bags)`** — the only export.
- `graph`: `networkx.Graph`, simple, undirected, **connected** (null/single vertex vacuously
  connected); nodes are the vertex names (distinct, sortable).
- `bags`: list of sets of names forming a path decomposition (D1 edge coverage, D2 contiguity,
  every vertex covered); **not** necessarily nice.
- Gates (layer only): `_is_connected(graph)` then `_is_path_decomp(graph, bags)`; `ValueError`
  halt on either failure. The core trusts its inputs and raises nothing.
- Returns frozen `ZFResult` in original names: `zf_set` (sorted tuple), `forts` (frozensets,
  discovery order), `arcs` ((name, name) pairs, sorted by tail; sources = `zf_set`).
  Guarantee: |S| ≤ (w+1)·|F|, w = max|bag| − 1.
- Layer steps: gates → `Graph(graph.nodes, graph.edges)` (sorted bijection reused) →
  `_to_nice` → `zf_core` → translate back via `to_names`/`arcs_to_names`. The layer never
  imports networkx (reads `.nodes`/`.edges`), so `import zf` is stdlib-only.
- `_to_nice` convention: drop empty/duplicate bags; between consecutive bags forget
  `X_i \ X_{i+1}` in increasing index order, then introduce `X_{i+1} \ X_i` in increasing index
  order (forget-first is forced by width preservation); every input bag appears verbatim;
  identity on already-nice bags. Disconnected inputs would pass through an empty intermediate
  bag — unreachable from the API since round 16, handled correctly by the internal core.
- Design rationale (round 8): NetworkX fixed as the single outside graph type (nodes already
  are names; standard in the community; dependency confined to the layer); bags fixed as a list
  of sets of names. An edge-list fallback was offered and not taken.
- Behavior notes: the loop evaluates W at z=k+1, so with no earlier fort the trivial fort V is
  added (paper-faithful) and every run on n≥1 returns ≥1 fort; `arcs` order is sorted by tail,
  not chain order. Full contract and proofs-of-behavior: [SPEC-v1.md](SPEC-v1.md) §7.
