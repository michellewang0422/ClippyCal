import Library

# A dictionary to store locally created/found events
dictionary = dict()

# Class for a singular calendar event
class CalEvent:

    # Initializer for a CalEvent object with optional parameters (params are checked in methods)
    def __init__(self, summary=None, start=None, end=None, location=None, description=None, time_zone=None):
        self.summary = summary
        self.start = start
        self.end = end
        self.location = location
        self.description = description
        self.time_zone = time_zone
        self.service = Library.getService()
        dictionary[(summary, start)] = self

    # Find a specified event
    # NOTE: THIS MUST BE CALLED ON ITS OWN (wrapper function for get)
    def find(summary=None, start=None, end=None):
        event = CalEvent.get(summary, start, end)
        if event is None:
            returnString = f"Event not found."
        else:
            returnString = f"Event found: {event.summary} {event.start} {event.end}"

        return returnString

    # Get and return a specified event
    # NOTE: THIS CANNOT BE CALLED ON ITS OWN (must be called with an additional command, i.e. update(), delete())
    def get(summary=None, start=None, end=None):
        error = Library.checkGet(summary, start, end)
        if error == "":
            # find the event in the Calendar
            event = Library.find(Library.getService(), summary, start, end)
            if event is None:
                print("Event not found.")
                return None
 
            summary = event['summary']
            start = event['start']['dateTime']

            # check if event is found in dictionary (searching by name and start time)
            if (summary, start) in dictionary:
                return dictionary[(summary, start)]
            # make a new dictionary event
            else:
                newDictEvent = CalEvent(summary=summary,start=start,end=event['end']['dateTime'])
                return newDictEvent

        return error

    # Create/schedule an event
    def create(self):
        returnString = Library.checkInit(self.summary, self.start, self.end, self.location, self.description, self.time_zone)
        if returnString == "":
            Library.create(self.service, self.summary, self.start, self.end, self.location, self.description, self.time_zone)
            returnString = f"Event created: {self.summary}"

        return returnString

    # Update a specified event with given new information
    def update(self, new_summary=None, new_start=None, new_end=None, shift_back=None, shift_forward=None, new_location=None, new_description=None, new_time_zone=None):
        returnString = Library.checkUpdate(new_summary, new_start, new_end, shift_back, shift_forward, new_location, new_description, new_time_zone)
        if returnString == "":
            Library.update(self.service, self.summary, new_summary, self.start, new_start, self.end, new_end, shift_back, shift_forward, new_location, new_description, new_time_zone)
            if new_summary != None:
                self.summary = new_summary
            if new_start != None:
                self.start = new_start
            if new_end != None:
                self.end = new_end
            if new_location != None:
                self.location = new_location
            if new_description != None:
                self.description = new_description
            if new_time_zone != None:
                self.time_zone = new_time_zone
            returnString = f"Event updated: {self.summary} {self.start} {self.end}"
        
        return returnString

    # List events given number of events and/or time range
    def listEvents(number=None, start=None, end=None):
        returnString = Library.checkList(number, start, end)
        if returnString == "":
            return "List of events: " + Library.listEvents(Library.getService(), number, start, end)

        return returnString

    # Delete a specified event
    def delete(self):
        Library.delete(self.service, self.summary, self.start)
        del dictionary[(self.summary, self.start)]
        returnString = f"Event deleted: {self.summary}"

        return returnString

    # Print out information for a specified CalEvent
    def prettyprint(self):
        return f"Event: {self.summary} starting at {self.start}"