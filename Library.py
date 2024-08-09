import datetime
import os.path

from datetime import datetime, timezone, timedelta
from dateutil import parser
from dateutil.parser import isoparse, ParserError
from dateutil.relativedelta import relativedelta
from tzlocal import get_localzone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from AST import CalEvent
from difflib import *

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar"]
timeZone = get_localzone()

def authorization():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "src/backend/credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return creds

def getService():
    creds = authorization()
    return build("calendar", "v3", credentials=creds)

def searchEvents(service, numEvents = None, startTime = None, endTime = None):
    if startTime == None:
        startTime = datetime.now(timezone.utc).isoformat()
    else:
        startParsed = parser.parse(startTime)
        startTime = startParsed.replace(tzinfo=timeZone).isoformat()
    if endTime == None:
     startParsed = parser.parse(startTime)
     endTime = (startParsed + relativedelta(years=1)).isoformat()
    else:
        endParsed = parser.parse(endTime)
        endTime = endParsed.replace(tzinfo=timeZone).isoformat()
    events_result = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=startTime,
            timeMax=endTime,
            maxResults=numEvents,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    events = events_result.get("items", [])
    return events
    
def listEvents(service, numEvents, startTime, endTime):
    events = searchEvents(service, numEvents, startTime, endTime)
    if not events:
        print("No upcoming events found.")
        return
    
    returnString = ""
    # Prints the start and name of the next numEvents events
    for event in events:
        summary = event["summary"]
        start = event["start"]["dateTime"]
        end = event["end"]["dateTime"]
        print(summary, start, end)
        returnString += summary + " " + start + " " + end + " "

    return returnString

def find(service, name = None, start = None, end = None):
    events = searchEvents(service, None, start, end)

    # No future events
    if not events:
        print("No upcoming events found.")
        return None

    event_names = []
    # Searching with event name and start
    if(name != None):
        for event in events:
            event_name = event['summary'].lower()
            
            # check if event name (and start time if provided) match
            if(event['summary'].lower() == name.lower()):
                # if start is provided, check that the even start matches
                if (start != None) and (event['start'].get('dateTime') == start):
                    return event
                return event

            else:
                # add event name to list of all event names to check if event name has any near matches
                event_names.append(event_name)
                
        # get list of close matches
        close_matches = get_close_matches(name, event_names)
        if close_matches != []:
            # TODO: implement a way for the user to pick which close match is the one they want (for now just pick the first)
            return find(service, name = close_matches[0])

    # Searching with just start
    if(start != None):
        for event in events:
            if(event['start'].get('dateTime') == start):
                return event
    
    return None

def create(service, summary, startTime, endTime, location, description, zone):
    if zone != None:
            timeZone = zone
    else:
            timeZone = get_localzone()
    if(endTime == None):
        startParsed = parser.parse(startTime)
        endTime = (startParsed + timedelta(hours = 1)).isoformat()

    event = {
        'summary': summary,
        'location': location,
        'description': description,
        'start': {
            'dateTime': startTime,
            'timeZone': str(timeZone),
        },
        'end': {
            'dateTime': endTime,
            'timeZone': str(timeZone),
        },
    }
    event = service.events().insert(calendarId='primary', body=event).execute()
    return event

def delete(service, name, start):
    if(name != None and start != None):
        event = find(service, name, start)
        if(event != None):
            service.events().delete(calendarId='primary', eventId=event.get('id')).execute()
            return

    if(name != None):
        event = find(service, name)
        if(event != None):
            service.events().delete(calendarId='primary', eventId=event.get('id')).execute()
            return

    if(start != None):
        event = find(service, None, start)
        if(event != None):
            service.events().delete(calendarId='primary', eventId=event.get('id')).execute()
         
def update(service, summary, newSummary, start, newStart, end, newEnd, back, forward, newLocation, newDescription, zone):
    if(summary != None):
        if zone != None:
            timeZone = zone
        else:
            timeZone = get_localzone()
        event = find(service, summary, start, end)
        oldStart = None
        if (event != None):
            if newSummary != None:
                event['summary'] = newSummary
            if back != None:
                shift = eval(back)
                oldstart = parser.parse(event['start']['dateTime'])
                oldend = parser.parse(event['end']['dateTime'])
                event['start'] = {
                    'dateTime': (oldstart-shift).isoformat(),
                    'timeZone': str(timeZone)
                }
                event['end'] = {
                    'dateTime': (oldend-shift).isoformat(),
                    'timeZone': str(timeZone)
                }
                if forward != None:
                    shift = eval(forward)
                    oldstart = parser.parse(event['start']['dateTime'])
                    oldend = parser.parse(event['end']['dateTime'])
                    event['start'] = {
                        'dateTime': (oldstart+shift).isoformat(),
                        'timeZone': str(timeZone)
                    }
                    event['end'] = {
                        'dateTime': (oldend-shift).isoformat(),
                        'timeZone': str(timeZone)
                    }
            if newStart != None:
                oldStart = parser.parse(event['start']['dateTime'])
                event['start'] = {
                    'dateTime': newStart,
                    'timeZone': str(timeZone)
                }
                if newEnd == None:
                    diference = parser.parse(event['end']['dateTime']) - oldStart
                    newEnd = parser.parse(newStart) + diference
            if newEnd != None:
                event['end'] = {
                    'dateTime': newEnd.isoformat(),
                    'timeZone': str(timeZone)
                }
            if newLocation != None:
                event['location'] = newLocation
            if newDescription != None:
                event['description'] = newDescription
            event = service.events().update(calendarId='primary', eventId=event['id'], body=event).execute()
            return event
            
        else:
            return "Error: Event not found"
    else:
        return "Error: Missing event name"

