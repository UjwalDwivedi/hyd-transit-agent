import requests
import os
from dotenv import load_dotenv
from ddgs import DDGS


current_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(current_dir, '.env')

load_dotenv(dotenv_path=env_path)

def get_current_weather(city: str) -> str:

    api_key = os.getenv("OPENWEATHER_API_KEY")

    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": api_key,
        "units": "metric"
    }
    
    try:
        response = requests.get(base_url, params=params)
        
        if response.status_code == 401:
            return "Error: Unauthorized (401)"
        elif response.status_code == 404:
            return f"Error: City '{city}' not found."
            
        response.raise_for_status() 
        data = response.json()
        
        weather_desc = data["weather"][0]["description"]
        temp = data["main"]["temp"]
        visibility_meters = data.get("visibility", "Unknown")
        
        if isinstance(visibility_meters, int):
            vis_string = f"{visibility_meters / 1000} km"
        else:
            vis_string = visibility_meters

        return f"Conditions: {weather_desc.capitalize()}, Temperature: {temp}°C, Visibility: {vis_string}"
        
    except requests.exceptions.RequestException as e:
        return f"Failed to fetch weather data: {e}"
    


def get_hyderabad_traffic(location: str) -> str:

    api_key = os.getenv("TOMTOM_API_KEY")

    coordinates = {
        "hitech city": "17.4474,78.3762",
        "gachibowli": "17.4401,78.3489",
        "madhapur": "17.4483,78.3915",
        "secunderabad": "17.4399,78.4983",
        "ameerpet": "17.4375,78.4482",
        "kukatpally": "17.4841,78.4011"  
    }
    
    search_loc = location.lower().strip()
    # Default to center of Hyderabad if the zone isn't in the dictionary
    point = coordinates.get(search_loc, "17.3850,78.4867") 

    # TomTom Traffic Flow API Endpoint
    base_url = "https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/10/json"
    params = {
        "point": point,
        "key": api_key
    }
    
    try:
        response = requests.get(base_url, params=params)
        
        if response.status_code == 403:
            return "Error: Unauthorized (403)"
            
        response.raise_for_status()
        data = response.json()

        flow_data = data.get("flowSegmentData")
        
        if not flow_data:
            error_msg = data.get("detailedError", {}).get("message", "Unknown API error structure")
            return f"TomTom API responded, but traffic telemetry was unavailable. Message: {error_msg}"
        

        current_speed = flow_data.get("currentSpeed", 0)
        free_flow_speed = flow_data.get("freeFlowSpeed", 1)

        congestion = round((1 - (current_speed / free_flow_speed)) * 100)   
        congestion = max(0, min(100, congestion)) 
        
        return (
            f"Live Traffic for '{location.title()}': "
            f"Current Speed is {current_speed} km/h (Normal free-flow is {free_flow_speed} km/h). "
            f"Estimated congestion level: {congestion}%."
        )
        
    except requests.exceptions.RequestException as e:
        return f" Failed to fetch live traffic data due to network error: {e}"
    



from ddgs import DDGS

def get_real_events(location: str) -> str:

    try:
        query = f"local events festivals schedule {location} Hyderabad 2026"
        
        results = DDGS().text(query, max_results=3)
        
        if not results:
            return f"No notable public events found for {location} in 2026."
            
        events_list = []
        for i, res in enumerate(results, 1):
            events_list.append(f"{i}. {res['title']} - {res.get('body', 'No description')}")
            
        return "\n".join(events_list)
        
    except Exception as e:
        return f"Event scraping failed: {e}"