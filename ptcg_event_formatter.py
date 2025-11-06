import json
import requests
import webbrowser
import argparse
import os
from datetime import datetime, timedelta

def fetch_and_format_events(x=-122.268863475967, y=37.868310020438):
    """
    Fetch events from Seagrove TCG API and format for Discord

    Args:
        x: Longitude coordinate (default is your provided value)
        y: Latitude coordinate (default is your provided value)

    Returns:
        tuple: (formatted_string, filtered_events_list)
    """
    # Make API request
    url = f"https://www.seagrovetcg.com/events?x={x}&y={y}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        events = response.json()
        print(f"Fetched {len(events)} total events from API")
    except requests.exceptions.RequestException as e:
        return f"Error fetching events: {e}"
    except json.JSONDecodeError as e:
        return f"Error parsing JSON response: {e}"
    
    return format_events_for_discord(events)

def format_events_for_discord(api_response):
    """
    Parse API response and format events for Discord
    Filters for events within 50 miles and next 7 days
    
    Args:
        api_response: JSON string or dict containing event data
    
    Returns:
        str: Formatted string ready for Discord
    """
    # Handle both JSON string and dict inputs
    if isinstance(api_response, str):
        events = json.loads(api_response)
    else:
        events = api_response

    # If the response is a single event (dict), wrap it in a list
    if isinstance(events, dict):
        events = [events]
    
    # Set up filtering criteria
    current_time = datetime.now()
    seven_days_from_now = current_time + timedelta(days=7)
    
    filtered_events = []
    
    for event in events:
        # Filter by distance (must be less than 50 miles)
        distance = event.get('distance', 0)
        if distance >= 50:
            continue
        
        # Filter by event type (only League Challenge and League Cup)
        event_type = event.get('type', '')
        if event_type not in ['League Challenge', 'League Cup']:
            continue
            
        # Filter by date (must be within next 7 days)
        try:
            event_datetime = datetime.fromisoformat(event['when'].replace('Z', '+00:00'))
            event_datetime = event_datetime.replace(tzinfo=None)  # Remove timezone for comparison
            
            if event_datetime < current_time:
                continue
            elif event_datetime > seven_days_from_now:
                continue
                
        except (ValueError, KeyError):
            continue
            
        # Event passed all filters
        filtered_events.append(event)
    
    print(f"Found {len(filtered_events)} events within 50 miles in the next 7 days (out of {len(events)} total)")

    if not filtered_events:
        return "No events found within 50 miles in the next 7 days."

    # Sort events by datetime
    def get_event_datetime(event):
        try:
            return datetime.fromisoformat(event['when'].replace('Z', '+00:00')).replace(tzinfo=None)
        except (ValueError, KeyError):
            return datetime.min  # Put events with invalid dates at the beginning

    filtered_events.sort(key=get_event_datetime)

    # Helper function to format an event
    def format_event(event):
        # Parse the datetime (we already validated it in filtering)
        event_datetime = datetime.fromisoformat(event['when'].replace('Z', '+00:00'))
        event_datetime = event_datetime.replace(tzinfo=None)

        # Format day of week and date (Fri 9/26)
        day_date = event_datetime.strftime("%a %-m/%-d")  # Use %-m and %-d to remove leading zeros

        # Format time (6:30 PM)
        time_formatted = event_datetime.strftime("%-I:%M %p")  # %-I removes leading zero from hour

        # Extract shop name from the full name or use shop field
        shop_name = event.get('shop', 'Unknown Shop')

        # Use the full street address as provided
        street_address = event['street_address']

        # Format the message
        formatted_message = f"**{day_date} {time_formatted}** {event['city']} {shop_name} {event['type']}\n{street_address}"

        # Add event website for League Cup events
        if event.get('type') == 'League Cup':
            event_website = event.get('Event_website', '')
            if event_website:
                formatted_message += f"\n{event_website}"

        return formatted_message

    # Create header with date range
    start_date = current_time.strftime("%b %-d")
    end_date = seven_days_from_now.strftime("%b %-d")
    header = f"**Upcoming Championship Point Events** (Week of {start_date}-{end_date}):"

    formatted_messages = [header]

    # Format all events
    for event in filtered_events:
        formatted_messages.append(format_event(event))

    # Add section with Pokemon URLs for manual status verification
    formatted_messages.append("")  # Add spacing
    formatted_messages.append("**Check event statuses (click to verify not cancelled):**")

    for event in filtered_events:
        pokemon_url = event.get('pokemon_url', '')
        if pokemon_url:
            shop_name = event.get('shop', 'Unknown Shop')
            event_datetime = datetime.fromisoformat(event['when'].replace('Z', '+00:00'))
            event_datetime = event_datetime.replace(tzinfo=None)
            day_date = event_datetime.strftime("%a %-m/%-d")
            formatted_messages.append(f"{day_date} {shop_name}: {pokemon_url}")

    return '\n\n'.join(formatted_messages), filtered_events

