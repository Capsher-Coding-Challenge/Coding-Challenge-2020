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

# Constants
IS_CITY = 1
IS_ZIPCODE = 2
TEN_MINUTES = 600

# load token into shell environment variables
# ex. export DISCORD_BOT_TOKEN="<insert_token_here>"
discord_token = os.environ['DISCORD_BOT_TOKEN']
weather_api_token = os.environ['OPEN_WEATHER_TOKEN']

class WeatherLookup:
    def __init__(self):
        # Cache for location lookups
        self.zipcode_lookup = {}
        self.last_request_for_location = {}
        # Tracking requests per minute
        # API free tier maxes out @ 60 requests per minute
        self.request_counter = 0
        self.last_request_reset = time.time()

    def location_type(self, location):
        if (location.isalpha()):
            return IS_CITY
        elif (location.isdigit()):
            return IS_ZIPCODE
        else:
            return 0

    def check_location(self, location):
        this_location = self.location_type(location)
        location_info = {}

        if (this_location == IS_CITY and
                location.upper() in self.last_request_for_location):
            location = location.upper()
            location_info = self.last_request_for_location[location.upper()]
        elif (this_location == IS_ZIPCODE and
                location in self.zipcode_lookup):
            city_name = self.zipcode_lookup[location]
            location_info = self.last_request_for_location[city_name]
        else:
            print("Did not find any cached data for: {}".format(location))
            return ""

        if (location_info and time.time() - location_info['last_request'] < 600):
            return location_info['response']

        return ""

    def create_and_cache_response(self, json_string, zipcode=""):
        # Deserialize the JSON so we can use the data
        weather_info = json.loads(json_string)
        # translate meterological degrees to a compass direction
        wind_direction = self.get_cardinal_direction(weather_info['wind']['deg'])
        # Format string for posting in Discord chat
        output_string = ">>> Current Weather in {}: {}\n" \
                        "Description: {}\n" \
                        "Temperature: {} Fahrenheit\n" \
                        "Humidity: {}%\n" \
                        "Wind: {} mph {}\n".format(weather_info['name'], weather_info['weather'][0]['main'],
                                            weather_info['weather'][0]['description'],
                                            weather_info['main']['temp'],
                                            weather_info['main']['humidity'],
                                            weather_info['wind']['speed'], wind_direction)
        # Store zipcode -> city name
        if (zipcode != ""):
            self.zipcode_lookup[zipcode] = weather_info['name'].upper()
        # Store output for a city
        self.last_request_for_location[weather_info['name'].upper()] = {'last_request' : time.time(), 'response' : output_string }
        return output_string

    # Got this from: https://www.campbellsci.com/blog/convert-wind-directions
    def get_cardinal_direction(self, degrees):
        directions = ["N","NNE","NE","ENE","E","ESE","SE","SSE","S","SSW","SW","WSW","W","WNW","NW","NNW","N"]
        return directions[round((degrees % 360) / 22.5)]

    def retrieve_weather_data(self, location):
        # Check our location cache to see if we already have data for this location
        location_response = self.check_location(location)
        if (location_response != ""):
            # We already had data for this location that we retrieved w/in
            # the last 10 minutes -- Don't need to send another request
            # API only updates current weather every 10 minutes
            print ("Found cached data for: {}".format(location))
            return location_response

        # Next, check to see if we can send another request
        if (time.time() - self.last_request_reset < 60):
            if(self.request_counter >= 60):
                return "This is awkward. I can't send another request just yet. Wait a minute or so."
            else:
                self.request_counter = self.request_counter + 1
        else:
            # Reset the request timer and counter
            self.last_request_reset = time.time()
            self.request_counter = 1

        # OK, we can send a request to the API
        # Starting URL -- want to add on to the query based on input
        url = "https://api.openweathermap.org/data/2.5/weather?"
        if (self.location_type(location) == IS_CITY):
            # received alphabetic input
            # -- let's try a city query
            url += "q=" + location
        elif (self.location_type(location) == IS_ZIPCODE):
            # received numeric input
            # -- let's try a zipcode query
            url += "zip=" + location
        else:
            # received some mixed input. Ask the user to try again.
            return "Uhhh. There seems to be a typo. Try again with a city name or zip code."

        # Send request to API endpoint
        # We're using https://openweathermap.org
        print("Sending request to Open Weather for: {}".format(location))
        weather_json_string = urllib.request.urlopen(url + "&appid=" + weather_api_token + "&units=imperial").read()
        if (weather_json_string == ""):
            print("Failed to get response from the Open Weather Server")
            return "Hmmmm.. I didn't get any response from the server. Try again in a couple minutes."
        else:
            # We got a response!
            # Create a response string using the weather info
            print("Successfully got response from server. Generating response")
            formatted_weather_info = self.create_and_cache_response(weather_json_string, location)
            return formatted_weather_info

# Bot code
bot = commands.Bot(command_prefix='weather.')

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('-------------')

# TODO: add option for units
@bot.command(name="current")
async def current(ctx, location):
    if (location == ""):
        await ctx.send("Please enter a location. Usage: weather.current <zip_code or city_name>")
    else:
        print("Weather lookup request for: {}".format(location))
        await ctx.send(wb.retrieve_weather_data(location))

# This token should be your bot token from discord
global wb
wb = WeatherLookup()
bot.run(discord_token)
