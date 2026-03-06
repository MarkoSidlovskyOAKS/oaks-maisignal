#!/usr/bin/env bash

# ─────────────────────────────────────────────
#  MAiSIGNAL – Ecomail transactional email send
#  Liek: LYRICA | Príjemca: marko.sidlovsky@oaks.cz
# ─────────────────────────────────────────────

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ -f "${SCRIPT_DIR}/config/.env" ]; then
  source "${SCRIPT_DIR}/config/.env"
else
  echo "ERROR: config/.env not found. Create it with ECOMAIL_API_KEY." >&2
  exit 1
fi

if [ -z "${ECOMAIL_API_KEY}" ]; then
  echo "ERROR: ECOMAIL_API_KEY is not set in config/.env." >&2
  exit 1
fi

HTML_FILE="sukl-alert-email-real-data.html"

# JSON-escape the HTML file content
HTML_CONTENT=$(python3 -c "
import json, sys
content = open('${HTML_FILE}').read()
print(json.dumps(content))
")

curl --request POST \
  --url "https://api2.ecomailapp.cz/transactional/send-message" \
  --header "Content-Type: application/json" \
  --header "key: ${ECOMAIL_API_KEY}" \
  --data "{
    \"message\": {
      \"subject\": \"⚠️ MAiSIGNAL: Výpadek LP – LYRICA (Pregabalin)\",
      \"from_name\": \"MAiSIGNAL Alerts\",
      \"from_email\": \"alerts@mailing.oaks.cz\",
      \"reply_to\": \"noreply@mailing.oaks.cz\",
      \"to\": [
        {
          \"email\": \"marko.sidlovsky@oaks.cz\",
          \"name\": \"Marko Sidlovsky\"
        }
      ],
      \"html\": ${HTML_CONTENT},
      \"text\": \"MAiSIGNAL Alert - Vypadek LP: LYRICA (Pregabalin). Duvod: Preruseni dodavky. Platnost od: 2025-01-01. Zdroj: SUKL - Hlaseni nedostupnosti. Vice informaci v HTML verzi emailu.\",
      \"options\": {
        \"click_tracking\": true,
        \"open_tracking\": true
      }
    }
  }"
