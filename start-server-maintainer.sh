#!/bin/bash
# For use by maintainers only. This is start-server.sh plus the pieces that need
# credentials: the secret manager wrapper, the .gateway-env fallback, --gateway, and
# --accountdb production.

# Starts the TTI server stack and then the client.
# Launch order: mongod -> astrond -> UberDOG -> AI -> client.
#
# With --client-only the servers are skipped and the client brings its own stack
# up through LocalServerStarter.
set -e

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOGS="$ROOT/logs"
mkdir -p "$LOGS" "$ROOT/astron/logs"

# Secrets reach a server process as environment variables. Infisical hands it over:
#
#   /districts/<name>  GATEWAY_TOKEN
#   /uberdog           GATEWAY_TOKEN, ACCOUNT_SERVICE_SECRET
#
# toontown/server/Deployment.py lists every environment variable a server reads
# a district's name and base channel come from the website when its token is authenticated
#
#
# Linking a developer machine to the "Server" project:
#   infisical login
#   infisical init
#
INFISICAL=0
if command -v infisical >/dev/null 2>&1 \
   && { [ -f "$ROOT/.infisical.json" ] || [ -n "$INFISICAL_PROJECT_ID" ]; }; then
    INFISICAL=1
fi

with_secrets() {
    local path="$1" token="$2"
    shift 2

    if [ "$INFISICAL" -eq 1 ]; then
        infisical run --env="${INFISICAL_ENV:-dev}" --path="$path" --silent \
            ${INFISICAL_PROJECT_ID:+--projectId="$INFISICAL_PROJECT_ID"} -- "$@"
    else
        GATEWAY_TOKEN="$token" \
        ACCOUNT_SERVICE_SECRET="${ACCOUNT_SERVICE_SECRET:-}" \
        "$@"
    fi
}

if [ "$INFISICAL" -eq 0 ]; then
    [ -f "$ROOT/.gateway-env" ] && . "$ROOT/.gateway-env"
fi

# Which account database the UberDOG authenticates against:
#   developer   takes any username; access level 400
#   offline     takes any username; access level 100
#   production  redeems launch tokens from the launcher against the website

ACCOUNTDB="developer"
GATEWAY=0
NO_CLIENT=0
CLIENT_ONLY=0
PROFILE=""

usage() {
    cat >&2 <<USAGE
Usage: ${0##*/} [options]

  --accountdb TYPE  Account database for the UberDOG (default: developer).
                    One of: developer, offline, production.
  --gateway         Open the UberDOG's and the district's sockets to the
                    website. Name review and account migration reach the game
                    and the district registers itself there. Off by default,
                    since a stack with no website behind it would retry forever.
  --no-client       Start the servers only.
  --client-only     Launch the client only.
  --profile NAME    Start the client in local mode as local profile NAME,
                    skipping the main menu and the login screen. Combine with
                    --client-only to test a cold start end to end.

Examples:
  ${0##*/}                                     servers, then the client
  ${0##*/} --accountdb production --no-client  servers only, launcher logins
  ${0##*/} --accountdb production --gateway --no-client
                                               the above, plus the website
                                               gateway for migration testing
  ${0##*/} --client-only                       client alone; use Play > Host
  ${0##*/} --client-only --profile Kid         client alone, cold start as "Kid"
USAGE
    exit 2
}

while [ $# -gt 0 ]; do
    case "$1" in
        --accountdb)
            [ $# -ge 2 ] || usage
            ACCOUNTDB="$2"; shift 2 ;;
        --accountdb=*)
            ACCOUNTDB="${1#*=}"; shift ;;
        --gateway)
            GATEWAY=1; shift ;;
        --no-client)
            NO_CLIENT=1; shift ;;
        --client-only)
            CLIENT_ONLY=1; shift ;;
        --profile)
            [ $# -ge 2 ] || usage
            PROFILE="$2"; shift 2 ;;
        --profile=*)
            PROFILE="${1#*=}"; shift ;;
        -h|--help)
            usage ;;
        *)
            echo "Unknown option: $1" >&2; usage ;;
    esac
done

case "$ACCOUNTDB" in
    developer|offline|production) ;;
    *) echo "Invalid --accountdb: $ACCOUNTDB" >&2; usage ;;
esac

if [ "$CLIENT_ONLY" -eq 1 ] && [ "$NO_CLIENT" -eq 1 ]; then
    echo "--client-only and --no-client together would start nothing." >&2
    usage
fi

if [ "$CLIENT_ONLY" -eq 1 ] && [ "$ACCOUNTDB" != "developer" ]; then
    echo "--accountdb has no effect with --client-only: the client starts its" >&2
    echo "own UberDOG, which reads accountdb-type from dev-server.prc." >&2
    exit 2
fi

PIDS=()
cleanup() {
    echo
    echo "Shutting down..."
    for pid in "${PIDS[@]}"; do
        kill "$pid" 2>/dev/null || true
    done
    wait 2>/dev/null || true
}
trap cleanup EXIT INT TERM

wait_for_port() {
    local port="$1" tries=30
    while ! lsof -nP -iTCP:"$port" -sTCP:LISTEN >/dev/null 2>&1; do
        tries=$((tries - 1))
        if [ "$tries" -le 0 ]; then
            echo "Timed out waiting for port $port" >&2
            exit 1
        fi
        sleep 0.5
    done
}

source "$ROOT/venv/bin/activate"

client_env() {
    if [ -n "$PROFILE" ]; then
        export TTI_SERVER_MODE=local
        export TTI_PROFILE="$PROFILE"
        export TTI_PROFILE_KEY="dev-profile-$PROFILE"
        echo "        local mode, profile \"$PROFILE\""
    fi
}

