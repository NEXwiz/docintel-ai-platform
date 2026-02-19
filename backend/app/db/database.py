from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URI = os.getenv("DATABASE_URI")

engine = create_engine(           #engine - db,pool, driver(psycopg2)
    DATABASE_URI,
    pool_pre_ping = True          #pool of reliable connections, also helps to check if connection is still alive or not
)

SessionLocal = sessionmaker(      #session - conversation
    autocommit = False,
    autoflush = False,
    bind = engine                 #attaching the engine to the session so it knows how to access the db
)

Base = declarative_base()