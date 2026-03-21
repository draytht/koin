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


### User

| Command | Description |
|---------|-------------|
| `/user create` | Create your finance profile (optional: `currency`, `timezone`) |
| `/user profile` | View your profile |

### Spending

| Command | Description |
|---------|-------------|
| `/spend` | Log an expense (`amount`, `category` required; optional: `merchant`, `note`, `payment_method`, `date`, `recurring`) |

### Income

| Command | Description |
|---------|-------------|
| `/earn log` | Log income (`amount`, `source` required; optional: `note`, `date`) |
| `/earn update` | Correct a logged income entry (`date`, `source` required; optional: `amount`, `new_amount`, `new_source`, `new_note`, `new_date`) |
| `/earn delete` | Delete a mistaken income entry (`date`, `source` required; optional: `amount`) |

### Savings

| Command | Description |
|---------|-------------|
| `/save log` | Log a saving (`amount`, `goal` required; optional: `note`, `date`) |
| `/save list` | View recent savings (optional: `limit`, default 10, max 25) |
| `/save update` | Correct a saving entry (`date`, `goal` required; optional: `amount`, `new_amount`, `new_goal`, `new_note`, `new_date`) |
| `/save delete` | Delete a mistaken saving entry (`date`, `goal` required; optional: `amount`) |

### Debts

| Command | Description |
|---------|-------------|
| `/debt add` | Add a debt (`debt_name`, `creditor`, `total_amount`, `interest_rate`, `minimum_payment` required; optional: `due_date`, `note`) |
| `/debt list` | View all tracked debts |
| `/debt update` | Update a debt's details (`debt_name` required; optional: `total_amount`, `current_balance`, `interest_rate`, `minimum_payment`, `note`) |
| `/debt delete` | Delete a mistakenly added debt (`debt_name` required) |

### Receipts

| Command | Description |
|---------|-------------|
| `/image` | Upload a receipt image to extract and log as an expense (`receipt` required; optional: `category`) |

### AI Analysis

| Command | Description |
|---------|-------------|
| `/ai analyze` | Full financial health analysis (last 30 days) |
| `/ai monthly_plan` | Suggested budget plan for next month (last 90 days) |
| `/ai debt_strategy` | Debt payoff strategy (avalanche vs snowball) |
| `/ai saving_advice` | Personalized saving suggestions |

### Charts

| Command | Description |
|---------|-------------|
| `/graph category_breakdown` | Spending by category pie chart (last 30 days) |
| `/graph income_vs_expenses` | Income vs expenses bar chart (last 90 days) |

### Help

| Command | Description |
|---------|-------------|
| `/help` | Show all commands |
