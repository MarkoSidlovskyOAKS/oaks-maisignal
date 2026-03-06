# MAiSIGNAL

Pharmaceutical market intelligence alert system by **OAKS Consulting s.r.o.**

MAiSIGNAL monitors Czech drug regulatory events — specifically SUKL drug unavailability reports — and sends branded transactional email alerts to pharma clients via the [Ecomail API](https://ecomailczv2.docs.apiary.io/). Alerts highlight market opportunities when competitor drugs experience supply disruptions.

## How It Works

1. **SUKL publishes a drug unavailability report** (e.g., LYRICA supply disruption)
2. MAiSIGNAL matches the affected drug to a client's product (e.g., PREGLENIX as a generic alternative)
3. An HTML email alert is generated with UZIS eRECEPT prescription/reimbursement data
4. The alert is delivered via Ecomail's transactional email API

## Project Structure

```
oaks-maisignal/
├── send_maisignal_alert.sh        # Sends transactional email via Ecomail REST API
├── sukl-alert-email-real-data.html # Self-contained HTML email template (inline CSS)
├── config/
│   └── .env                       # Ecomail API key (not committed)
├── .gitignore
├── CLAUDE.md
└── README.md
```

## Prerequisites

- **Bash** (macOS/Linux)
- **Python 3** — used for JSON-escaping HTML content
- **curl** — for Ecomail API calls
- **Ecomail account** with a valid API key

## Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/MarkoSidlovskyOAKS/oaks-maisignal.git
   cd oaks-maisignal
   ```

2. Create the environment file with your Ecomail API key:

   ```bash
   mkdir -p config
   echo 'ECOMAIL_API_KEY="your-api-key-here"' > config/.env
   ```

3. Make the script executable:

   ```bash
   chmod +x send_maisignal_alert.sh
   ```

## Usage

```bash
./send_maisignal_alert.sh
```

The script will:
- Load the API key from `config/.env`
- JSON-escape the HTML email template
- Send the email via `POST https://api2.ecomailapp.cz/transactional/send-message`
- Enable click and open tracking

## Email Content

The alert email includes:

- **SUKL report details** — affected drug, reason for disruption, estimated recovery date, substitute drugs
- **KPI metrics** — quarterly reimbursement figures for the affected drug, the client's product, untapped opportunity value, and total market
- **Prescriber tables** — top 10 prescribers split into those already using the client's product vs. priority targets (LYRICA-only)
- **Pharmacy tables** — top 10 pharmacies with the same split
- **Market opportunity analysis** — actionable interpretation highlighting white spots and expansion potential

## Domain Glossary

| Term | Description |
|------|-------------|
| **SUKL** | Statni ustav pro kontrolu leciv — Czech State Institute for Drug Control |
| **UZIS eRECEPT** | Czech national e-prescription data source for reimbursement/prescription analytics |
| **ATC code** | Anatomical Therapeutic Chemical classification (e.g., N02BF02 = Pregabalin) |
| **LP** | Lecivy pripravek — medicinal product |

## License

Proprietary. (c) OAKS Consulting s.r.o.
