import json
import requests
from datetime import datetime, timedelta

def fetch_and_format_events(x=-122.268863475967, y=37.868310020438):
    """
    Fetch events from Seagrove TCG API and format for Discord
    
    Args:
        x: Longitude coordinate (default is your provided value)
        y: Latitude coordinate (default is your provided value)
    
    Returns:
        str: Formatted string ready for Discord
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
    
    # Create header with date range
    start_date = current_time.strftime("%b %-d")
    end_date = seven_days_from_now.strftime("%b %-d")
    header = f"**Upcoming Championship Point Events** (Week of {start_date}-{end_date}):"
    
    formatted_messages = [header]
    
    for event in filtered_events:
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
        
        formatted_messages.append(formatted_message)
    
    return '\n\n'.join(formatted_messages)

# Example usage:
if __name__ == "__main__":
    # Fetch events from API and format for Discord
    print("Fetching events from Seagrove TCG API...")
    result = fetch_and_format_events()
    print("\nFormatted for Discord:")
    print("=" * 50)
    print(result)
    print("=" * 50)
    print("Copy the text above and paste it into Discord!")
    
    # You can also use custom coordinates if needed:
    # result = fetch_and_format_events(x=-122.5, y=37.5)  # Different location