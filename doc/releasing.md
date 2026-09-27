# Releasing

For maintainers. This page covers how a release gets from `master` to players. The steps themselves run in `[.github/workflows/release.yml](../.github/workflows/release.yml)`.

---

## Channels


| Channel | Who plays it                                           |
| ------- | ------------------------------------------------------ |
| `live`  | Everyone. This is what the launcher offers by default. |
| `qa`    | Testers. It runs on its own server.                    |


Each channel's server has its own runner, labelled with the channel name.

## Versions and tags

A release is a tag named `tti-<channel>-v<version>`, e.g. `tti-live-v1.2.0` or `tti-qa-v1.2.0`.

There are two kinds of version:

- **Full release** (`1.2.0`): builds and deploys new server images, publishes the client and updates the protocol the channel serves.
- **Revision** (`1.2.0a`, `1.2.0b`, ...): a client-only update on top of a full release. It doesn't build or deploy the servers.

A revision is only allowed if nothing the servers load has changed since its full release, and if the protocol matches what the channel serves. The release workflow checks both and fails if either one doesn't hold. When it fails, cut a full release instead.

## The protocol

`server-version` in `[config/distribution/live.prc](../config/distribution/live.prc)` is the protocol version, e.g. `tti-live-p1`. Clients and servers only connect if their protocols match. The Astron image is tagged with the protocol, so it's only published once per protocol.

**Bump the protocol whenever** `astron/dclass/` **changes.** A full release fails if the DC file changed but the protocol still matches an earlier release.

## Cutting a release

From a checkout with the build tools at `tools/`:

```sh
python tools/release.py                # asks for the channel and version
python tools/release.py live-1.2.0     # checks and tags live 1.2.0
python tools/release.py --dry-run      # runs every check but doesn't tag or push
```

The script checks what changed, suggests whether it can ship as a revision and pushes the tag. You can also run the **Release** workflow by hand with a version and a channel.

When the tag is pushed, the workflow:

1. Resolves the version and channel, and checks the protocol.
2. Builds and pushes the server images. On a full release, `live` also gets `:latest`.
3. Builds the client for each platform and uploads it to R2.
4. Deploys to the channel's server. MongoDB, Astron and UberDOG start first, then the districts restart one at a time.
5. Promotes the release by pointing the channel's `latest.json` at it. The launcher only sees the release after this step, so players are never offered a client that no server accepts.
6. On `live`, tells the website about the release. The website then whispers the Toons who are online.

## Rolling back

Run the **Deploy** workflow by hand with the previous image tag, e.g. `tti-live-v1.1.0`, and the channel. This rolls back only the servers. `latest.json` keeps pointing at the newer client until another release is promoted.

## Housekeeping

The **Prune releases** workflow runs on the 1st of every month. It deletes client files on R2 that no kept release uses.