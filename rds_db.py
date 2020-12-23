import json
from decimal import Decimal
from time import sleep

import pymysql

# Connection to database (sensitive data removed)
conn = pymysql.connect(
        host = "rds.amazonaws.com", # not real endpoint link
        port = 1111, # not real port
        user = "admin", # not real admin login
        password = "my_password", # not real password
        db = "food_items", # real database table name
        )


# ~~~~~~~~~~[ Create: INSERT FOOD ITEM]~~~~~~~~~~~~~ #
def insert_food_item_into_food_diary(food_name, calories, protein, carbohydrate, fat, user_id):
    cur = conn.cursor()
    cur.execute("SET time_zone = 'US/Pacific'")
    cur.execute("INSERT INTO FoodDiary (food_name, calories, protein, carbohydrate, fat, user_id, dt) VALUES (%s, %s, %s, %s, %s, %s, NOW())", 
        (food_name, calories, protein, carbohydrate, fat, user_id))
    conn.commit()
    
# ~~~~~~~~~[ Quickly Add Food Items for Debugging Purposes ]~~~~~~~~~~~~~~~~~~ #
def debug_populate_food_diary():
    cur = conn.cursor()
    food_name = "Apple"
    calories = 95
    protein = 1
    carbohydrate = 25
    fat = 0
    user_id = 1
    cur.execute("SET time_zone = 'US/Pacific'")
    cur.execute("INSERT INTO FoodDiary (food_name, calories, protein, carbohydrate, fat, user_id, dt) VALUES (%s, %s, %s, %s, %s, %s, NOW())",
        (food_name, calories, protein, carbohydrate, fat, user_id))
    conn.commit()

# ~~~~~~~~~~[ Update: CLEAR FOOD ITEMS FoodDiary DB]~~~~~~~~~~~~~ #
def delete_all_rows_from_food_diary():
    cur = conn.cursor()
    cur.execute("DELETE FROM FoodDiary")
    conn.commit()

# ~~~~~~~~~~[ Read: GET FOOD ITEMS]~~~~~~~~~~~~~ #
def get_food_items_from_food_diary():
    cur = conn.cursor()
    cur.execute("SELECT * FROM FoodDiary")
    food_items = cur.fetchall()
    return food_items

# ~~~~~~~~~~[ Get all food items and stats for a particular user]~~~~~~~~~~~~~ #
def get_food_stats_for_user_from_food_diary(user_id):
    cur = conn.cursor()
    cur.execute("SELECT * FROM FoodDiary WHERE user_id = %s", user_id)
    food_items = cur.fetchall()
    return food_items

# ~~~~~~~~~~[ GET USER STATS]~~~~~~~~~~~~~ #
def get_current_user(name):
    cur = conn.cursor()
    cur.execute("SELECT * FROM Users WHERE name = %s", name)
    current_user = cur.fetchall()
    return current_user

def get_current_user_caloric_goal(name):
    current_user = get_current_user(name)
    user_caloric_goal = current_user[0][2]
    user_caloric_goal = float(user_caloric_goal)
    return user_caloric_goal

def get_current_user_protein_goal(name):
    current_user = get_current_user(name)
    user_protein_goal = current_user[0][3]
    user_protein_goal = float(user_protein_goal)
    return user_protein_goal

def get_current_user_carbohydrate_goal(name):
    current_user = get_current_user(name)
    user_carbohydrate_goal = current_user[0][4]
    user_carbohydrate_goal = float(user_carbohydrate_goal)
    return user_carbohydrate_goal

def get_current_user_fat_goal(name):
    current_user = get_current_user(name)
    user_fat_goal = current_user[0][5]
    user_fat_goal = float(user_fat_goal)
    return user_fat_goal

# Import JSON Formatted User List into MySQL DB
def add_userlist_from_txt_file():
    with open("users_goals.txt") as fp:
        while True:
            curr_line = fp.readline()
            if curr_line == "":
                break
            curr_line = json.loads(curr_line)

            user_id = curr_line["user_id"]
            name = curr_line["name"]
            calories_goal = curr_line["calories_goal"]
            protein_goal = curr_line["protein_goal"]
            carbohydrate_goal = curr_line["carbohydrate_goal"]
            fat_goal = curr_line["fat_goal"]

            cur = conn.cursor()
            cur.execute("INSERT IGNORE INTO Users (user_id, name, calories_goal, protein_goal, carbohydrate_goal, fat_goal) VALUES (%s, %s, %s, %s, %s, %s)", 
                (user_id, name, calories_goal, protein_goal, carbohydrate_goal, fat_goal))
            conn.commit()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~[ Getting User Nutrients Consumed from MySQL DB] ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
def get_user_id(name):
    cur = conn.cursor()
    cur.execute("SELECT user_id FROM Users WHERE name = %s", (name))
    user_id = cur.fetchone()
    user_id = int(user_id[0])
    return user_id

# Remove the 'Decimal' wording
def remove_decimal_fix(var):
    var_fixed = []
    for row in var:
        var_fixed.append(list(map(str, list(row))))
        
    # Take the calories from the array of arrays (since we're just getting the #)
    var_fixed = var_fixed[0][0]
    if var != None:
        try:
            var_fixed = float(var_fixed)
        except:
            var_fixed = 0
    else:
        print("remove_decimal_fix bug")
    return var_fixed

def get_calories_consumed_from_user(user_id):
    cur = conn.cursor()
    cur.execute("SELECT SUM(calories) FROM FoodDiary, Users WHERE FoodDiary.user_id = Users.user_id AND FoodDiary.user_id = %s", (user_id))
    calories = cur.fetchall()
    calories = remove_decimal_fix(calories)    
    return calories

