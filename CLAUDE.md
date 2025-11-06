# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a single-purpose Python script that fetches Pokemon TCG events from the Seagrove TCG API and formats them for Discord posting. It filters events by distance (< 50 miles), date (next 7 days), and event type (League Challenge and League Cup only).

## Running the Script

```bash
python3 ptcg_event_formatter.py
```

This will:
1. Fetch events from Seagrove TCG API
2. Print formatted Discord message to terminal
3. Generate `check_events.html` with all event URLs
4. Automatically open the HTML file in your browser

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

**Single-file architecture** with three main functions:

1. `fetch_and_format_events(x, y)` - ptcg_event_formatter.py:8
   - Makes HTTP request to Seagrove TCG API
   - Handles errors (network, JSON parsing)
   - Calls formatting function with response
   - Returns tuple: (formatted_string, filtered_events_list)

2. `format_events_for_discord(api_response)` - ptcg_event_formatter.py:32
   - Filters events by distance (<50 miles), type, and date (next 7 days)
   - Sorts chronologically
   - Formats output as Discord markdown with headers and event details
   - League Cup events include event website URLs
   - Appends section with Pokemon.com URLs for manual status verification

3. `generate_html_checker(events, filename)` - ptcg_event_formatter.py:156
   - Creates an HTML file with all event URLs
   - Includes a button to open all URLs at once (staggered by 100ms)
   - Provides individual links for each event with date/shop labels
   - Returns the filename of the generated HTML file

**Filtering logic**: Events are filtered in sequence (distance → type → date) and only those passing all filters are included in output.

**Output format**: Main section lists all events, followed by a "Check event statuses" section with Pokemon URLs labeled by date and shop name. This allows manual verification that events aren't cancelled (Seagrove API doesn't include status updates).

**Date formatting**: Uses platform-specific format codes (`%-m`, `%-d`, `%-I`) that work on Unix/macOS but may need adjustment for Windows (`#` instead of `-`).

## API Integration

Base URL: `https://www.seagrovetcg.com/events?x={longitude}&y={latitude}`

Expected response: JSON array of event objects with fields:
- `distance` (float) - distance in miles
- `type` (string) - event type
- `when` (ISO datetime string)
- `city`, `shop`, `street_address` (strings)
- `Event_website` (string, optional) - used for League Cup events
