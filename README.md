# MAiSIGNAL

Pharmaceutical market intelligence alert system by **OAKS Consulting s.r.o.**

MAiSIGNAL monitors Czech drug regulatory events — specifically SUKL drug unavailability reports — and sends branded transactional email alerts to pharma clients via the [Ecomail API](https://ecomailczv2.docs.apiary.io/). Alerts highlight market opportunities when competitor drugs experience supply disruptions.

## How It Works

1. **SUKL publishes a drug unavailability report** (e.g., LYRICA supply disruption)
2. MAiSIGNAL matches the affected drug to a client's product (e.g., PREGLENIX as a generic alternative)
3. An HTML email alert is generated with UZIS eRECEPT prescription/reimbursement data
4. The alert is delivered via Ecomail's transactional email API

## Repository Structure

```
oaks-maisignal/
├── snowflake/          # Snowflake SQL init & data layer
├── backend/            # Python alert sender application
├── terraform/          # AWS infrastructure (ECR, ECS, VPC, Lambda)
├── .github/
│   ├── workflows/      # CI/CD pipelines
│   └── dependabot.yml  # Automated dependency updates
├── CLAUDE.md
├── CHANGELOG.md
└── LICENSE
```

| Component | Description | Details |
|-----------|-------------|---------|
| [`snowflake/`](snowflake/README.md) | Snowflake database init scripts, L0 tables, and per-environment schemas | SQLFluff linted |
| [`backend/`](backend/README.md) | Python application — hexagonal architecture, sends alerts via Ecomail API | 99% test coverage |
| [`terraform/`](terraform/README.md) | AWS infrastructure (VPC, ECS Fargate, ECR, Lambda, Secrets Manager, KMS) | Terraform >= 1.5 |

## Quick Start

```bash
# Backend setup
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
echo 'ECOMAIL_API_KEY=your-key' > config/.env
python -m maisignal
```

See each component's README for detailed setup instructions.

## CI/CD & Security

| Tool | Purpose |
|------|---------|
| **GitHub Actions** | Backend CI, deploy to dev/prod, Trivy scan, Checkov scan |
| **Dependabot** | Automated dependency updates (pip, Terraform, Actions, Docker) |
| **CodeQL** | Code scanning and code quality analysis |
| **Secret scanning** | Detects accidentally committed secrets (with push protection) |
| **Trivy** | Container and code vulnerability scanning |
| **Checkov** | Terraform infrastructure-as-code security scanning |

## Domain Glossary

| Term | Description |
|------|-------------|
| **SUKL** | Statni ustav pro kontrolu leciv — Czech State Institute for Drug Control |
| **UZIS eRECEPT** | Czech national e-prescription data source for reimbursement/prescription analytics |
| **ATC code** | Anatomical Therapeutic Chemical classification (e.g., N02BF02 = Pregabalin) |
| **LP** | Lecivy pripravek — medicinal product |

## License

Proprietary. (c) OAKS Consulting s.r.o.
