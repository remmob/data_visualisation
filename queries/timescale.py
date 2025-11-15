from sqlalchemy import create_engine
import pandas as pd

# example: postgresql://user:password@host:port/dbname
def get_engine():
    return create_engine("postgresql://homeassistant:Glasaal22!@192.168.22.208:5432/HomeAssistant")

def fetch_ltts(entity_id, start_time, end_time):
    query = """
        SELECT time, state
        FROM ltss
        WHERE entity_id = %s AND time BETWEEN %s AND %s
        ORDER BY time ASC
    """
    engine = get_engine()
    df = pd.read_sql(query, engine, params=(entity_id, start_time, end_time))
    return df
