"""
Run these commands:

LINUX Commands
export FLASK_APP=app.py
export FLASK_DEBUG=1
python3 -m flask run --host=0.0.0.0

WINDOWS Commands
set FLASK_APP=server.py
python -m flask run

WINDOWS RUN IN DEBUG MODE:
$env:FLASK_APP = "app"  
$env:FLASK_ENV = "development"
app.debug = True
"""

from time import sleep
from datetime import datetime
import requests

from flask import Flask, render_template, request

import rds_db as db
# from food_recognition_api import get_food_item_from_picture

# Global Variables (Mock Readings)
global food_reading_counter
global food_item_list
food_reading_counter = 0
food_item_list = ["Apple", "Egg", "Steak", "Orange", "Avocado"] 
food_name = "Apple"

app = Flask(__name__, static_url_path="/static")

@app.route("/")
def index():
    # (Not Debugging) Clear the FoodDiary database on application launch
    # FoodDiary database holds information on users and their food items consumed
    db.delete_all_rows_from_food_diary()

    # Get the current user's user_id and name
    name = "Dennis"
    curr_user_id = db.get_user_id("Dennis")

    # Retrieve weight reading in grams from the Arduino Digital Weight Scale (HX711 Load Cell)
    # through the ESP8266 Wi-Fi Module
    reading_in_grams = request.args.get("var") 

    # Display status of reading to console (debugging purposes)
    if reading_in_grams != None:
        print("Food reading is currently: " + str(reading_in_grams) + "g") 
    else: 
        print("Food reading is currently: " + "0g") 

    # Calculate macros for food item read if reading is not 0g
    if reading_in_grams != None:
        if float(reading_in_grams) > 0:

            # Using food_reading_counter to iterate through mock data array
            global food_reading_counter
            # Handling when array reaches end (may swap out for mod implementation)
            if food_reading_counter == len(food_item_list) - 1:
                food_reading_counter = 0
            else:
                food_reading_counter += 1
            
            # Get the food item name from the mock data array
            global food_item_list
            food_name = food_item_list[food_reading_counter]

            ### Machine Learning API Implementation (Future Iteration)
            # food_name = food_name.lower() + ".jpg"
            # food_name = get_food_item_from_picture(food_name)
            ### Get the food item name (have to hard code for now) from Machine Learning API (FoodAI)
            # get_food_item_from_picture("orange")

            # ~~~~~~~~~~~~~~ [ Read the food item stats from the database ] ~~~~~~~~~~~~~~~~~~~~ #

            # Calculate the ratio of the grams relative to previous 
            gram_ratio = float(reading_in_grams) / db.get_food_item_grams_facts(food_name)

            # Calculate the amount of calories based on the gram ratio
            calorie_content = gram_ratio * db.get_food_item_calorie_facts(food_name)   

            # Calculate protein content
            protein_content = float(gram_ratio * db.get_food_item_protein_facts(food_name))

            # Calculate carbohydrate content
            carbohydrate_content = float(gram_ratio * db.get_food_item_carbohydrate_facts(food_name))

            # Calculate fat content
            fat_content = float(gram_ratio * db.get_food_item_fat_facts(food_name))

            # Update FoodDiary / User stats
            db.insert_food_item_into_food_diary(food_name, calorie_content, protein_content, carbohydrate_content, fat_content, curr_user_id)
            # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

    # Define the nutrition goals based upon the user's input in the Database
    caloric_goal = db.get_current_user_caloric_goal(name)
    protein_goal = db.get_current_user_protein_goal(name)
    carbs_goal = db.get_current_user_carbohydrate_goal(name)
    fat_goal = db.get_current_user_fat_goal(name)
    
    # Get the nutrients that the user has already consumed
    curr_calories = db.get_calories_consumed_from_user(curr_user_id)
    curr_protein = db.get_protein_consumed_from_user(curr_user_id)
    curr_carbs = db.get_carbohydrate_consumed_from_user(curr_user_id)
    curr_fat = db.get_fat_consumed_from_user(curr_user_id)

    # List of food items user has consumed (currently hard-coded) for Graph #3
    food_items_consumed = db.get_food_consumed_for_user_from_food_diary_db(curr_user_id)

    ## Get food calories and time read (paired together) for line graph (Graph #1)
    calorie_consumption_list, calorie_accumulation_list, time_calories_read_list = db.get_calories_and_time_consumed_from_user(curr_user_id)
    
    # ~~~~~~~~~ [ Calculate remaining nutrition goals for card 4 ] ~~~~~~~~~~~~~~~~~~~~~ #
    calories_remaining = caloric_goal - curr_calories
    if calories_remaining < 0:
        calories_remaining = 0

    protein_remaining = protein_goal - curr_protein
    if protein_remaining < 0:
        protein_remaining = 0

    carbs_remaining = carbs_goal - curr_carbs
    if carbs_remaining < 0:
        carbs_remaining = 0

    fat_remaining = fat_goal - curr_fat
    if fat_remaining < 0:
        fat_remaining = 0
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

    # Display data and send context objects over to index.html
    return render_template("index.html", food_items_consumed = food_items_consumed, 
        curr_calories = curr_calories, curr_protein = curr_protein,
        curr_carbs = curr_carbs, curr_fat = curr_fat,
        calories_remaining = calories_remaining, protein_remaining = protein_remaining, 
        carbs_remaining = carbs_remaining, fat_remaining = fat_remaining,
        calorie_consumption_list = calorie_consumption_list, calorie_accumulation_list = calorie_accumulation_list,
        time_calories_read_list = time_calories_read_list,
        caloric_goal = caloric_goal, protein_goal = protein_goal,
        carbs_goal = carbs_goal, fat_goal = fat_goal)

if __name__ == "__main__":
    app.run(debug = True)