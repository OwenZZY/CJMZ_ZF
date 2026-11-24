# Report — zf-approx (current: round 17, 2026-11-24; history: rounds 1–16)

**Reading guide: nothing pending — no decisions needed.** This file is the consolidated
owner-facing status: §1 what needs doing (nothing required), §2 what exists and the round
history, §3 recorded rulings, §4 agent findings (informational). The living contract is
[SPEC-v1.md](SPEC-v1.md); the coordination record and owner rulings are [HANDOFF.md](HANDOFF.md).
Earlier versions of this report are in git; round 17 consolidated them.

---

## 1. What needs to be done (by whom)

- **Nothing required.** All sixteen rounds are complete and verified; the package, the spec,
  the visual demo, and the presentation snippets are current and committed.
- Optional, owner, only on your word:
  - building a path decomposition from a graph (pathwidth) — your API point 2, out of scope
    unless asked;
  - more worked examples / a direct guarantee display — deferred by you to your Jupyter
    notebook presentation phase;
  - public-release packaging and the §4 name proposal in [SPEC-v1.md](SPEC-v1.md)
    (default: keep the names); `graph.py`/`arcs.py` could take a `zf_` prefix if you prefer
    uniformity (agent recommendation: keep them generic);
  - accepting disconnected graphs at the API again (e.g. per-component runs) — a layer
    feature, not a core change; currently rejected by ruling (round 16).

## 2. What is done

- **Round 20 (2026-11-24): notebook output format (owner request).** The one-line
  `S | forts | arcs` print and the in-title explanation are replaced by a `report(r, bags)`
  helper printing line by line with the guarantee aligned (`S`, `forts`, `arcs`, then
  `|S|`, `w`, `|F|`, `(w+1)|F|`, and the checked inequality `|S| <= (w+1)|F| : 2 <= 3 OK`),
  followed by the figure whose explanation now lives in a legend placed outside the axes
  (green = S, purple arrow = forcing arcs, grey = other vertices). Applied to
  [docs/presentation_snippets.py](docs/presentation_snippets.py) (all case cells) and
  [docs/standalone_H.py](docs/standalone_H.py); figures regenerated
  ([demo_house.png](docs/demo_house.png), [demo_c5.png](docs/demo_c5.png),
  [demo_H.png](docs/demo_H.png)); all cells re-executed headlessly, standalone agrees.

**Current deliverables**

- `zf/` — 7 modules, 528 lines, standard-library only. Core (338 lines, zero
  `try`/`except`/`raise`): [graph.py](zf/graph.py) (static graph, sorted name↔index bijection,
  output views), [arcs.py](zf/arcs.py) (`out_arcs`/`in_arcs`, add/delete/reverse/extend/sources),
  [path_decomp.py](zf/path_decomp.py) (`NicePathDecomposition`: ops, bags, k, width),
  [zf_closure.py](zf/zf_closure.py) (Brimkov–Fast–Hicks white counts, min-index canon),
  [alg_core.py](zf/alg_core.py) (`zf_core`: L1–L8 with the three tricks). Layer (171 lines):
  [api.py](zf/api.py) (`zf_via_path_decomp`, gates `_is_connected` + `_is_path_decomp`,
  `_to_nice`, names-based `ZFResult`); [__init__.py](zf/__init__.py) exports only the one
  function (v0.3.0).
- [examples.py](examples.py) — 8 explicit blocks exercising the internal core; all pass
  (`python3 examples.py`).
- [SPEC-v1.md](SPEC-v1.md) — living spec: paper transcription (§2), structure and interfaces
  (§5), v0 issue resolutions (§6), outside API contract (§7).
- [docs/definitions.md](docs/definitions.md) — every mathematical definition, one per line,
  with tex references. [docs/closure-review.md](docs/closure-review.md) — the B-F-H comparison
  and canon-alignment evidence.
- [docs/pipeline-demo.html](docs/pipeline-demo.html) — the whole one-way procedure as a
  self-contained figure (input → layer → loop → names result), every state traced from the
  shipped code; house walkthrough + C5 card + file map.
