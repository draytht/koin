# Koin — Personal AI Finance Discord Bot

A private Discord bot that acts as your personal financial operating system.

## Setup

1. Clone and enter the project directory
2. Copy `.env.example` to `.env` and fill in your credentials
3. Run the database migration in Supabase SQL editor (`db/migrations/001_initial_schema.sql`)
4. Create a private `receipts` bucket in Supabase Storage
5. Install dependencies: `pip install -r requirements.txt`
6. Install system dependencies: `sudo apt install tesseract-ocr libmagic1`
7. Run: `python -m bot.main`

## Docker

```bash
cp .env.example .env
# Fill in .env
docker-compose up -d
```

## First Use

In Discord, run `/user create` to set up your profile, then `/help` to see all commands.


| Command | Description |
|---------|-------------|
| `/user create` | Create your profile |
| `/spend` | Log an expense |
| `/earn` | Log income |
| `/debt add/list/update` | Track debts |
| `/image` | Upload receipt for auto-extraction |
| `/ai analyze` | Full financial analysis |
| `/ai monthly_plan` | Budget plan |
| `/ai debt_strategy` | Debt payoff strategy |
| `/ai saving_advice` | Saving suggestions |
| `/graph category_breakdown` | Spending pie chart |
| `/graph income_vs_expenses` | Monthly bar chart |
| `/help` | Show all commands |
