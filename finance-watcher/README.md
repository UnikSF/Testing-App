# Finance Watcher

A local-first personal finance web app for tracking expenses, syncing with French bank accounts, and getting AI-powered spending insights.

**Status: in active development**

## What it Does

- Connects to your French bank via **GoCardless Bank Account Data** to sync transactions automatically
- Supports **manual expense entry** alongside the bank sync
- **Categorizes** transactions using seeded rules; uncategorized ones fall back to the Claude API
- Corrections you make teach the rule engine over time
- Tracks **budgets**, **savings goals** with forecasts, **recurring transactions**, and **AI spending insights**

## Tech Stack

- **Frontend:** Next.js 15 (App Router), TypeScript, Tailwind CSS v4, Recharts
- **Backend:** Next.js API routes, better-sqlite3
- **Database:** local SQLite (`data/finance.db`)
- **External APIs:** GoCardless Bank Account Data, Claude API (categorization fallback)
- **Currency:** EUR (France)

## How to Start

```bash
npm install
npm run dev
```

Open `http://localhost:3000`.

Make sure your `.env.local` has the required keys (see `.env.example`):
- `GOCARDLESS_SECRET_ID` / `GOCARDLESS_SECRET_KEY` — for bank sync
- `ANTHROPIC_API_KEY` — for AI categorization fallback

The SQLite database is created automatically at `data/finance.db` on first run.

## Project Structure

```
app/             — Next.js App Router pages and API routes
components/      — React UI components
lib/             — Database access, GoCardless client, categorization logic
data/            — SQLite database file (gitignored)
```
