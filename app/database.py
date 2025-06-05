from sqlalchemy import create_engine
from sqlalchemy .ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import psycopg2, time
from psycopg2.extras import RealDictCursor
from .config import settings
SQLALCHEMY_DATABASE_URL = f'postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}'
#'postgresql://postgres:disha@localhost:5433/fastapi_database'
#'postgresql://<username>:<password>@<ip-address/hostname>/<database_name>'

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit = False , autoflush = False , bind = engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# while True:
 #       try:
 #           conn = psycopg2.connect(host = 'localhost', database = 'fastapi_database', user = 'postgres', \
  #                                  password = 'disha', cursor_factory = RealDictCursor, port = 5433)
   #         cursor = conn.cursor()
   #         print("DAtabase connection was successful!")
   #         break

   #     except Exception as error:
   #         print("Connecting to database failed")
   #         print("Error: ", error)
   #         time.sleep(2)