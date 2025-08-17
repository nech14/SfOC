from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.database.models.models import User, Coefs, Filters, Nights, Paths

DATABASE_URL = "mysql+pymysql://root@192.168.0.19:3306/api_test"

engine = create_engine(DATABASE_URL, echo=True)  # echo=True выводит все SQL-запросы
Session = sessionmaker(bind=engine)
session = Session()

# users = session.query(Paths).all()
#
# for u in users:
#     print(f"{u.__dict__}")