#!/bin/sh
set -e

if [ -n "$INFISICAL_CLIENT_ID" ] && [ -z "$_INFISICAL_INJECTED" ]; then
    if [ -z "$INFISICAL_CLIENT_SECRET" ]; then
        echo "entrypoint: INFISICAL_CLIENT_ID is set but INFISICAL_CLIENT_SECRET is not" >&2
        exit 1
    fi

    INFISICAL_TOKEN=$(infisical login --method=universal-auth \
        --client-id="$INFISICAL_CLIENT_ID" \
        --client-secret="$INFISICAL_CLIENT_SECRET" \
        --plain --silent)
    export INFISICAL_TOKEN
    
    export _INFISICAL_INJECTED=1
    exec infisical run \
        --env="${INFISICAL_ENV:-prod}" \
        --projectId="$INFISICAL_PROJECT_ID" \
        --path="${INFISICAL_PATH:-/}" \
        -- "$0" "$@"
fi

case "${1:-}" in
    ai|uberdog)
        service="$1"
        shift

        # Channel ranges. Fixed for the UberDOG
        # A district normally learns its base channel and name from the gateway when its
        # token is authenticated, so BASE_CHANNEL is set only for a stack with no
        # website behind it:
        if [ "$service" = 'uberdog' ]; then
            : "${BASE_CHANNEL:=1000000}"
            : "${CHANNEL_ALLOCATION:=9999}"
        else
            : "${CHANNEL_ALLOCATION:=999999}"
        fi
        export BASE_CHANNEL CHANNEL_ALLOCATION

        # Written once startup has finished, and what the healthcheck
        # looks for:
        export READY_FILE=/tmp/ready

        set -- python -m "toontown.$service.ServiceStart" \
            --distribution live \
            docker/container.prc \
            "$@"
        ;;
esac

exec "$@"
