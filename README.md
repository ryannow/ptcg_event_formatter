A script to download local Pokemon TCG events and output formatted markdown to share in Discord. Uses SeagroveTCG's website since the event locator redesign.

## Features

- Fetches events from Seagrove TCG API (replaces the broken Pokemon event locator)
- Filters for League Challenge and League Cup events within 50 miles and next 7 days
- Outputs Discord-formatted markdown for easy posting
- Generates an HTML file with a "Check All" button to quickly verify event statuses

## Usage

```bash
pip install -r requirements.txt
python3 ptcg_event_formatter.py
```

This will:
1. Print formatted Discord message to your terminal
2. Generate `check_events.html` with all event URLs
3. Automatically open the HTML file in your browser for status checking

Click the "Open All Events" button in the HTML page to open all event URLs at once, then verify they are sanctioned (not cancelled).

Use `--no-browser` flag to skip auto-opening the browser:
```bash
python3 ptcg_event_formatter.py --no-browser
```
