from fastapi import FastAPI
from db import get_conn
import threading
import time
import requests
import psycopg2
import json
from deepdiff import DeepDiff
from db import get_conn
# Global variable to store cached data (in-memory)
cached_data = None
from queue import Queue
data_queue = Queue()

from datetime import datetime, timezone
from fastapi import FastAPI, BackgroundTasks
from sse_starlette.sse import EventSourceResponse
from fastapi.middleware.cors import CORSMiddleware

import asyncio
# Create a FastAPI instance
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins, change to specific domains if needed
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)
from queue import Queue

# Define a dynamic endpoint
@app.get("/dashboard")
def read_item():
    conn = get_conn()
    cur = conn.cursor()
    try:
        
        q = """select "id" , "examine" , "lowalch" , "limit" , "value" , "highalch" , "icon" , "name" , "high" , "low" , "highTime" , "lowTime" from "scores"  """
        cur.execute(q)
        res = cur.fetchall()
        keys = ["id" , "examine" , "lowalch" , "limit" , "value" , "highalch" , "icon" , "name" , "high" , "low" , "highTime" , "lowTime" ]
        ret = []
        for d in res : 
            ret.append(dict(zip(keys, d)))
        
        return {"data" : ret}
    except Exception as e:
        return { "message": "Internal Server Error"}
    finally:
        cur.close()
        conn.close()


@app.on_event("startup")
async def start_background_task():
    # Run the periodic scan in a separate thread
    threading.Thread(target=periodic_api_call, daemon=True, name="periodic" ).start()

# SSE endpoint to stream events to the browser
@app.get("/events")
async def sse():
    async def event_generator():
        while True:
            # Check if there's any new data to send
            data = data_queue.get()
            if data:
                 # Get the next data entry
                # print(found_data , "data")
                  # Block until data is available
                data_queue.task_done()
                yield f"data: {data}\n\n"
            await asyncio.sleep(1)  # Check for new data every 1 second

    return EventSourceResponse(event_generator())




# Function to make an API call
def fetch_api_data():
    url = 'https://prices.runescape.wiki/api/v1/osrs/latest'
    response = requests.get(url)
    return response.json()  # Assuming the API returns JSON data

# Function to check the difference between cached and new data
def get_data_difference(new_data):
    global cached_data
    if cached_data is None:
        return new_data  # If no cached data, return the new data as the difference
    
    # Compare cached_data with new_data using DeepDiff
    diff = DeepDiff(cached_data, new_data, verbose_level=2)  # verbose_level gives more detailed output
    return diff

# Function to check if the data has changed and update DB
def check_and_update_db(new_data):
    global cached_data
    global found_data
    
    # Get the difference between the cached data and the new data
    data_diff = get_data_difference(new_data)
    
    if data_diff:  # If there is a difference, update DB and cache
        # Insert new data into DB (store it as a JSON string)
        # conn = get_db_connection()
        # cursor = conn.cursor()
        
        # cursor.execute(
        #     "INSERT INTO api_data (data_column) VALUES (%s)", 
        #     (json.dumps(new_data),)
        # )
        # conn.commit()
        
        # cursor.close()
        # conn.close()

        # Update cached data with new data
        changed_keys = []
        if 'values_changed' in data_diff:
            for path in data_diff['values_changed']:
                # Path format: "root['data']['219']['highTime']"
                new_val = data_diff['values_changed'][path]['new_value']
                parts = path.replace("root['", "").replace("']['", "/").replace("']", "").split('/')
                
                # Extract the keys (219, 'highTime')
                key_list = [int(parts[1]), parts[2],new_val ]  # [219, 'highTime', 23242]
                changed_keys.append(key_list)
        if changed_keys:
            data_queue.put(changed_keys) 
            print("data found")
            update_dynamic_columns(changed_keys)
            changed_keys.clear()

        cached_data = new_data
        print("Data updated in DB and cache refreshed.")

    else:
        print("No change in data. Skipping update.")

# Periodic API call function
def periodic_api_call():
    while True:
        new_data = fetch_api_data()  # Fetch data from API
        check_and_update_db(new_data)  # Compare and update DB if changed
        time.sleep(5)  # Sleep for 60 seconds (adjust the interval as needed)
# periodic_api_call()
# Start the thread for periodic API calls
# thread = threading.Thread(target=periodic_api_call)
# thread.daemon = True  # Set daemon to True to allow the thread to exit when the program exits
# thread.start()


def update_dynamic_columns(data):
    conn = get_conn()
    cursor = conn.cursor()
    try:
        for row in data:
            # Prepare the UPDATE query for each row
            if row[1] in ['highTime', 'lowTime']:
                c_val = datetime.fromtimestamp(row[2], tz=timezone.utc)
                update_sql = f"""UPDATE scores SET "{row[1]}" = '{c_val}' WHERE id = {row[0]} """

            else:
                c_val = row[2]
                update_sql = f"""UPDATE scores SET {row[1]} = {c_val} WHERE id = {row[0]} """

            # Execute the update statement with the new timestamp and record ID
            cursor.execute(update_sql)
            
            # Optionally, commit after each update if you want each to be atomic
            # conn.commit()  # Uncomment this line if you want each update to be committed individually

        # Commit all updates after completing the loop (for batch commit)
        conn.commit()
        # Execute the dynamic update query

        # Commit the changes to the database
        print("Rows updated successfully.")
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()  # Rollback if there's an error
    finally:
        # Close the cursor and the connection
        cursor.close()
        conn.close()