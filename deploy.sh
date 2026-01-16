#!/bin/bash
# Deploy decks to SharePoint folder or local Downloads
# Reads destination from .env.local (gitignored)
#
# Usage:
#   ./deploy.sh              Deploy all to SharePoint
#   ./deploy.sh file.html    Deploy specific file to SharePoint
#   ./deploy.sh --local      Deploy all to ~/Downloads/
#   ./deploy.sh --local file.html  Deploy specific file to ~/Downloads/

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$SCRIPT_DIR/.env.local"
LOCAL_EXPORT_PATH="$HOME/Downloads"
USE_LOCAL=false
TARGET_FILE=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --local|-l)
            USE_LOCAL=true
            shift
            ;;
        *)
            TARGET_FILE="$1"
            shift
            ;;
    esac
done

# Determine destination
if [ "$USE_LOCAL" = true ]; then
    DEST_PATH="$LOCAL_EXPORT_PATH"
    DEST_NAME="Downloads"

    # Create Downloads directory if it doesn't exist
    if [ ! -d "$DEST_PATH" ]; then
        mkdir -p "$DEST_PATH"
    fi
else
    # Load config for SharePoint
    if [ ! -f "$ENV_FILE" ]; then
        echo "Error: .env.local not found"
        echo "Copy .env.local.example to .env.local and set your SharePoint path"
        echo "Or use --local to export to ~/Downloads/"
        exit 1
    fi

    source "$ENV_FILE"

    if [ -z "$SHAREPOINT_DECKS_PATH" ]; then
        echo "Error: SHAREPOINT_DECKS_PATH not set in .env.local"
        exit 1
    fi

    # Check destination exists
    if [ ! -d "$SHAREPOINT_DECKS_PATH" ]; then
        echo "Error: SharePoint folder not found: $SHAREPOINT_DECKS_PATH"
        echo "Make sure the folder is synced and mounted"
        exit 1
    fi

    DEST_PATH="$SHAREPOINT_DECKS_PATH"
    DEST_NAME="SharePoint"
fi

# Deploy specific file or all
if [ -n "$TARGET_FILE" ]; then
    # Deploy specific file
    if [ ! -f "$SCRIPT_DIR/docs/$TARGET_FILE" ]; then
        echo "Error: File not found: docs/$TARGET_FILE"
        exit 1
    fi
    cp "$SCRIPT_DIR/docs/$TARGET_FILE" "$DEST_PATH"
    echo "✓ Deployed: $TARGET_FILE → $DEST_NAME"
else
    # Deploy all decks
    count=0
    for f in "$SCRIPT_DIR/docs/"*.html; do
        if [ -f "$f" ]; then
            cp "$f" "$DEST_PATH"
            echo "✓ $(basename "$f")"
            count=$((count + 1))
        fi
    done
    echo ""
    echo "Deployed $count decks to $DEST_NAME ($DEST_PATH)"
fi
