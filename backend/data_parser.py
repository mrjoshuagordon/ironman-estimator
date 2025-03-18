data parser.py - tanner 

def parse_activities(activities) : #let me know if anything else needs to be parsed from the strava api. this is currently what it will parse. 
  parsed_data = [] 
  for activity in activities: 
      activity_data = {
        "name": activity.get("name"), 
        "distance": activity.get("distance"),
        "moving_time": activity.get("moving_time"), 
        "start_date": activity.get("start_date"),
        "type": activity.get("type"),
      }
    parsed_data.append(activity_data)
return parsed_data 
# notes that strava is limited in the requests and access tokens expire so tokens need to be refreshed. 
# token refresh logic/needs error handling capabilites aswell 