- Presentation: [docs/presentation_snippets.py](docs/presentation_snippets.py) — four
  copy-paste Jupyter cells (setup + helper; house; C5; your graph H), one figure per case,
  S green + forcing arcs purple, forts printed only;
  [docs/standalone_H.py](docs/standalone_H.py) — the same for H in a single paste. Figures:
  [demo_house.png](docs/demo_house.png), [demo_c5.png](docs/demo_c5.png),
  [demo_H.png](docs/demo_H.png).
- [zf-round2-backup.zip](zf-round2-backup.zip) — the round-2 defensive core + 112-test suite +
  examples + README, preserved verbatim (superseded work is kept, not deleted).

**Round history** (all commits local; nothing pushed)

| rounds | date | commit | substance |
|---|---|---|---|
| 1–5 | 11-20/21 | `76700f8` | spec steps 1–3; implementation; closure review + min-index canon alignment; lean-core ruling; name outputs; examples; index audit |
| 6–8 | 11-21 | `aa5d70c`, `b53242d` | handoff; math-origin reminder (7); outside-API design (8) — chats elsewhere |
| 9 | 11-21 | `88d1196` | outside API: one export, translation layer, forget-first nicification, names-based result |
| 10 | 11-23 | `22aadf0` | visual pipeline demo (traced figure) |
| 11 | 11-23 | `fa1e848` | renames (`path_decomp`/`zf_closure`/`alg_core`; `zf_via_path_decomp`/`zf_core`) + `_is_path_decomp` gate |
| 12 | 11-23 | `18edf22` | presentation snippets + NetworkX drawing (checkpoint for later restructures) |
| 13 | 11-23 | `c4d093b` | one cell per case; forts print-only; S + arcs highlighted |
| 14 | 11-23 | `55ddf70` | owner's graph H as a case cell (bags verbatim, already nice) |
| 15 | 11-23 | `2f8afc4` | standalone one-paste snippet for H |
| 16 | 11-23 | `868b23f` | connectedness gate; disconnected examples removed from presentation |
| 17 | 11-24 | `ccac571` | consolidation of REPORT and HANDOFF |
| 18 | 11-24 | `e128a12` | git hygiene: ignore `.ipynb_checkpoints/`; audit of tracked/untracked |
| 19 | 11-24 | `17d6ae1` | record ruling: `demo.ipynb` stays untracked |
| 20 | 11-24 | this commit | notebook print format: line-by-line results + aligned bound; legend outside axes |

**Verification evidence (cumulative, throwaway scripts deleted after use):** round 1: 111 unit
tests + 336 prototype trials; round 2: 960/960 closure parity vs the parallel project; round 3:
420 invariant + 480 parity trials; round 9: 300 parity + 300 invariant trials; round 11: 250
parity + 250 invariant + 125 invalid-input halts; round 16: 250 parity + 250 connected-invariant
+ 250 disconnected-halt trials. Invariants checked against brute-force Z(G): S forces G; forts
valid and pairwise disjoint; |F| ≤ Z(G) ≤ |S| ≤ (w+1)|F|; arcs replay as a forcing process from
S; width preserved; determinism. Presentation cells re-executed headlessly each round.

## 3. What is known / decided (recorded rulings — no action needed)

- **Lean internal core** (owner, round 3): the core trusts suitable inputs; no validation, no
  try/except, no raised exceptions inside the five core modules; no unasked extras. Superseded
  work lives in [zf-round2-backup.zip](zf-round2-backup.zip).
- **One interface outside** (owner, rounds 7–9): `zf.zf_via_path_decomp(graph, bags)` is the
  only export; NetworkX graph (nodes = names) + list of sets of names (a path decomposition,
  not necessarily nice); frozen names-based `ZFResult` (`zf_set`, `forts`, `arcs` sorted by
  tail). The translation layer is the only place touching external formats; it never imports
  networkx, so `import zf` is stdlib-only.
