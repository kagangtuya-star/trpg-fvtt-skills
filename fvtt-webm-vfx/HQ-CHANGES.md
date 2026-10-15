# High-Quality update

This package is the high-quality variant of the FVTT WebM VFX skill.

## What changed
- **Forced high-quality rendering** in `scripts/build_vfx.py`:
  - minimum `render_scale = 2` (internal supersampling before downscale)
  - default VP9 alpha encode upgraded to `crf=22`, `deadline=good`, `cpu_used=2`
  - manifest now records HQ settings
- **Skill instructions updated** in `SKILL.md` to explicitly forbid low-quality / fast-placeholder output.
- Added **new sample recipes**:
  - `assets/recipes/jjk-blue-pull-collapse-hq.json`
  - `assets/recipes/jjk-red-charge-core-hq.json`
  - `assets/recipes/jjk-red-projectile-burst-hq.json`
- Added helper sprite:
  - `assets/sprites/red-core.png`

## Render command
```bash
python3 scripts/build_vfx.py --recipe assets/recipes/jjk-blue-pull-collapse-hq.json --outdir out
```

## Important behavior
Even if a recipe tries to request lower quality, the script now clamps it to **at least 2x render scale**.
