from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import DATABASE_URL

engine = create_engine(DATABASE_URL, echo=True)  # echo=True выводит все SQL-запросы
Session = sessionmaker(bind=engine)
session = Session()
