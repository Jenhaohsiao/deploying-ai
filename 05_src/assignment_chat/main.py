import sys
from pathlib import Path

# Add 05_src directory to Python path to allow execution from any directory
sys.path.insert(0, str(Path(__file__).parent.parent))

from openai import OpenAI
from dotenv import load_dotenv
from prompts import return_instructions_root
import json
import requests
from utils.logger import get_logger
import os

_logs = get_logger(__name__)

src_dir = Path(__file__).parent.parent
load_dotenv(src_dir / ".env")
load_dotenv(src_dir / ".secrets")

client = OpenAI()

open_ai_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# Define tools for the OpenAI API
tools = [
    {
        "type": "function",
        "name": "get_coordinates",
        "description": "Converts a city or location name to geographical coordinates (latitude and longitude) using the Nominatim geocoding service.",
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The city or location name to geocode (e.g., 'Tokyo', 'New York', 'Paris')",
                }
            },
            "required": ["location"],
            "additionalProperties": False
        },
    },
    {
        "type": "function",
        "name": "get_weather",
        "description": "Retrieves weather forecast data for a given location using coordinates. Returns detailed weather information including temperature, cloudiness, and precipitation.",
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {
                "lat": {
                    "type": "number",
                    "description": "Latitude of the location (range: -90 to 90)",
                },
                "lon": {
                    "type": "number",
                    "description": "Longitude of the location (range: -180 to 180)",
                }
            },
            "required": ["lat", "lon"],
            "additionalProperties": False
        },
    },
]


def get_coordinates(location: str) -> dict:
    """
    Uses Nominatim API to convert a location name to coordinates.
    
    Args:
        location: City or location name (in any language)
        
    Returns:
        Dictionary containing latitude, longitude, and display name
    """
    _logs.info(f"Getting coordinates for location: {location}")
    
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": location,
        "format": "json",
        "limit": 1,
        "accept-language": "en"  # Request English results
    }
    headers = {
        "User-Agent": "WeatherChatBot/1.0"  # Nominatim requires a User-Agent
    }
    
    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        
        if not data:
            return {
                "error": f"Location '{location}' not found. The location name may be misspelled or doesn't exist. Please verify the spelling.",
                "location_input": location,
                "found": False
            }
        
        result = {
            "lat": float(data[0]["lat"]),
            "lon": float(data[0]["lon"]),
            "display_name": data[0].get("display_name", location),
            "location_input": location,
            "found": True
        }
        
        _logs.info(f"Found coordinates: {result}")
        return result
        
    except requests.exceptions.RequestException as e:
        _logs.error(f"Error calling Nominatim API: {e}")
        return {
            "error": f"Failed to geocode location: {str(e)}",
            "location_input": location,
            "found": False
        }


