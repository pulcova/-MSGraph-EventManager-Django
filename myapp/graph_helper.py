import requests
import json

graph_url = 'https://graph.microsoft.com/v1.0'

def get_user(token):
    # Send GET to /me
    '''
        get_user(token): This function retrieves details of the currently authenticated user.
            It sends a GET request to the /me endpoint of the Graph API.
            The function requires an access token which is passed in the Authorization header.
            The params dictionary specifies which user attributes to retrieve: displayName, mail, mailboxSettings, and userPrincipalName.
            The function returns the user's details in JSON format.
    '''
    user = requests.get('{0}/me'.format(graph_url),
    headers={'Authorization': 'Bearer {0}'.format(token)},
    params={
'$select':'displayName,mail,mailboxSettings,userPrincipalName'})
    return user.json()

def get_events(token):
    # Send GET to /me/events
    '''
        get_events(token): This function retrieves events from the authenticated user's calendar.
            It sends a GET request to the /me/events endpoint of the Graph API.
            Similar to the get_user function, an access token is required and passed in the Authorization header.
        The params dictionary specifies:
            Which event attributes to retrieve: subject, start, and end.
            How to order the results: by the start date and time in descending order.
            The function returns the events in JSON format.
    '''
    events = requests.get(
        '{0}/me/events'.format(graph_url),
        headers={'Authorization': 'Bearer {0}'.format(token)},
        params={
            '$select': 'subject,start,end',
            '$orderby': 'start/dateTime DESC'
        }
    )
    return events.json()
