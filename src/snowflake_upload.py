import pandas as pd
import snowflake.connector
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# --------------------------------------------------
# 1. Load cleaned CSV
# --------------------------------------------------

file_path = "data/rainfall_cleaned.csv"

df = pd.read_csv(file_path)

print("CSV loaded successfully!")
print("Rows:", len(df))
print("Columns:", len(df.columns))

# --------------------------------------------------
# 2. Convert Date
# --------------------------------------------------

df["Date"] = pd.to_datetime(df["Date"]).dt.date
# Replace pandas NaN/NA with None
df = df.astype(object).where(pd.notna(df), None)

# --------------------------------------------------
# 3. Connect to Snowflake
# --------------------------------------------------

conn = snowflake.connector.connect(
    user=os.getenv("SNOWFLAKE_USER"),
    password=os.getenv("SNOWFLAKE_PASSWORD"),
    account=os.getenv("SNOWFLAKE_ACCOUNT"),
    warehouse="ATMOSYNC_WH",
    database="ATMOSYNC_DB",
    schema="WEATHER_ANALYTICS"
)

cursor = conn.cursor()

print("Connected to Snowflake!")

# --------------------------------------------------
# 4. Insert data
# --------------------------------------------------

insert_sql = """
INSERT INTO WEATHER_DATA (
    DATE,
    YEAR,
    MONTH,
    DAY_TYPE,
    CITY,
    REGION,
    LATITUDE,
    LONGITUDE,
    ELEVATION_M,
    SEASON,
    RAINFALL_MM,
    RAINED,
    RAIN_INTENSITY,
    ALERT_LEVEL,
    WEATHER_CONDITION,
    MAX_TEMP_C,
    MIN_TEMP_C,
    AVG_TEMP_C,
    HUMIDITY_PCT,
    WIND_SPEED_KMPH,
    WIND_DIRECTION_DEG,
    PRESSURE_HPA,
    CLOUD_COVER_PCT,
    SUNSHINE_HOURS,
    EVAPORATION_MM
)
VALUES (
    %s, %s, %s, %s, %s,
    %s, %s, %s, %s, %s,
    %s, %s, %s, %s, %s,
    %s, %s, %s, %s, %s,
    %s, %s, %s, %s, %s
)
"""

data = [tuple(row) for row in df.values]

cursor.executemany(insert_sql, data)

conn.commit()

print("Data uploaded successfully!")

# --------------------------------------------------
# 5. Verify row count
# --------------------------------------------------

cursor.execute("SELECT COUNT(*) FROM WEATHER_DATA")

count = cursor.fetchone()[0]

print("Rows in Snowflake WEATHER_DATA:", count)

cursor.close()
conn.close()

print("Snowflake connection closed.")