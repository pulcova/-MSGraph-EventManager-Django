import yaml
import msal
import os
import json


# Load the oauth_settings.yml file located in your app DIR
# Get the directory of the current file
current_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the full path to the oauth_settings.yml file
settings_file = os.path.join(current_dir, '..', 'oauth_settings.yml')

# Open the file
with open(settings_file, 'r') as stream:
    settings = yaml.safe_load(stream)

def load_cache(request):
  # Check for a token cache in the session
  cache = msal.SerializableTokenCache()
  if request.session.get('token_cache'):
    cache.deserialize(request.session['token_cache'])
  return cache

def save_cache(request, cache):
  # If cache has changed, persist back to session
  if cache.has_state_changed:
    request.session['token_cache'] = cache.serialize()

def get_msal_app(cache=None):
  # Initialize the MSAL confidential client
  auth_app = msal.ConfidentialClientApplication(
    settings['app_id'],
    authority=settings['authority'],
    client_credential=settings['app_secret'],
    token_cache=cache)
  return auth_app

# Method to generate a sign-in flow
def get_sign_in_flow():
  '''The get_sign_in_flow function initiates the authorization code flow, which is a part of the    
    OAuth2.0 protocol. This is the first step in the process where a user logs in and grants permissions to your app.
  '''
  auth_app = get_msal_app()
  return auth_app.initiate_auth_code_flow(
    settings['scopes'],
    redirect_uri=settings['redirect'])

# Method to exchange auth code for access token
def get_token_from_code(request):
  '''
    The get_token_from_code function exchanges the authorization code (received after a user logs in) for an access token.
  '''
  cache = load_cache(request)
  auth_app = get_msal_app(cache)

  # Get the flow saved in session
  flow = request.session.pop('auth_flow', {})
  result = auth_app.acquire_token_by_auth_code_flow(flow, request.GET)
  save_cache(request, cache)

  return result


def store_user(request, user):
  '''
    The store_user function saves user details in the session after they've logged in. The remove_user_and_token function removes the user and token details from the session, effectively logging the user out.
  '''
  try:
    request.session['user'] = {
      'is_authenticated': True,
      'name': user['displayName'],
      'email': user['mail'] if (user['mail'] != None) else user['userPrincipalName'],
      'timeZone': user['mailboxSettings']['timeZone'] if (user['mailboxSettings']['timeZone'] != None) else 'UTC'
    }
  except Exception as e:
    print(e)

def get_token(request):
  '''
    The get_token function retrieves the access token from the cache if it exists. If the token has expired, it will try to refresh it.
  '''
  cache = load_cache(request)
  auth_app = get_msal_app(cache)

  accounts = auth_app.get_accounts()
  if accounts:
    result = auth_app.acquire_token_silent(
      settings['scopes'],
      account=accounts[0])
    save_cache(request, cache)

    return result['access_token']

def remove_user_and_token(request):
  if 'token_cache' in request.session:
    del request.session['token_cache']

  if 'user' in request.session:
    del request.session['user']

def get_new_access_token(request):
    '''
    The get_new_access_token function retrieves a new access token using the refresh token.The get_new_access_token function is designed to get a new access token using a refresh token. It does the following:
      - It first checks if the access_token.json file exists. If it does, it loads the token data from this file.
      - It then retrieves the refresh token from the loaded data.
      - If a refresh token is found, it uses the MSAL library to get a new access token using this refresh token.
      - If a new access token is successfully retrieved, it saves this new token (and any other data, like a new refresh token) back to the access_token.json file.
      
      Finally, it returns the new access token. If any step fails, it returns None, indicating that it couldn't get a new token.

    '''
    # Load the token data from the JSON file
    if os.path.exists('access_token.json'):
        with open('access_token.json', 'r') as f:
            token_data = json.load(f)
    else:
        token_data = {}

    refresh_token = token_data.get('refresh_token')
    if not refresh_token:
        return None

    # Use the refresh token to get a new access token
    auth_app = get_msal_app()
    result = auth_app.acquire_token_by_refresh_token(refresh_token, settings['scopes'])
    if 'access_token' in result:
        # Save the new access token and refresh token to the JSON file
        with open('access_token.json', 'w') as f:
            json.dump(result, f)
        return result['access_token']
    else:
        return None

