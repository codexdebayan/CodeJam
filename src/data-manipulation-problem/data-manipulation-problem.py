import mysql.connector
import json
import pandas as pd
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Print the current working directory
logging.info(f"Current working directory: {os.getcwd()}")

# Load JSON data
json_file_path = 'sample_data_for_assignment.json'
try:
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    logging.info("JSON data loaded successfully.")
except FileNotFoundError as e:
    logging.error(f"Error: {e}")
    exit()
except json.JSONDecodeError as e:
    logging.error(f"Error decoding JSON: {e}")
    exit()

# Database connection
try:
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="data_manupulation"
    )
    cursor = conn.cursor()
    logging.info("Database connection established.")
except mysql.connector.Error as err:
    logging.error(f"Error connecting to database: {err}")
    exit()

# Create table
try:
    create_table_query = """
    CREATE TABLE IF NOT EXISTS json_to_sql_table (
        {}
    );
    """.format(
        ', '.join([f"{col} VARCHAR(255)" for col in data['cols']])
    )
    cursor.execute(create_table_query)
    logging.info("Table created successfully or already exists.")
except mysql.connector.Error as err:
    logging.error(f"Error creating table: {err}")
    exit()

# Insert data into the table
try:
    insert_query = f"""
    INSERT INTO json_to_sql_table ({', '.join(data['cols'])})
    VALUES ({', '.join(['%s'] * len(data['cols']))});
    """
    cursor.executemany(insert_query, data['data'])
    conn.commit()
    logging.info("Data inserted into the table successfully.")
except mysql.connector.Error as err:
    logging.error(f"Error inserting data: {err}")
    exit()
finally:
    cursor.close()
    conn.close()
    logging.info("Database connection closed after insertion.")

# Reload data into DataFrame
try:
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="data_manupulation"
    )
    df = pd.read_sql('SELECT * FROM json_to_sql_table', conn)
    conn.close()
    logging.info("Data reloaded into DataFrame successfully.")
except mysql.connector.Error as err:
    logging.error(f"Error reloading data into DataFrame: {err}")
    exit()

# Process data

# Change email addresses to have the domain @gmail.com while keeping the original name
def update_email_domain(email):
    if pd.notna(email):
        local_part = email.split('@')[0]  # Extract the part before the '@'
        return f"{local_part}@gmail.com"
    return email

df['email'] = df['email'].apply(update_email_domain)

# Convert all postalZip values to integers
def convert_postal_zip(value):
    if pd.isna(value):
        return None
    if isinstance(value, int):
        return value
    # Remove non-numeric characters and convert to int
    numeric_value = ''.join(filter(str.isdigit, str(value)))
    return int(numeric_value) if numeric_value else None

df['postalZip'] = df['postalZip'].apply(convert_postal_zip)

# Process phone numbers
def process_phone(phone):
    if pd.isna(phone):
        return None
    phone = ''.join(filter(str.isdigit, str(phone)))
    result = []
    for i in range(0, len(phone) - 1, 2):
        num = int(phone[i:i + 2])
        if num < 65:
            result.append('O')
        else:
            result.append(chr(num))
    return ''.join(result)

df['coded_phone_number'] = df['phone'].apply(process_phone)
df.drop('phone', axis=1, inplace=True)

# Display the resulting DataFrame
logging.info("Final DataFrame after processing:")
print(df)
