#!/usr/bin/env bash
# Promote writer intro artifacts into personas/media/{id}/
# - Copies still.jpg, intro.mp4
# - Extracts voice.wav via ffmpeg
# - Converts intro id dashes to underscores to match YAML id convention
set -euo pipefail

PROJ_ROOT="/Users/kaigani/Documents/PROJECTS/DEVELOPMENT/260125 codeywood"
INTRO_DIR="$PROJ_ROOT/projects/260414-writer-introductions"
PERSONAS_DIR="$PROJ_ROOT/skills/writer/personas"
MEDIA_ROOT="$PERSONAS_DIR/media"

mkdir -p "$MEDIA_ROOT"

count=0
for still in "$INTRO_DIR/STILLS/"*.jpg; do
    base=$(basename "$still" .jpg)
    # Convert dashes to underscores for YAML-id convention
    yaml_id="${base//-/_}"
    clip="$INTRO_DIR/CLIPS/${base}.mp4"
    if [[ ! -f "$clip" ]]; then
        echo "MISSING clip: $base"
        continue
    fi
    dst="$MEDIA_ROOT/$yaml_id"
    mkdir -p "$dst"
    cp "$still" "$dst/portrait.jpg"
    cp "$clip"  "$dst/intro.mp4"
    # Extract audio as 48kHz mono WAV (voice sample for voiceclone use)
    ffmpeg -y -loglevel error -i "$clip" -vn -ac 1 -ar 48000 -sample_fmt s16 "$dst/voice.wav"
    count=$((count+1))
    echo "  [$count] $yaml_id"
done

echo "Done: $count writers promoted to $MEDIA_ROOT"
