import requests
from db import get_conn

def create_insert_from_json(table_name, json_data):
    # Escape reserved keywords (like "limit") by wrapping them in double quotes
    columns = ', '.join([f'"{key}"' if key.lower() in ['limit'] else key for key in json_data.keys()])
    
    # Process values to handle booleans, strings, and numbers properly
    def format_value(value):
        if isinstance(value, str):
            # Escape single quotes in strings (e.g., O'Reilly becomes O\'Reilly)
            return f"'{value.replace("'", "''")}'"
        elif isinstance(value, bool):
            return 'TRUE' if value else 'FALSE'
        else:
            return str(value)
    
    # Generate formatted values
    values = ', '.join(map(format_value, json_data.values()))

    # Construct the SQL INSERT statement
    insert_query = f"INSERT INTO {table_name} ({columns}) VALUES ({values});"
    return insert_query
def insert_all():
    response = requests.get('https://prices.runescape.wiki/api/v1/osrs/mapping')
    res =  response.json()  # Assuming the API returns JSON data
    print(res)
    table_name = 'scores'
    conn = get_conn()
    cursor = conn.cursor()
    for json_data in res:
        
        insert_statement = create_insert_from_json(table_name, json_data)
        cursor.execute(insert_statement)
    conn.commit()

    conn.close()



insert_all()


