#!/bin/sh
set -e

case "${1:-test}" in
    test)
        exec sh scripts/test.sh
        ;;
    api)
        exec uvicorn deskpilot.api:app --host 0.0.0.0 --port "${PORT:-8080}"
        ;;
    *)
        exec "$@"
        ;;
esac
