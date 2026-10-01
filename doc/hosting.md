# Hosting a server

A Toontown Infinite server is four processes: `mongod`, `astrond`, the UberDOG and the district (AI). There are two ways to bring them up, and they all start the same four processes.

---

## From the launcher

The launcher's **Hosting** tab is the best place to deploy your own instance of Toontown Infinite. Enabling hosting will download the additional files needed to run your own server, and once installed, **Start server** runs it.

A server started there keeps running even when the launcher is closed.

## On a machine with no screen (VPS)

We've made it even easier to deploy your own Toontown Infinite server on a headless machine with the following command:

```
curl -fsSL https://raw.githubusercontent.com/TT-Infinite-Archive/source/master/scripts/install-server.sh | sh -s -- --dir /srv/tti
/srv/tti/bin/server/"Toontown Infinite Server" --dedicated --port 7000
```

`install-server.sh` downloads the parts of a release a server needs: the resources, the host add-on (the server and `astrond`), and the DC file from the game section. Run it again to update and it only fetches what changed.

It installs the current `live` release. `--channel` picks a different one, and `--version` pins an exact release under it.

It works out which build the machine needs on its own: Linux x64, macOS on Apple Silicon or Intel, or Windows x64 from Git Bash or MSYS2. `--platform` overrides that, for staging an install meant for another machine.

The script needs `curl`, and either `jq` or `python3`. The server itself needs [MongoDB](https://www.mongodb.com/docs/manual/administration/install-community/) with `mongod` on `PATH`, unless you point it at a database with `--mongodb-url`.

Only the port players connect to (7000 by default) has to be open in your firewall. The rest of the stack listens on 7010, 7020 and 7030 for itself.

> [!WARNING]
> Be careful when running commands that download and execute scripts from the internet (like the `curl ... | sh` example above). Always review the script at the provided URL before running it to ensure it comes from a trusted source, and understand what it will do on your system.



### Options


| Option            | Meaning                                                                                          |
| ----------------- | ------------------------------------------------------------------------------------------------ |
| `--port`          | The port players connect to. Default 7000.                                                       |
| `--district-name` | What the district is called. Default `Kookyboro`.                                                |
| `--mongodb-url`   | An existing database to use. Without this, the server starts a `mongod` of its own on port 7030. |
| `--settings-file` | The settings this server runs with. Default `server-settings.json`.                              |
| `--status-file`   | Where to report who is online, for the launcher to poll. Default `server-status.json`.           |


Relative paths are taken from the install directory, or from `TTI_DATA_DIRECTORY` if it is set. The database lives in `astron/data` under the same directory.

## What other players need

Players choose **Someone else's** on their launcher's play screen and type in
`address:port`. Saving it puts the server in their bookmarks. The launcher logs them in from there and takes them directly to the Pick-A-Toon screen.

A hosted server keeps its own accounts and creates one the first time a username logs in, so there is nothing for a host to set up per player. The username is the one the player signed into the launcher with, marked with an `@` to keep it clear of the host's own local profiles.

This is why players need an official account first: it keeps usernames from clashing in your database. The password that comes with it is derived from the server's address, so it is worth nothing on any other server. Every server you join still sees your username so only join servers run by hosts you trust.

## Settings and status

These are two separate files:

`server-settings.json` is the host's. The district name, port, EXP multiplier and which zones are open live here; the Hosting tab writes it, and every process in the stack reads it.

`server-status.json` is the district's. It is rewritten every time somebody logs in or out, and only the launcher reads it:

```json
{
  "district": "Kookyboro",
  "available": true,
  "draining": false,
  "version": "tti-live-v1.2.2",
  "population": 2,
  "players": [{"id": 100000001, "name": "Lil Oldman"}],
  "port": 7000,
  "invasion": null,
  "startedAt": 1788113353,
  "updatedAt": 1788113420
}
```

