# HANDOFF — zf-approx

**Where to take off:** read §1 (design principles) and §4 (next rounds), then fill in §6 (your
comment area). Current status is §2, git is §3. All deliverables are committed at `76700f8`
(local, not pushed); this handoff file itself is uncommitted.

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

## 2. Current status (rounds 1–5, 2026-11-20/21)

**Done and verified:**
- Lean core `zf/` (~370 lines, 6 modules), **zero** `try`/`except`/`raise`:
  - `graph.py` — `Graph`: static, 0-based, name bijection (`names` index→name, `index` name→index),
    edge list, `adj`; output views `to_names(vertices)` and `arcs_to_names(arcs)`.
  - `arcs.py` — `Arcs`: `out_arcs`/`in_arcs` (−1 = absent), dynamic `count`/`__len__`,
    `add`/`delete(heads)`/`reverse`/`extend`/`sources(vertices=None)`/`arcs()`.
  - `decomposition.py` — `NicePathDecomposition`: `ops=(v,±1)`, `bags`/`k`/`width`, `from_bags`;
    no validation.
  - `closure.py` — `closure(graph, blue) -> (white, arcs)`: Brimkov–Fast–Hicks count engine
    (complementary white counts), **min-index canon** (min-heap), stale-entry guard.
  - `algorithm.py` — `zero_forcing_set(graph, pd) -> ZFResult(zf_set, forts, arcs)`:
    Algorithm L1–L8 with the three tricks.
- **Tricks:** [L3] introduce steps and forgets of vertices in `X_t` skip closure; [L6b] `S`
  computed once at the end (`A.sources()`); [L6c] closure on the FULL graph with outside vertices
  blued (no induced subgraph ever built).
- **Canon:** smallest-eligible-index = paper tex:L621 = the parallel project's `zf_closure.py`;
  arc-for-arc parity verified (960/960 round 2; 480/480 round 3).
- `examples.py` — 8 explicit blocks (path a-b-c, P3, P4, C5 A/B, star, K4, C5 fort from `[0]`,
  sources-mask demo); all assertions pass (`python3 examples.py`).
- Docs: `SPEC-v1.md` (living spec, lean contract), `docs/definitions.md` (all math definitions,
  one per line), `docs/closure-review.md` (B-F-H comparison), `REPORT.md` (rounds 1–5).
- Backup: `zf-round2-backup.zip` = round-2 defensive core + 112-test suite + examples + README,
  preserved verbatim.

**Key math facts (do not re-derive):**
- Indexing: `ops` length `2n`; `k = 2n−1` non-empty bags; 0-based op `z−1` produces `X_z`; signs
  exactly `{+1, −1}` (no `0` op). Audited correct in code and report.
- `sources(vertices)` = `sources ∩ mask`: needed because [L6c] blues outside vertices, which
  otherwise appear as spurious sources. The main algorithm computes `sources(A)` once at the end
  over all `V`, so it needs no mid-loop mask.
- Input suitability = D1–D4 + every vertex in some bag; the caller's responsibility (weaker than
  the paper's connectedness assumption, so edgeless/disconnected graphs work).
- Paper: arXiv:2402.08866v1. Algorithm box tex:L623–665; canon tex:L621; "S once at end" remark
  tex:L685; closure subroutine = Brimkov–Fast–Hicks, EJOR 273(3):889–903 (2019), Algorithm 1.
  Local tex: `resources/paper/arXiv-2402.08866v1/2024-02-13-Zero_Forcing_Approx_Alg.tex`.

## 3. Git state

- The core deliverables are in commit `76700f8` (12 files). This handoff is committed on top of
  it (the latest commit — run `git log` to see its hash). Everything is local; nothing is pushed.
- Files in the repository: the 12 deliverables, this handoff, and the baseline `.gitignore`,
  `AGENTS.md`, `HANDOFF.md`.
- Left as-is (not committed): your edit to `AGENTS.md`. Never added to the repository:
  `SPEC.md` (your v0), `resources/` (the papers), `spec2` (not created by me).
- No push and no remote change (AGENTS.md rule 7).

## 4. What I expect to do next round (I will confirm scope with you first)

1. **One function for the outside.** Today the package exposes several names (`Graph`, `Arcs`,
   `NicePathDecomposition`, `closure`, `zero_forcing_set`, `ZFResult`). You asked for a single
   interface, so I would hide the helpers and leave just one function for you to call.
   *Default: that function is `zero_forcing_set`; tell me what it should take in and give back.*
2. **Where the decomposition comes from.** Today you supply a ready-made nice path decomposition
   (the list of add/remove steps). Building one from a graph is a separate algorithm (pathwidth).
   *Default: not part of this project unless you ask.*
3. **More worked examples.** Name the graphs you want and I will work them through.
   *Default: only when you ask.*
4. **Show the guarantee directly.** The result already satisfies: size of the zero forcing set
   ≤ (width + 1) × (number of forts). I can display this comparison more directly if it helps.
   *Default: only when you ask.*
5. **Keep the spec (`SPEC-v1.md`) and the report (`REPORT.md`) current** each round.
6. **The numbering question** in §5, if you still see a problem.

## 5. Open questions (answer in one line; if you skip, the default applies)

- **Just one function?** Should the package give you only one function to call from outside —
  you pass in a graph and its decomposition, and it returns the zero forcing set, the forts, and
  the arcs, all using your original vertex names — with every helper hidden inside?
  *Default: yes; that one function is `zero_forcing_set`.*
- **Add the left-out files to git?** Your v0 `SPEC.md`, the paper PDFs in `resources/`, and
  `spec2` are not in the repository right now. Should I add them?
  *Default: leave them out.*
- **Any numbering mistake left?** I checked the add/remove step numbering and the +1/−1 signs
  and found them correct. Do you still see a specific place where a number is off by one? If so,
  tell me the file and line.
  *Default: it is correct; nothing to change.*

## 6. Owner comment area (please fill in — feedback / where to take off)

> _Answer any of these, or write free-form notes for me / the next chat:_
>
> - Where should the next chat begin?
>   -
> - What should the one outside function take as input, and give back?
>   -
> - Which graphs or examples do you want next?
>   -
> - Is anything in the "key math facts" (§2) wrong?
>   -
> - What is in scope / out of scope for next round?
>   -
> - Anything else:
>   -

## 7. Pointers

- Spec: `SPEC-v1.md` · definitions: `docs/definitions.md` · review: `docs/closure-review.md` ·
  status: `REPORT.md`.
- Examples: `examples.py` (`python3 examples.py`).
- Prior work + tests: `zf-round2-backup.zip`.
- Paper: `resources/paper/arXiv-2402.08866v1/` · Brimkov PDFs: `resources/brimkov*.pdf`.