# Building Panda3D

Nothing here is needed to run the game. `requirements.txt` asks for
`Panda3D>=1.10.16,<1.12`, which pip resolves from PyPI like any other
dependency. This document covers the newer build the macOS client ships with.

---

## Why

Retina Mode needs macOS to honour `dpi-aware`, which Panda3D only does from
1.11 onwards. 1.11 is unreleased, so there is no package for it on PyPI and the
wheel has to be built.

The version range is what keeps that optional:

- With no 1.11 wheel, pip installs 1.10.16 and the game runs with Retina Mode
gated off. The option does not appear on the settings page.
- With one already installed, pip leaves it alone.

## Usage

```
usage: build_panda3d.py [-h] [--output OUTPUT] [--jobs JOBS]
                        [--arch {x86_64,arm64}] [--install-deps]
                        [--keep-work] [--print-pin]

options:
  --output OUTPUT       where to write the wheel; omit to only install
                        dependencies
  --jobs JOBS           how many compile jobs to run at once
  --arch {x86_64,arm64}
                        which architecture to produce. Defaults to the
                        host: each runner builds natively rather than
                        producing a universal wheel
  --install-deps        install the build dependencies first
  --keep-work           leave the build tree behind for inspection
  --print-pin           print the pinned Panda3D revision and exit, so CI
                        can key the built wheel by it
```

## Example

```
python scripts/build_panda3d.py --install-deps
python scripts/build_panda3d.py --output wheels
pip install wheels/*.whl
```

Expect a few minutes. The script clones Panda3D at a pinned revision, gets the dependencies that revision needs, builds a wheel, and then installs that wheel into a throwaway venv.

## The pin

`PANDA3D_REV` at the top of the script fixes which revision gets built. It  
is a commit rather than a branch, because master is where upstream's  
in-progress work lands. Bumping it changes the cache key that  
`publish-client.yml` builds against, so CI picks the change up on its own.

