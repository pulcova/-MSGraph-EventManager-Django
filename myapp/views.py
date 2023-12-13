from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.dateparse import parse_datetime
from myapp.auth_helper import get_sign_in_flow, get_token_from_code, store_user, remove_user_and_token, get_new_access_token
from myapp.graph_helper import *
from .models import Event
import json
import os
from django.utils import timezone
import pytz
from datetime import datetime


def home(request):
    """
    Handle the main page of the application.
    
    - Initialize context with user and error details.
    - Check and retrieve access token.
    - Fetch and save events from Microsoft Graph API.
    - Filter events based on request parameters.
    - Return the rendered HTML page with events and filters.
    """
    context = initialize_context(request)

    # Load the token data from the JSON file
    if os.path.exists('access_token.json'):
        with open('access_token.json', 'r') as f:
            token_data = json.load(f)
    else:
        token_data = {}

    # Check if the access token exists
    token = token_data.get('access_token')
    if not token:
        # If the access token doesn't exist or is expired, try to get a new one
        token = get_new_access_token(request)
        if not token:
            # Handle the case where we couldn't get a new token
            # Redirect the user to the sign-in page
            request.session['flash_error'] = 'Your session has expired. Please sign in again.'
            return HttpResponseRedirect(reverse('signin'))

    headers = {
        'Authorization': 'Bearer ' + token,
    }

    # List all events
    response = requests.get(
        graph_url + '/me/events',
        headers=headers,
    )

    # Write all events to a JSON file
    events = response.json().get('value', [])
    with open('events.json', 'w') as f:
        json.dump(events, f, indent=4)

    # Save the events to the database
    for event in events:
        # Parse the start and end times as naive datetime objects
        start_time = parse_datetime(event['start']['dateTime'])
        end_time = parse_datetime(event['end']['dateTime'])
        
        # Get the location, attendees, and description
        location = event['location']['displayName']
        attendees = json.dumps(event['attendees'])  # Convert the attendees list to a JSON string
        organizer = json.dumps(event['organizer'])  # Convert the organizer dict to a JSON string
        description = event['bodyPreview']

        # Get the additional fields
        is_cancelled = event['isCancelled']
        is_online_meeting = event['isOnlineMeeting']
        online_meeting_provider = event['onlineMeetingProvider']
        web_link = event['webLink']

        # Check if the event already exists in the database
        if not Event.objects.filter(event_id=event['id'], subject=event['subject'], start_time=start_time, end_time=end_time).exists():
            # Create a new Event object
            Event.objects.create(
                event_id=event['id'],
                subject=event['subject'],
                start_time=start_time,
                end_time=end_time,
                location=location,                        
                attendees=attendees,
                organizer=organizer,
                description=description,
                is_cancelled=is_cancelled,
                is_online_meeting=is_online_meeting,
                online_meeting_provider=online_meeting_provider,
                web_link=web_link,
            )

    # Start with all events
    events = Event.objects.all().order_by('start_time')

    # Get the date filter from the GET parameters
    filter = request.GET.get('filter')
    now = timezone.now()

    # Apply the date filter if provided
    if filter == 'today':
        events = events.filter(start_time__date=now.date())
    elif filter == 'past':
        events = events.filter(end_time__lt=now)
    elif filter == 'upcoming':
        events = events.filter(start_time__gt=now)

    # Get the location filter from the GET parameters
    location_filter = request.GET.get('locationFilter')

    # Apply the location filter if provided
    if location_filter and location_filter != 'all':
        events = events.filter(location=location_filter)

    # Create a new list to store the modified events
    modified_events = []
    for event in events:
        # Parse attendees JSON into list of dictionaries
        attendees_data = json.loads(event.attendees)
        organizer_data = json.loads(event.organizer)
        
        # Extract name and email addresses from attendees data
        attendees_info = [f"{attendee['emailAddress']['name']} - {attendee['emailAddress']['address']}" for attendee in attendees_data]
        organizer_info = f"{organizer_data['emailAddress']['name']} - {organizer_data['emailAddress']['address']}"
        
        # Modify the event's attendees attribute in-place
        event.attendees = ', '.join(attendees_info)
        event.organizer = organizer_info

        # Add the modified event to the new list
        modified_events.append(event)

    context['locationFilter'] = location_filter
    context['filter'] = filter
    context['events'] = modified_events

    return render(request, 'myapp/home.html', context)




def initialize_context(request):
    """
    Initialize the context for views.
    
    - Check for flash error messages.
    - Retrieve or set user authentication status.
    - Return the context dictionary.
    """
    context = {}
    error = request.session.pop('flash_error', None)
    if error is not None:
        context['errors'] = []
        context['errors'].append(error)
    # Check for user in the session
    context['user'] = request.session.get('user', {'is_authenticated': False})
    return context

def sign_in(request):
    """
    Initiate the user sign-in process.
    
    - Get the sign-in flow from the authentication helper.
    - Save the flow to the session.
    - Redirect to Azure sign-in page.
    """
    # Get the sign-in flow
    flow = get_sign_in_flow()
    # Save the expected flow so we can use it in the callback
    try:
        request.session['auth_flow'] = flow
    except Exception as e:
        print(e)
    # Redirect to the Azure sign-in page
    return HttpResponseRedirect(flow['auth_uri'])

def sign_out(request):
    """
    Handle user sign-out process.
    
    - Remove user and token from session.
    - Delete access_token.json if exists.
    - Redirect to home page.
    """
    # Clear out the user and token
    remove_user_and_token(request)

    # Delete the access_token.json file
    if os.path.exists('access_token.json'):
        os.remove('access_token.json')

    return HttpResponseRedirect(reverse('home'))

def callback(request):
    """
    Handle the callback from Azure sign-in.
    
    - Retrieve token using code from request.
    - Save token to JSON file.
    - Get and store user profile in session.
    - Redirect to home page.
    """
    # Make the token request
    result = get_token_from_code(request)

    # Save the token to a JSON file
    with open('access_token.json', 'w') as f:
        json.dump(result, f)

    # Get the user's profile
    user = get_user(result['access_token'])

    # Store user
    store_user(request, user)

    return HttpResponseRedirect(reverse('home'))

