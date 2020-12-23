import requests
import json

# "To access FoodAI classification API, create a POST request w/ form data and image bytes"
# FoodAI only supports POST requests

def get_food_item_from_picture(query):
    # Get image from the query argument and format it to read an image from directory
    query_string = "img/" + query + ".jpg"

    # Read the current food item image as image bytes and store it into a dictionary
    with open(query_string, 'rb') as f:
        image_bytes = f.read()
        files = {'image_data': image_bytes}

    # Set up the API Key and URL for FoodAI Machine Learning API
    api_key = {'api_key': 'my_api_key'}
    url = 'https://api.foodai.org/v1/classify'

    # Send a POST request which returns a JSON object of the food results prediction
    food_item = requests.post(url, files = files, data = api_key).text

    # Transform the string into a dictionary object
    food_item = json.loads(food_item)

    # Get the value from the food_results key
    food_item_array = food_item["food_results"]

    # Get only the name of the strongest prediction match of the food item
    food_item_name = food_item_array[0][0]

    return food_item_name