- **Layer gates** (owner, rounds 11 and 16): `_is_connected` (connected graph — the paper's
  assumption, tex:L822; null/single vertex vacuously connected) and `_is_path_decomp`
  (bag elements are vertices, coverage, D1, D2); `ValueError` halt on either failure. These are
  the only two `raise`s in the package. The core still trusts its inputs and still handles
  disconnected graphs correctly if called directly.
- **Nice-ification** (`_to_nice`): forget-first, width-preserving (forced: introduce-first can
  inflate a bag to |X_i ∪ X_{i+1}|); drop empty/duplicate bags; every input bag appears
  verbatim; identity on already-nice bags. Paper citation: Bodlaender–Kloks Lemma 13.1.3
  (tex:L580–581).
- **Forcing-order canon** (owner-approved, round 2): smallest eligible index via min-heap
  (tex:L621), matching the parallel project; white sets and fort packings are canon-independent.
  The whole algorithm is deterministic.
- **The three tricks**: [L3] introduce steps and forgets inside X_t skip closure; [L6b] S read
  once at the end from `A.sources()` (tex:L685); [L6c] closure on the full graph with outside
  vertices blued — no induced subgraph ever built.
- **Index convention**: `len(ops) = 2n`, `k = 2n−1`, 0-based op `z−1` produces `X_z`, signs
  exactly {+1, −1}. Audited correct (round 5).
- **Suitability**: core = D1–D4 + every vertex in some bag (caller's responsibility; weaker than
  the paper, so disconnected/edgeless work internally); outside API = connected + valid PD
  (round 16).
- **Scope**: pathwidth construction out unless asked (your API point 2); examples/guarantee
  display deferred to your notebook phase; the old demo's factual error about ZF sets ignored
  per your instruction; API point 3 closed as none (round 11).
- **Housekeeping**: no push, no remote changes; `SPEC.md` and `resources/` untouched; your
  uncommitted [AGENTS.md](AGENTS.md) edit and the untracked reference files (`SPEC.md`,
  `resources/`, `spec2`) left as-is; your `demo.ipynb` stays untracked by your ruling
  (round 18); `.ipynb_checkpoints/` ignored.
- You are the paper's author: nothing here asks you to confirm a fact from your own paper;
  relied-upon statements are cited by tex line in [SPEC-v1.md](SPEC-v1.md) §2.

## 4. Agent findings (informational — no need to read unless auditing)

- **Forget-first is forced, not a preference** (round 9): see §3 nice-ification; recorded in
  [SPEC-v1.md](SPEC-v1.md) §7.3.
- **The trivial fort V is paper-faithful** (round 9): the loop evaluates W at z=k+1
  (tex:L639–642); with t=0, W = white(∅, G) = V, so V joins F and the final `A.reverse()` flips
  the last chain. Hence every run on n≥1 returns at least one fort.
- **Empty intermediate bags** (rounds 9, 16): width-preserving nicification of disconnected
  inputs passes through ∅; the core replays ops without D3 checks and handles it. Since round 16
  this path is reachable only by calling the internal core directly.
- **Path vs tree decomposition** (round 11): `NicePathDecomposition` and Algorithm 1 are
  path-specific (linear ops, interval regions); a tree decomposition would be a different
  algorithm, not a rename.
- **v0 typos resolved** (round 1): the [L6c] blue set is `(V \ X_t^z) ∪ X_t ∪ X_z` (v0's literal
  reading blues everything); `Arcs.delete` removes by head (`in_arcs[j]`, `out_arcs[i]`).
  [SPEC-v1.md](SPEC-v1.md) §6.1–6.2.
- **Brute-force sanity**: Z(Petersen)=5, Z(K_n)=n−1, Z(K_{1,k})=k−1, Z(P_n)=1 reproduced.
- **Historical only**: the round-1/2 defensive core raised `ValueError` on out-of-range indices,
  empty `from_bags`, non-comparable names, etc. Those behaviors were removed in round 3 and
  exist only in [zf-round2-backup.zip](zf-round2-backup.zip); the active core raises nothing.
