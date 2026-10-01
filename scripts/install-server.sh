#!/bin/sh
# Install dependencies needed to run an instance of Toontown Infinite on a machine with no launcher.
#
# A server needs the game's resources, the host add-on, and the DC file
# from the game section.
#
#   ./install-server.sh --dir /srv/tti
#   /srv/tti/bin/server/"Toontown Infinite Server" --dedicated --port 7000
#
# MongoDB has to be on PATH, or the server has to be pointed at one with
# --mongodb-url.
set -eu

CDN="https://cdn.toontown.io"
DIR="./tti-server"
VERSION=""
CHANNEL="live"
PLATFORM=""

usage() {
    cat >&2 <<USAGE
Usage: ${0##*/} [options]

  --dir DIR         Where to install (default: $DIR).
  --version VER     Which release (default: whatever is current).
  --channel NAME    Which channel to install from (default: $CHANNEL).
  --platform NAME   linux-x64, mac-arm64, mac-x64 or win-x64
                    (default: this machine).
  --cdn URL         Where releases are served from (default: $CDN).

Needs curl, and either jq or python3, to read the release manifests.
USAGE
    exit 2
}

while [ $# -gt 0 ]; do
    case "$1" in
        --dir) [ $# -ge 2 ] || usage; DIR="$2"; shift 2 ;;
        --dir=*) DIR="${1#*=}"; shift ;;
        --version) [ $# -ge 2 ] || usage; VERSION="$2"; shift 2 ;;
        --version=*) VERSION="${1#*=}"; shift ;;
        --channel) [ $# -ge 2 ] || usage; CHANNEL="$2"; shift 2 ;;
        --channel=*) CHANNEL="${1#*=}"; shift ;;
        --platform) [ $# -ge 2 ] || usage; PLATFORM="$2"; shift 2 ;;
        --platform=*) PLATFORM="${1#*=}"; shift ;;
        --cdn) [ $# -ge 2 ] || usage; CDN="${2%/}"; shift 2 ;;
        --cdn=*) CDN="${1#*=}"; CDN="${CDN%/}"; shift ;;
        -h|--help) usage ;;
        *) echo "Unknown option: $1" >&2; usage ;;
    esac
done

command -v curl >/dev/null 2>&1 || { echo "curl is required." >&2; exit 1; }

if command -v jq >/dev/null 2>&1; then
    READER="jq"
elif command -v python3 >/dev/null 2>&1; then
    READER="python3"
else
    echo "Either jq or python3 is required to read the release manifests." >&2
    exit 1
fi

if command -v sha256sum >/dev/null 2>&1; then
    sha256() { sha256sum "$1" | cut -d' ' -f1; }
elif command -v shasum >/dev/null 2>&1; then
    sha256() { shasum -a 256 "$1" | cut -d' ' -f1; }
else
    echo "sha256sum or shasum is required to verify downloads." >&2
    exit 1
fi

if [ -z "$PLATFORM" ]; then
    case "$(uname -s)/$(uname -m)" in
        Linux/x86_64) PLATFORM="linux-x64" ;;
        Darwin/arm64) PLATFORM="mac-arm64" ;;
        Darwin/x86_64) PLATFORM="mac-x64" ;;
        MINGW*/x86_64|MSYS*/x86_64|CYGWIN*/x86_64) PLATFORM="win-x64" ;;
        *)
            echo "No server build for $(uname -s)/$(uname -m). Use --platform." >&2
            exit 1 ;;
    esac
fi

fetch() {
    curl -fsSL --retry 3 --retry-delay 2 "$1"
}

if [ "$CHANNEL" = live ]; then
    RELEASES="$CDN/releases"
else
    RELEASES="$CDN/releases/$CHANNEL"
fi

