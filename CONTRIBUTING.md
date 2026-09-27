# Contributing to Toontown Infinite

Thanks for helping out! This guide explains how to run the game from source and how to send in changes.

## Issues

Use issues for **code problems only**. If you need help installing or starting the game, ask on [Discord](https://discord.toontown.io); setup issues opened here will be closed.

A good bug report says what you did, what you expected and what actually happened.

## Running from source

### Requirements

- **Python 3.14**
- **MongoDB**, with `mongod` on your `PATH`

The art lives in the [resources](https://github.com/TT-Infinite-Archive/resources) repository, pinned here as a submodule at `resources/`. Clone with it:

```sh
git clone --recursive https://github.com/TT-Infinite-Archive/source.git
```

In an existing clone, or after a pull that moves the pin, run `git submodule update --init`.



### Setup

The game needs a Panda3D 1.11 build that isn't on PyPI, so you build it first:

```sh
python3.14 -m venv venv
source venv/bin/activate

python scripts/build_panda3d.py --install-deps
python scripts/build_panda3d.py --output wheels
pip install wheels/*.whl -r requirements.txt
```



### Starting the game

`start-server.sh` starts the whole local stack in this order: MongoDB, Astron, UberDOG, an AI district and the client. Logs go to `logs/`.

```sh
./start-server.sh                        # servers, then the client
./start-server.sh --no-client            # servers only
./start-server.sh --client-only          # client alone; it starts its own stack when needed
./start-server.sh --client-only --profile Kid   # skip the menu and log in as local profile "Kid"
```

`--accountdb developer` is the default and gives full developer access. Use `--accountdb offline` to play as a normal player. With either option the login screen accepts any username.

Host settings such as the district name, port, XP multiplier and enabled zones are read from `server-settings.json` in the repository root.

## Project layout


| Path                    | Contents                                                  |
| ----------------------- | --------------------------------------------------------- |
| `toontown/`             | Game code: client, AI and UberDOG                         |
| `otp/`                  | The OTP engine layer that Toontown is built on            |
| `astron/`               | Prebuilt Astron server binaries and the dclass files      |
| `config/`               | Panda3D `.prc` config files, per distribution and holiday |
| `docker/`, `Dockerfile` | Server images and the production compose stack            |
| `scripts/`              | Development helpers, such as the Panda3D build script     |
| `doc/`                  | Style guides and the release process                      |




## Branches

Only `[master](https://github.com/TT-Infinite-Archive/source/tree/master)` is actively maintained. The other branches come from the original development and are kept exactly as they were. They haven't been updated for modern Python or Panda3D. You're welcome to repair one and open a pull request.

## Pull requests

- Branch off `master`. Put the branch in one of these categories: `bugfix/`, `enhancement/`, `feature/`, `test/` or `wip/`. Branch names are lowercase with dashes, e.g. `bugfix/trolley-crash`.
- Write commit messages in [Conventional Commits](https://www.conventionalcommits.org/) style: `type(scope): lowercase summary`, e.g. `fix(minigames): stop the trolley from leaving without toons`.
- Follow the [Python style guide](doc/style-guide/python-style.md).
- Keep each pull request to one change, and explain what it fixes and how you tested it.

