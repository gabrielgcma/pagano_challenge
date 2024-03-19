from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import URL
import logging

import models
import struct

logging.basicConfig(level=logging.INFO)

docker_compose_db_url = URL.create(
    drivername='postgresql+psycopg2',
    username='postgres',
    password='postgres',
    host='db_opcua',
    database='opcua',
    port=5432
)

engine = create_engine(docker_compose_db_url)

Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

models.Base.metadata.create_all(engine)

def create_msg(msg: str):
    with Session() as session:
        db_msg = models.Message(value=float(msg))
        session.add(db_msg)
        session.commit()
        session.refresh(db_msg)
        logging.info(db_msg)