def get_protein_consumed_from_user(user_id):
    cur = conn.cursor()
    cur.execute("SELECT SUM(protein) FROM FoodDiary, Users WHERE FoodDiary.user_id = Users.user_id AND FoodDiary.user_id = %s", (user_id))
    protein = cur.fetchall()
    protein = remove_decimal_fix(protein)
    return protein

def get_carbohydrate_consumed_from_user(user_id):
    cur = conn.cursor()
    cur.execute("SELECT SUM(carbohydrate) FROM FoodDiary, Users WHERE FoodDiary.user_id = Users.user_id AND FoodDiary.user_id = %s", (user_id))
    carbohydrate = cur.fetchall()    
    carbohydrate = remove_decimal_fix(carbohydrate)
    return carbohydrate

def get_fat_consumed_from_user(user_id):
    cur = conn.cursor()
    cur.execute("SELECT SUM(fat) FROM FoodDiary, Users WHERE FoodDiary.user_id = Users.user_id AND FoodDiary.user_id = %s", (user_id))
    fat = cur.fetchall()
    fat = remove_decimal_fix(fat)
    return fat

def get_food_consumed_for_user_from_food_diary_db(user_id):
    cur = conn.cursor()
    cur.execute("SELECT * FROM FoodDiary, Users WHERE FoodDiary.user_id = Users.user_id AND FoodDiary.user_id = %s", (user_id))
    food_items_for_user = cur.fetchall()
    food_list = []
    for row in food_items_for_user:
        food_list.append(list(map(str, list(row))))
    result = []
    for item in food_list:
        result.append(item[0])
    return result
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~[Get Stats from FoodItem DB for each food item]~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
# ~~~~~[ Return Grams for Certain Food Item]~~~~~~ #
def get_food_item_grams_facts(food_name):
    cur = conn.cursor()
    cur.execute("SELECT grams FROM FoodItems WHERE food_name = %s", (food_name))
    food_item = cur.fetchone()
    food_item_calories = food_item[0]
    return float(food_item_calories)

# ~~~~~[ Return Calories for Certain Food Item]~~~~~~ #
def get_food_item_calorie_facts(food_name):
    cur = conn.cursor()
    cur.execute("SELECT calories FROM FoodItems WHERE food_name = %s", (food_name))
    food_item = cur.fetchone()
    food_item_calories = food_item[0]
    return float(food_item_calories)

# ~~~~~[ Return Protein Content for Certain Food Item]~~~~~~ #
def get_food_item_protein_facts(food_name):
    cur = conn.cursor()
    cur.execute("SELECT protein FROM FoodItems WHERE food_name = %s", (food_name))
    food_item = cur.fetchone()
    food_item_protein = food_item[0]
    return float(food_item_protein)

# ~~~~~[ Return Carbohydrate Content for Certain Food Item]~~~~~~ #
def get_food_item_carbohydrate_facts(food_name):
    cur = conn.cursor()
    cur.execute("SELECT carbohydrate FROM FoodItems WHERE food_name = %s", (food_name))
    food_item = cur.fetchone()
    food_item_carbohydrate = food_item[0]
    return float(food_item_carbohydrate)

# ~~~~~[ Return Fat Content for Certain Food Item]~~~~~~ #
def get_food_item_fat_facts(food_name):
    cur = conn.cursor()
    cur.execute('SELECT fat FROM FoodItems WHERE food_name = %s', (food_name))
    food_item = cur.fetchone()
    food_item_fat = food_item[0]
    return float(food_item_fat)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

# (Unused) Might use for a future iteration
def get_time_from_dt(dt):
    time_formatted = dt.strftime("%H:%M:%S")
    hours = time_formatted[0:2]
    minutes = time_formatted[3:5]
    seconds = time_formatted[6:9]

    result = hours + minutes 
    print(result)
    return result

def get_calories_and_time_consumed_from_user(user_id):

    cur = conn.cursor()
    cur.execute("SELECT calories, dt FROM FoodDiary, Users WHERE FoodDiary.user_id = Users.user_id AND FoodDiary.user_id = %s", (user_id))
    calories_dt_obj = cur.fetchall()

    # Remove the "Decimal" part
    calorie_timeread_list = []
    for row in calories_dt_obj:
        calorie_timeread_list.append(list(map(str, list(row))))


    for food_item_reading in calorie_timeread_list:
        food_item_reading[1] = food_item_reading[1][11:]
        hour = int(food_item_reading[1][0:2])
        minute = food_item_reading[1][3:5]
        second = food_item_reading[1][6:9]

        if hour > 12:
            hour -= 12
            hour = str(hour)
            am_pm = "PM"
        else:
            if hour < 10:
                hour = food_item_reading[1][1:2]
            am_pm = "AM"
        my_formatted_time = "%s:%s:%s %s" % (hour, minute, second, am_pm)
        food_item_reading[1] = my_formatted_time

    # Initialize arrays with 0 to better see the line chart (Graph 1)
    calorie_consumption_list = [0]
    calorie_accumulation_list = [0]
    time_calories_read_list = [0]

    accumulation_calories = 0
    for i in range(len(calorie_timeread_list)):
        calorie_consumption_list.append(calorie_timeread_list[i][0])

        accumulation_calories += float(calorie_timeread_list[i][0])
        calorie_accumulation_list.append(str(accumulation_calories))

        time_calories_read_list.append(calorie_timeread_list[i][1])

    return calorie_consumption_list, calorie_accumulation_list, time_calories_read_list
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #