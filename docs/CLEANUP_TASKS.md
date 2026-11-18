# Cleanup / backlog tasks — src/zf_npd

Status of the clean-up performed 2026-XX-XX (manager + user). This file is a
management artifact, NOT part of the `src/` package. It records what remains to
be done and the decisions already ratified.

## Decided / done
- `zf_ndp.py` (typo) deleted; its role (L3 driver) is now `zf_npd.py`,
  which carries the module docstring + a `zf_npd()` skeleton.
- `nice_pd` -> `NicePD`, `make_ndp()` -> `make_npd()` (PEP8). Bodies untouched.
- **API form: function-style (spec §9)** — `white(g, B, active)`,
  `fas(g, B, active)`. The class-style `zf_closure` shape in `zf_closure.py` is
  therefore to be refactored away when it is implemented.
- `workspace-ZFImp/` is detached experimental material — NOT a source of truth,
  do not vendor its spec, do not migrate its implementation. The authoritative
  source is `src/zf_npd/` itself.
- Unimplemented bodies are left as `NotImplementedError` skeletons; testing is
  deferred to the end (user instruction).

## Backlog (not yet done, in dependency order)

### P0 — structure blocking import/use
- [ ] Add `src/zf_npd/__init__.py` re-exporting the public API
      (`Graph, build_graph, NicePD, make_npd, ArcSet, white, fas, zf_npd`)
      so `from zf_npd import ...` works.

### P1 — missing implementations (L1/L2 then L3)
- [ ] `zf_graph.py`: `build_graph(n, edges)` (L1)  [file currently skeleton-only]
- [ ] `nice_pd.py`: implement `make_npd()`, `check_nice()` (L1)
- [ ] `zf_closure.py`: rewrite class-style `zf_closure` to **function-style**
      `white(...)` / `fas(...)` (L2) [API decision above]
- [ ] `zf_arcset.py`: implement `extend`, `sources`, `sinks`, `arcs`
      (`__init__/add/reverse/delete_heads/__len__` already present)
- [ ] `zf_npd.py`: implement `zf_npd()` driver (L3)

### P2 — engineering scaffolding
- [ ] `pyproject.toml` (src-layout + pytest config)
- [ ] `tests/` scaffold
- [ ] `examples/` demo entry
- [ ] Stale docstrings that still say "interface skeleton" updated
      once implementations land.

## Open (need a decision, not urgent)
- Test import style: re-export via `__init__.py` (recommended) vs explicit
  `from zf_npd.zf_npd import ...`. Deferred until tests are written.
