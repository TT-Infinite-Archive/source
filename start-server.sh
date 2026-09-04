#!/bin/bash
# Starts the TTI server stack and then the client.
# Launch order: mongod -> astrond -> UberDOG -> AI -> client
#
# With --client-only the servers are skipped and the client brings its own stack
# up through LocalServerStarter, same as the launcher in local mode.
set -e

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOGS="$ROOT/logs"
mkdir -p "$LOGS" "$ROOT/astron/logs"

# Which account database the UberDOG authenticates against.
#   developer   the login screen takes any username; access level 400
#   offline     the login screen takes any username; access level 100
#
# Overrides accountdb-type in config/distribution/dev-server.prc.
ACCOUNTDB="developer"
NO_CLIENT=0
CLIENT_ONLY=0
PROFILE=""

usage() {
    cat >&2 <<USAGE
Usage: ${0##*/} [options]

  --accountdb TYPE  Account database for the UberDOG (default: developer).
                    One of: developer, offline.
  --no-client       Start the servers only; don't launch the client.
  --client-only     Launch the client only. Nothing else is started, so the
                    client spins the stack up itself the first time it needs it.
  --profile NAME    Start the client in local mode as local profile NAME,
                    skipping the main menu and the login screen. Combine with
                    --client-only to test a cold start end to end.

Examples:
  ${0##*/}                                     servers, then the client
  ${0##*/} --no-client                         servers only
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
    developer|offline) ;;
    *) echo "Invalid --accountdb: $ACCOUNTDB" >&2; usage ;;
esac

if [ "$CLIENT_ONLY" -eq 1 ] && [ "$NO_CLIENT" -eq 1 ]; then
    echo "--client-only and --no-client together would start nothing." >&2
    usage
fi

# The client's own stack always runs the developer accountdb, since it loads
# dev.prc with no --accountdb of its own:
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
    # Local mode needs a password as well as a name -- it becomes the account's
    # password on the local server:
    if [ -n "$PROFILE" ]; then
        export TTI_SERVER_MODE=local
        export TTI_PROFILE="$PROFILE"
        export TTI_PROFILE_KEY="dev-profile-$PROFILE"
        echo "        local mode, profile \"$PROFILE\""
    fi
}

if [ "$CLIENT_ONLY" -eq 1 ]; then
    if lsof -nP -iTCP:7000 -sTCP:LISTEN >/dev/null 2>&1; then
        echo "Note: something is already listening on 7000, so the client will"
        echo "connect to it rather than starting a stack of its own."
    fi

    echo "[1/1] Launching client (no servers; it starts its own when needed)..."
    client_env
    python -m toontown.toonbase.ClientStart
    exit 0
fi

if lsof -nP -iTCP:7000 -sTCP:LISTEN >/dev/null 2>&1; then
    echo "Port 7000 is already in use." >&2
    exit 1
fi

DISTRICT="Nuttyboro"

echo "[1/5] Starting mongod..."
mongod --port 7030 --dbpath "$ROOT/astron/data" > "$LOGS/mongod.log" 2>&1 &
PIDS+=($!)
wait_for_port 7030

echo "[2/5] Starting astrond..."
python "$ROOT/scripts/write_astron_config.py" > /dev/null
(cd "$ROOT/astron" && exec "./astrond-$(uname -s | tr '[:upper:]' '[:lower:]')" --loglevel info dev.yml > "$LOGS/astrond.log" 2>&1) &
PIDS+=($!)
wait_for_port 7010
wait_for_port 7000

echo "[3/5] Starting UberDOG (accountdb: $ACCOUNTDB)..."
python -m toontown.uberdog.ServiceStart \
    --base-channel 1000000 --max-channels 9999 --stateserver 4002 \
    --astron-ip 127.0.0.1:7010 --eventlogger-ip 127.0.0.1:7020 \
    --mongodb-ip mongodb://127.0.0.1:7030/game \
    --accountdb "$ACCOUNTDB" > "$LOGS/uberdog.log" 2>&1 &
PIDS+=($!)

echo "[4/5] Starting AI..."
python -m toontown.ai.ServiceStart \
    --base-channel 401000000 --max-channels 999999 --stateserver 4002 \
    --district-name "$DISTRICT" \
    --astron-ip 127.0.0.1:7010 --eventlogger-ip 127.0.0.1:7020 \
    --mongodb-ip mongodb://127.0.0.1:7030/game > "$LOGS/ai.log" 2>&1 &
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
