from sqlalchemy import create_engine,inspect
from langchain_community.utilities import SQLDatabase
from pathlib import Path
import pandas as pd 

BASE_DIR=Path(__file__).parent

def execute_query_to_df(db_path: str, query:str):
    engine= create_engine(f"sqlite:///{db_path}")
    return pd.read_sql_query(query, engine)

def get_db_connection(db_path):
    engine=create_engine(f"sqlite:///{db_path}")
    db = SQLDatabase(engine,sample_rows_in_table_info=2)
    return db

def get_schema_summary(db_path):
    engine=create_engine(f"sqlite:///{db_path}")
    inspector=inspect(engine)
    lines=[]
    for table_name in inspector.get_table_names():
        lines.append(f"Table:{table_name}")
        columns=inspector.get_columns(table_name)

        for column in columns:
            lines.append(f" - {column['name']}({column['type']})")

    return "\n".join(lines)

if __name__=="__main__":
    DB_PATH=BASE_DIR/"Database"/"Sample"/"Chinook_Sqlite.sqlite"
    print(f"Looking for DB at: {DB_PATH}")
    if not DB_PATH.exists():
        print(f"File not found at: {DB_PATH}")
    else:
        print("File Found!")
        db=get_db_connection(DB_PATH)
        print(get_schema_summary(DB_PATH))