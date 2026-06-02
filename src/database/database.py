from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import config

engine = create_engine(
    config.DATABASE_URL,
    echo=config.DATABASE_PRINT_SQL_QUERIES,
    pool_pre_put=True,
)
Session = sessionmaker(bind=engine)
session = Session()