# Where the client will look for a local server, as the game records it:
configured_port() {
    local port=""

    if [ -f "$ROOT/server-settings.json" ]; then
        port="$(sed -n 's/.*"host-port"[^0-9]*\([0-9][0-9]*\).*/\1/p' \
            "$ROOT/server-settings.json" | head -n 1)"
    fi

    echo "${port:-7000}"
}

if [ "$CLIENT_ONLY" -eq 1 ]; then
    CLIENT_PORT="$(configured_port)"

    if lsof -nP -iTCP:"$CLIENT_PORT" -sTCP:LISTEN >/dev/null 2>&1; then
        echo "Note: something is already listening on $CLIENT_PORT, so the client"
        echo "will connect to it rather than starting a stack of its own."
    fi

    echo "[1/1] Launching client (no servers)..."
    client_env
    python -m toontown.toonbase.ClientStart
    exit 0
fi

DISTRICT="Nuttyboro"
DISTRICT_PATH="$(printf '%s' "$DISTRICT" | tr '[:upper:]' '[:lower:]')"
WANTED_PORT="$(configured_port)"
GATEWAY_FLAG=""
[ "$GATEWAY" -eq 1 ] && GATEWAY_FLAG="--gateway"

require_token() {
    local variable="$1" value="$2" issue="$3"

    if [ "$GATEWAY" -eq 1 ] && [ "$INFISICAL" -eq 0 ] && [ -z "$value" ]; then
        echo "--gateway needs $variable, which neither the environment nor" >&2
        echo ".gateway-env supplies. Issue one from the website checkout:" >&2
        echo >&2
        echo "    $issue" >&2
        echo >&2
        exit 1
    fi
}

require_token UBERDOG_GATEWAY_TOKEN "${UBERDOG_GATEWAY_TOKEN:-}" \
    "pnpm gateway:issue --uberdog uberdog"
require_token AI_GATEWAY_TOKEN "${AI_GATEWAY_TOKEN:-}" \
    "pnpm gateway:issue $DISTRICT"

echo "[1/5] Starting mongod..."
mongod --port 7030 --dbpath "$ROOT/astron/data" > "$LOGS/mongod.log" 2>&1 &
PIDS+=($!)
wait_for_port 7030

echo "[2/5] Starting astrond..."
PORT="$(python "$ROOT/scripts/write_astron_config.py" | tail -n 1)"
case "$PORT" in
    ''|*[!0-9]*)
        echo "Couldn't work out which port to use; see the output above." >&2
        exit 1 ;;
esac

if [ "$PORT" != "$WANTED_PORT" ]; then
    echo "        Port $WANTED_PORT was taken, so the stack is on $PORT."
fi

# A bare address on the join screen goes to 7000, so anywhere else has to be
# typed in full:
if [ "$PORT" != "7000" ]; then
    echo "        On the join screen, type 127.0.0.1:$PORT"
fi
case "$(uname -s)" in
    Linux*)           ASTROND_BIN="astrond-linux" ;;
    Darwin*)          ASTROND_BIN="astrond-darwin-$(uname -m)" ;;
    MINGW*|MSYS*|CYGWIN*) ASTROND_BIN="astrond-win32.exe" ;;
    *) echo "Unsupported platform: $(uname -s)" >&2; exit 1 ;;
esac
(cd "$ROOT/astron" && exec "./$ASTROND_BIN" --loglevel info dev.yml > "$LOGS/astrond.log" 2>&1) &
ASTROND_PID=$!
PIDS+=($ASTROND_PID)
wait_for_port 7010 "$ASTROND_PID" "$LOGS/astrond.log"
wait_for_port "$PORT" "$ASTROND_PID" "$LOGS/astrond.log"

echo "[3/5] Starting UberDOG (accountdb: $ACCOUNTDB, gateway: $([ "$GATEWAY" -eq 1 ] && echo on || echo off))..."
with_secrets /uberdog "${UBERDOG_GATEWAY_TOKEN:-}" \
    python -m toontown.uberdog.ServiceStart \
    --base-channel 1000000 --max-channels 9999 --stateserver 4002 \
    --astron-ip 127.0.0.1:7010 --eventlogger-ip 127.0.0.1:7020 \
    --mongodb-ip mongodb://127.0.0.1:7030/game \
    --accountdb "$ACCOUNTDB" $GATEWAY_FLAG > "$LOGS/uberdog.log" 2>&1 &
PIDS+=($!)

echo "[4/5] Starting AI (gateway: $([ "$GATEWAY" -eq 1 ] && echo on || echo off))..."
with_secrets "/districts/$DISTRICT_PATH" "${AI_GATEWAY_TOKEN:-}" \
    python -m toontown.ai.ServiceStart \
    --base-channel 401000000 --max-channels 999999 --stateserver 4002 \
    --district-name "$DISTRICT" \
    --astron-ip 127.0.0.1:7010 --eventlogger-ip 127.0.0.1:7020 \
    --mongodb-ip mongodb://127.0.0.1:7030/game \
    $GATEWAY_FLAG > "$LOGS/ai.log" 2>&1 &
PIDS+=($!)

sleep 2
if [ "$NO_CLIENT" -eq 1 ]; then
    echo "[5/5] Servers up; skipping the client (--no-client). Ctrl-C to shut down."
    wait
else
    echo "[5/5] Launching client..."
    client_env
    python -m toontown.toonbase.ClientStart
fi