# Reads a manifest:
flatten() {
    if [ "$READER" = "jq" ]; then
        jq -r '.files | to_entries[]
               | [.key, .value.sha256, (.value.size|tostring),
                  (if .value.exec then "x" else "-" end)]
               | @tsv'
    else
        python3 -c '
import json, sys

manifest = json.load(sys.stdin)

for path, entry in manifest["files"].items():
    print("\t".join((path, entry["sha256"], str(entry["size"]),
                     "x" if entry.get("exec") else "-")))
'
    fi
}

version_of() {
    if [ "$READER" = "jq" ]; then
        jq -r '.version'
    else
        python3 -c 'import json,sys; print(json.load(sys.stdin)["version"])'
    fi
}

if [ -z "$VERSION" ]; then
    VERSION="$(fetch "$RELEASES/latest.json" | version_of)"
    [ -n "$VERSION" ] || { echo "Could not read the current $CHANNEL release." >&2; exit 1; }
fi

echo "Installing Toontown Infinite server tti-$CHANNEL-v$VERSION ($PLATFORM) into $DIR"

mkdir -p "$DIR"
DIR="$(cd "$DIR" && pwd)"

MANIFESTS="$(mktemp -d)"
trap 'rm -rf "$MANIFESTS"' EXIT INT TERM

# The sections a server needs:
for section in resources "host-$PLATFORM" game; do
    if ! fetch "$RELEASES/$VERSION/$section.json" > "$MANIFESTS/$section.json"; then
        echo "No $section in $CHANNEL for $VERSION" >&2
        exit 1
    fi

    flatten < "$MANIFESTS/$section.json" \
        | awk -F'\t' -v section="$section" '!(section == "game" && $1 ~ /(^|\/)client\.zip$/)' \
        >> "$MANIFESTS/files"
done

total="$(wc -l < "$MANIFESTS/files" | tr -d ' ')"
echo "$total files to check."

done_count=0
fetched=0

while IFS="$(printf '\t')" read -r path digest size exec_bit; do
    done_count=$((done_count + 1))
    target="$DIR/$path"

    case "$path" in
        /*|*..*) echo "Refusing the manifest path $path" >&2; exit 1 ;;
    esac

    if [ -f "$target" ] && [ "$(sha256 "$target")" = "$digest" ]; then
        continue
    fi

    mkdir -p "$(dirname "$target")"

    printf '\r[%d/%d] %s' "$done_count" "$total" "$path" >&2

    if ! fetch "$CDN/releases/blob/$digest" > "$target.part"; then
        echo >&2
        echo "Could not download $path" >&2
        exit 1
    fi

    if [ "$(sha256 "$target.part")" != "$digest" ]; then
        echo >&2
        echo "$path arrived corrupt" >&2
        rm -f "$target.part"
        exit 1
    fi

    mv "$target.part" "$target"

    if [ "$exec_bit" = "x" ]; then
        chmod 755 "$target"
    fi

    fetched=$((fetched + 1))
done < "$MANIFESTS/files"

printf '\r%*s\r' 78 '' >&2

mkdir -p "$DIR/astron/data" "$DIR/logs"

SERVER="$DIR/bin/server/Toontown Infinite Server"

if [ "$PLATFORM" = "win-x64" ]; then
    SERVER="$SERVER.exe"
fi

if [ ! -f "$SERVER" ]; then
    echo "The server binary is missing from this release." >&2
    exit 1
fi

if [ ! -f "$DIR/astron/dclass/vanilla.dc" ]; then
    echo "astron/dclass/vanilla.dc is missing from $VERSION; use a newer --version." >&2
    exit 1
fi

chmod 755 "$SERVER" 2>/dev/null || true

echo "Done: $fetched files downloaded, $((total - fetched)) already current."
echo
echo "Start it with:"
echo "  \"$SERVER\" --dedicated --port 7000 --district-name \"Kookyboro\""
echo
echo "Add --mongodb-url mongodb://127.0.0.1:27017/game to use a database you"
echo "already run, rather than letting the server start its own."

if ! command -v mongod >/dev/null 2>&1; then
    echo
    echo "mongod is not on PATH, so the server cannot start its own database."
    echo "Install MongoDB, or pass --mongodb-url."
fi