def get_weather(lat: float, lon: float) -> dict:
    """
    Uses 7Timer! API to get weather forecast for given coordinates.
    
    Args:
        lat: Latitude
        lon: Longitude
        
    Returns:
        Dictionary containing weather forecast data
    """
    _logs.info(f"Getting weather for coordinates: lat={lat}, lon={lon}")
    
    url = "http://www.7timer.info/bin/api.pl"
    params = {
        "lon": lon,
        "lat": lat,
        "product": "civillight",  # Simplified civil forecast
        "output": "json"
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        # Fix malformed JSON from 7Timer API
        # Sometimes the API returns incomplete values like "min" : without a value
        raw_text = response.text
        
        # Fix incomplete numeric values by replacing `: \n` or `: ,` with `: null`
        import re
        # Pattern: "key" : <whitespace or comma or newline>
        fixed_text = re.sub(r':\s*([,\n}])', r': null\1', raw_text)
        
        try:
            data = json.loads(fixed_text)
        except json.JSONDecodeError as je:
            _logs.error(f"JSON decode error even after fixing: {je}")
            _logs.debug(f"Fixed text sample: {fixed_text[:500]}")
            return {
                "error": "Unable to parse weather data from API"
            }
        
        # Parse the 7Timer response
        # The dataseries contains forecast for different time periods
        if "dataseries" in data and len(data["dataseries"]) > 0:
            forecasts = data["dataseries"][:3]  # Get next 3 time periods
            
            weather_info = {
                "location": f"lat={lat}, lon={lon}",
                "forecasts": []
            }
            
            for forecast in forecasts:
                # Keep original weather codes - let OpenAI interpret and translate them
                weather_code = forecast.get("weather", "unknown")
                
                # Extract temperature data safely
                temp2m = forecast.get("temp2m", {})
                if isinstance(temp2m, dict):
                    temp_max = temp2m.get("max")
                    temp_min = temp2m.get("min")
                else:
                    temp_max = None
                    temp_min = None
                
                forecast_item = {
                    "date": forecast.get("date"),  # Format: YYYYMMDD
                    "timepoint": forecast.get("timepoint"),  # Hours from init
                    "weather_code": weather_code,  # Original code like 'pcloudy', 'lightrain', etc.
                    "temp_max": temp_max,  # Maximum temperature (Celsius)
                    "temp_min": temp_min,  # Minimum temperature (Celsius)
                    "cloudcover": forecast.get("cloudcover", 0),  # 1-9 scale
                    "wind10m_max": forecast.get("wind10m_max", 0),  # Wind speed
                }
                
                weather_info["forecasts"].append(forecast_item)
            
            _logs.info(f"Weather data retrieved: {weather_info}")
            return weather_info
        else:
            return {
                "error": "No weather data available for this location"
            }
            
    except requests.exceptions.RequestException as e:
        _logs.error(f"Error calling 7Timer API: {e}")
        return {
            "error": f"Failed to retrieve weather data: {str(e)}"
        }
    except Exception as e:
        _logs.error(f"Unexpected error in get_weather: {e}")
        return {
            "error": f"Unexpected error: {str(e)}"
        }


def sanitize_history(history: list[dict]) -> list[dict]:
    """Remove tool-related fields from history for cleaner conversation context"""
    clean_history = []
    for msg in history:
        clean_history.append({
            "role": msg.get("role"),
            "content": msg.get("content")
        })
    return clean_history


def assignment_chat(message: str, history: list[dict] = []) -> str:
    """
    Main chat function that handles weather queries using OpenAI API with function calling.
    
    Args:
        message: User's input message
        history: Conversation history
        
    Returns:
        Assistant's response text
    """
    _logs.info(f'User message: {message}')
    
    instructions = return_instructions_root()
    
    user_msg = {
        "role": "user",
        "content": message
    }
    
    conversation_input = sanitize_history(history) + [user_msg]
    
    # First API call
    response = client.responses.create(
        model=open_ai_model,
        instructions=instructions,
        input=conversation_input,
        tools=tools,
    )
    
    conversation_input += response.output
    
    # Handle function calls
    max_iterations = 5  # Prevent infinite loops
    iteration = 0
    
    while iteration < max_iterations:
        function_called = False
        
        for item in response.output:
            if item.type == "function_call":
                function_called = True
                _logs.info(f'Function call: {item.name}')
                
                args = json.loads(item.arguments)
                _logs.info(f'Function call args: {args}')
                
                # Call the appropriate function
                if item.name == "get_coordinates":
                    result = get_coordinates(**args)
                elif item.name == "get_weather":
                    result = get_weather(**args)
                else:
                    result = {"error": f"Unknown function: {item.name}"}
                
                # Add function result to conversation
                func_call_output = {
                    "type": "function_call_output",
                    "call_id": item.call_id,
                    "output": json.dumps(result)
                }
                
                _logs.debug(f"Function call output: {func_call_output}")
                conversation_input.append(func_call_output)
                
                # Make another API call with the function result
                response = client.responses.create(
                    model=open_ai_model,
                    instructions=instructions,
                    tools=tools,
                    input=conversation_input
                )
                
                conversation_input += response.output
                break  # Process one function call at a time
        
        if not function_called:
            # No more function calls, we're done
            break
        
        iteration += 1
    
    if iteration >= max_iterations:
        _logs.warning("Max iterations reached in function calling loop")
    
    return response.output_text

