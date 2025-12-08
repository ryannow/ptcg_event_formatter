# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python script that fetches Pokemon TCG events from the Seagrove TCG API and formats them for Discord posting. It generates two formatted message blocks:
1. **Weekly events**: All Championship Point events (League Challenge and League Cup) within 50 miles in the next 7 days
2. **Monthly League Cups**: Only League Cup events within 50 miles in the next 30 days

## Running the Script

```bash
python3 ptcg_event_formatter.py
```

This will:
1. Fetch events from Seagrove TCG API (single API call)
2. Print formatted Discord message for weekly events
3. Generate `check_events.html` with weekly event URLs
4. Print formatted Discord message for monthly League Cups
5. Generate `check_league_cups.html` with League Cup URLs
6. Automatically open both HTML files in your browser

To skip auto-opening the browser:
```bash
python3 ptcg_event_formatter.py --no-browser
```

The script uses hardcoded default coordinates (x=-122.268863475967, y=37.868310020438) but can be customized by passing different coordinates to `fetch_and_format_events()`.

## Dependencies

Install with: `pip install -r requirements.txt`

Required packages:
- `requests` - for HTTP API calls to Seagrove TCG
- Standard library: `json`, `datetime`

## Code Architecture

**Single-file architecture** with the following functions:

### Helper Functions

1. `get_event_datetime(event)` - ptcg_event_formatter.py:60
   - Extracts datetime from event dictionary
   - Returns datetime.min for invalid dates
   - Used for sorting events chronologically

2. `format_event(event)` - ptcg_event_formatter.py:72
   - Formats a single event as Discord markdown
   - Includes date, time, location, and shop info
   - Adds event website URL for League Cup events
   - Reused by both formatting functions

### Main Functions

3. `fetch_and_format_events(x, y)` - ptcg_event_formatter.py:8
   - Makes HTTP request to Seagrove TCG API
   - Handles errors (network, JSON parsing)
   - Calls `format_events_for_discord()` with response
   - Returns tuple: (formatted_string, filtered_events_list)

4. `fetch_and_format_league_cups(x, y)` - ptcg_event_formatter.py:34
   - Makes HTTP request to Seagrove TCG API
   - Handles errors (network, JSON parsing)
   - Calls `format_league_cups_for_discord()` with response
   - Returns tuple: (formatted_string, filtered_events_list)

5. `format_events_for_discord(api_response)` - ptcg_event_formatter.py:108
   - Filters events by distance (<50 miles), type (League Challenge + League Cup), and date (next 7 days)
   - Sorts chronologically using `get_event_datetime()`
   - Formats output using `format_event()` helper
   - Appends section with Pokemon.com URLs for manual status verification
   - Returns tuple: (formatted_string, filtered_events_list)

6. `format_league_cups_for_discord(api_response)` - ptcg_event_formatter.py:174
   - Filters events by distance (<50 miles), type (League Cup only), and date (next 30 days)
   - Sorts chronologically using `get_event_datetime()`
   - Formats output using `format_event()` helper
   - Appends section with Pokemon.com URLs for manual status verification
   - Returns tuple: (formatted_string, filtered_events_list)

7. `generate_html_checker(events, filename)` - ptcg_event_formatter.py:261
   - Creates an HTML file with all event URLs
   - Includes a button to open all URLs at once (staggered by 100ms)
   - Provides individual links for each event with date/shop labels
   - Returns the filename of the generated HTML file

**Filtering logic**: Events are filtered in sequence (distance → type → date) and only those passing all filters are included in output.

**Output format**: Main section lists all events, followed by a "Check event statuses" section with Pokemon URLs labeled by date and shop name. This allows manual verification that events aren't cancelled (Seagrove API doesn't include status updates).

**Main execution**: When run as a script, the main block makes a single API call and reuses the data for both formatters (weekly events and monthly League Cups), improving performance and reliability.

**Date formatting**: Uses platform-specific format codes (`%-m`, `%-d`, `%-I`) that work on Unix/macOS but may need adjustment for Windows (`#` instead of `-`).

## API Integration

Base URL: `https://www.seagrovetcg.com/events?x={longitude}&y={latitude}`

Expected response: JSON array of event objects with fields:
- `distance` (float) - distance in miles
- `type` (string) - event type
- `when` (ISO datetime string)
- `city`, `shop`, `street_address` (strings)
- `Event_website` (string, optional) - used for League Cup events