def is_valid_tzinfo(identifier):
    try:
        ZoneInfo(identifier)
        return True
    except ZoneInfoNotFoundError:
        return False

def is_iso8601(date_string):
    try:
        isoparse(date_string)
        return True
    except (ValueError, ParserError):
        return False

def checkInit(summary, start, end, location, description, time_zone):
    error = ""
    # checking for summmary
    if isinstance(summary, str) == False:
        error += "Event must have a summary as a string\n"
    # checking for start time
    if isinstance(start, str) == False:
        error += "Event must have a start time as a string\n"
    # checking format of start time
    elif is_iso8601(start) == False:
        error += "Event must have a start time in ISO 8601 format\n"
    # checking format of end time
    if isinstance(end, str) == True:
        if is_iso8601(end) == False:
            error += "End time must be in ISO 8601 format\n"
    # making sure end is not a type other than string or None
    elif end != None:
        error += "End time must be a string\n"
    # checking format of location
    if isinstance(location, str) == False and location != None:
        error += "Location must be a string\n"
    # checking format of description
    if isinstance(description, str) == False and description != None:
        error += "Description must be a string\n"
    # checking format of time zone
    if isinstance(time_zone, str) == True:
        if is_valid_tzinfo(time_zone) == False:
            error += "The time zone must be a tzinfo identifier\n"
    # making sure time zone is not a type other than string or none
    elif time_zone != None:
        error += "The time zone must be a string\n"
    return error

def checkGet(summary, start, end):
    error = ""
    # checking for summary or start
    if summary == None and start == None:
        error += "Must include a summary and/or a start time to get an event\n"
    # making sure summary is not a type other than string or None
    if isinstance(summary, str) == False and summary != None:
        error += "Summary must be a string\n"
    # checking format of start time
    if isinstance(start, str) == True:
        if is_iso8601(start) == False:
            error += "Start time must be in ISO 8601 format\n"
    # making sure that start is not a type other than string or none
    elif start != None:
        error += "The start time must be a string\n"
    # checking format of end time
    if isinstance(end, str) == True:
        if is_iso8601(end) == False:
            error += "End time must be in ISO 8601 format\n"
    # making sure end time is not a type other than string or None
    elif end != None:
        error += "End time must be a string\n"
    return error

def checkList(number, start, end):
    error = ""
    # checking for number or start
    if number == None and start == None:
        error += "Must include a number and/or a start time to get an event\n"
    # making sure number is not a type other than int or None
    if isinstance(number, int) == False and number != None:
        error += "Number of events must be a string\n"
     # checking format of start time
    if isinstance(start, str) == True:
        if is_iso8601(start) == False:
            error += "Start time must be in ISO 8601 format\n"
    # making sure that start is not a type other than string or none
    elif start != None:
        error += "The start time must be a string\n"
    # checking format of end time
    if isinstance(end, str) == True:
        if is_iso8601(end) == False:
            error += "End time must be in ISO 8601 format\n"
    # making sure end time is not a type other than string or None
    elif end != None:
        error += "End time must be a string\n"
    return error

def checkUpdate(summary, start, end, back, forward, location, description, time_zone):
    error = ""
    if summary == None and start == None and end == None and back == None and forward == None and location == None and description == None and time_zone == None:
        error += "No updates being made\n"
    # making sure summary is not a type other than string or None
    if isinstance(summary, str) == False and summary != None:
        error += "Summary must be a string\n"
    # checking format of start time
    if isinstance(start, str) == True:
        if is_iso8601(start) == False:
            error += "Start time must be in ISO 8601 format\n"
    # making sure that start is not a type other than string or none
    elif start != None:
        error += "The start time must be a string\n"
    # checking format of end time
    if isinstance(end, str) == True:
        if is_iso8601(end) == False:
            error += "End time must be in ISO 8601 format\n"
    # making sure end time is not a type other than string or None
    elif end != None:
        error += "End time must be a string\n"
    # checking format of back shift
    if isinstance(back, str) == True:
        shift = eval(back)
        if isinstance(shift, timedelta) == False:
            error += "The back shift must be a timedelta object\n"
    # making sure back shift is not a type other than string or none
    elif back != None:
        error += "The back shift must be a string\n"
        # checking format of forward shift
    if isinstance(forward, str) == True:
        shift = eval(forward)
        if isinstance(shift, timedelta) == False:
            error += "The forward shift must be a timedelta object\n"
    # making sure forward shift is not a type other than string or none
    elif forward != None:
        error += "The forward shift must be a string\n"
    # making sure location is not a type other than string or None
    if isinstance(location, str) == False and location != None:
        error += "Location must be a string\n"
    # making sure description is not a type other than string or None
    if isinstance(description, str) == False and description != None:
        error += "Description must be a string\n"
    # checking format of time zone
    if isinstance(time_zone, str) == True:
        if is_valid_tzinfo(time_zone) == False:
            error += "The time zone must be a tzinfo identifier\n"
    # making sure time zone is not a type other than string or none
    elif time_zone != None:
        error += "The time zone must be a string\n"
    return error
