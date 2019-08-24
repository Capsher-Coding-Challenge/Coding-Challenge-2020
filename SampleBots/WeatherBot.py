# Loading environment variable
import os

# Discord library
import discord
from discord.ext import commands

# HTTP request library
import urllib.request

# JSON parsing
import json

# time tracking
import time

# For rounding in degree to direction calculation
import math

IS_CITY = 1
IS_ZIPCODE = 2
TEN_MINUTES = 600

# load token into shell environment variables
# ex. export DISCORD_BOT_TOKEN="<insert_token_here>"
discord_token = os.environ['DISCORD_BOT_TOKEN']
weather_api_token = os.environ['OPEN_WEATHER_TOKEN']

# Cache for location lookups
zipcode_lookup = {}
last_request_for_location = {}

# Tracking requests per minute
# API free tier maxes out @ 60 requests per minute
request_counter = 0
last_request_reset = time.time()

def location_type(location):
    if (location.isalpha()):
        return IS_CITY
    elif (location.isdigit()):
        return IS_ZIPCODE
    else:
        return 0

def check_location(location):
    this_location = location_type(location)
    location_info = {}
    if (this_location == IS_CITY and
            this_location in last_request_for_location.key):
        location_info = last_request_for_location[this_location]
    elif (this_location == IS_ZIPCODE and
            this_location in zipcode_lookup.keys()):
        city_name = zipcode_lookup[this_location]
        location_info = last_request_for_location[city_name]
    else:
        return ""

    if (location_info and time.time() - location_info.last_request < 600):
        return location_info.response

    return ""

def create_and_cache_response(json_string, zipcode=""):
    # Deserialize the JSON so we can use the data
    weather_info = json.loads(json_string)
    # translate meterological degrees to a compass direction
    wind_direction = get_cardinal_direction(weather_info.wind.direction)
    # Format string for posting in Discord chat
    output_string = ">>>Current Weather in {}: {}\n" \
                    "Description: {}"
                    "Temperature: {} Fahrenheit\n" \
                    "Humidity: {}%\n" \
                    "Wind: {} mph {}\n".format(weather_info.name, weather_info.weather[0].main,
                                        weather_info.weather[0].description,
                                        weather_info.main.temp,
                                        weather_info.main.humidty,
                                        weather_info.wind.speed, wind_direction)
    # Store zipcode -> city name
    if (zipcode != ""):
        zipcode_lookup[zipcode] = weather_info.name.upper()
    # Store output for a city
    last_request_for_location[weather_info.name.upper()] = output_string
    return output_string

# Got this from: https://www.campbellsci.com/blog/convert-wind-directions
def get_cardinal_direction(degrees):
    directions = ["N","NNE","NE","ENE","E","ESE","SE","SSE","S","SSW","SW","WSW","W","WNW","NW","NNW","N"]
    return directions[math.round((degrees % 360) / 22.5)]

# Bot code
bot = commands.Bot(command_prefix='weather.')

# TODO: add option for units
@bot.command()
async def current(ctx, location : string):
    # First, check our location cache
    location_response = check_location(location)
    if (location_response != ""):
        # We already had data for this location that we retrieved w/in
        # the last 10 minutes -- Don't need to send another request
        # API only updates current weather every 10 minutes
        await ctx.send(location_response)
        return

    # Next, check to see if we can send another request
    if (time.time() - last_request_reset < 60):
        if(request_counter >= 60):
            await ctx.send("This is awkward. I can't send another request just yet. Wait a minute or so.")
            return
        else:
            request_counter += 1
    else:
        # Reset the request timer and counter
        last_request_reset = time.time()
        request_counter = 1

    # OK, we can send a request to the API
    # Starting URL -- want to add on to the query based on input
    url = "https://api.openweathermap.org/data/2.5/weather?"
    if (location_type(location) == IS_CITY):
        # received alphabetic input
        # -- let's try a city query
        url += "q=" + location
    elif (location_type(location) == IS_ZIPCODE):
        # received numeric input
        # -- let's try a zipcode query
        url += "zip=" + location
    else:
        # received some mixed input. Ask the user to try again.
        await ctx.send("Uhhh. There seems to be a typo. Try again with a city name or zip code.")
        return

    # Send request to API endpoint
    # We're using https://openweathermap.org
    weather_json_string = urllib.request.urlopen(url + "&appid=" + weather_api_token + "&units=imperial").read()
    if (weather_json_string == ""):
        await ctx.send("Hmmmm.. I didn't get any response from the server. Try again in a couple minutes.")
    else:
        # We got a response!
        # Create a response string using the weather info
        formatted_weather_info = create_and_cache_response(weather_json_string, location)
        # Post the info in the channel!
        await ctx.send(formatted_weather_info)

# This token should be your bot token from discord
bot.run(discord_token)