def generate_html_checker(events, filename='check_events.html'):
    """
    Generate an HTML file with a button to open all event URLs for status checking

    Args:
        events: List of event dictionaries with pokemon_url field
        filename: Name of the HTML file to create

    Returns:
        str: Path to the generated HTML file
    """
    html_content = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Pokemon TCG Event Status Checker</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            max-width: 800px;
            margin: 40px auto;
            padding: 20px;
            background: #f5f5f5;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            margin-top: 0;
        }
        button {
            background: #0066cc;
            color: white;
            border: none;
            padding: 12px 24px;
            font-size: 16px;
            border-radius: 6px;
            cursor: pointer;
            margin: 10px 0;
        }
        button:hover {
            background: #0052a3;
        }
        .event-list {
            margin-top: 20px;
        }
        .event {
            padding: 10px;
            margin: 8px 0;
            background: #f8f9fa;
            border-radius: 4px;
        }
        .event a {
            color: #0066cc;
            text-decoration: none;
        }
        .event a:hover {
            text-decoration: underline;
        }
        .info {
            color: #666;
            font-size: 14px;
            margin-top: 15px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎴 Pokemon TCG Event Status Checker</h1>
        <p>Click the button below to open all event pages and verify they are sanctioned (not cancelled).</p>

        <button onclick="openAllEvents()">Open All Events (""" + str(len(events)) + """ tabs)</button>

        <div class="event-list">
            <h3>Events:</h3>
"""

    # Add each event
    for event in events:
        pokemon_url = event.get('pokemon_url', '')
        if pokemon_url:
            shop_name = event.get('shop', 'Unknown Shop')
            event_datetime = datetime.fromisoformat(event['when'].replace('Z', '+00:00')).replace(tzinfo=None)
            day_date = event_datetime.strftime("%a %m/%d")

            html_content += f"""            <div class="event">
                <strong>{day_date}</strong> - {shop_name}<br>
                <a href="{pokemon_url}" target="_blank">{pokemon_url}</a>
            </div>
"""

    # Add JavaScript and closing tags
    html_content += """        </div>

        <div class="info">
            <p><strong>Note:</strong> Your browser may block multiple tabs from opening at once. If this happens, you may need to allow pop-ups for this page or click the links individually.</p>
        </div>
    </div>

    <script>
        function openAllEvents() {
            const urls = [
"""

    # Add URLs to JavaScript array
    for i, event in enumerate(events):
        pokemon_url = event.get('pokemon_url', '')
        if pokemon_url:
            comma = ',' if i < len(events) - 1 else ''
            html_content += f'                "{pokemon_url}"{comma}\n'

    html_content += """            ];

            urls.forEach((url, index) => {
                setTimeout(() => {
                    window.open(url, '_blank');
                }, index * 100); // Stagger opening by 100ms to avoid browser blocking
            });
        }
    </script>
</body>
</html>
"""

    # Write to file
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html_content)

    return filename

# Example usage:
if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Fetch and format Pokemon TCG events for Discord')
    parser.add_argument('--no-browser', action='store_true',
                        help='Do not automatically open the HTML checker in browser')
    args = parser.parse_args()

    # Fetch events from API and format for Discord
    print("Fetching events from Seagrove TCG API...")
    result, events = fetch_and_format_events()

    print("\nFormatted for Discord:")
    print("=" * 50)
    print(result)
    print("=" * 50)
    print("\nCopy the text above and paste it into Discord!")

    # Generate HTML checker
    if events:
        html_file = generate_html_checker(events)
        print(f"\nGenerated {html_file} for easy status checking.")

        # Open HTML file in browser unless --no-browser flag is set
        if not args.no_browser:
            print("Opening status checker in your browser...")
            abs_path = os.path.abspath(html_file)
            webbrowser.open('file://' + abs_path)
        else:
            print(f"Run 'open {html_file}' to check event statuses.")

    # You can also use custom coordinates if needed:
    # result, events = fetch_and_format_events(x=-122.5, y=37.5)  # Different location
