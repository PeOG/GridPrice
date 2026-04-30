#!/bin/bash

# Hämtar din text, eller sätter "Automatisk uppdatering" om det är tomt
BAS_KOMMENTAR=${1:-"Automatisk uppdatering"}

# Lägger till klockslag efter din text
FULL_KOMMENTAR="$BAS_KOMMENTAR ($(date +'%Y-%m-%d %H:%M'))"

git add .
git commit -m "$FULL_KOMMENTAR"
git push origin main