import os

from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class PGC(Base):
    __tablename__ = "pgc"
    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String(200))


#PostgreSQLとの接続用
db_uri = os.environ['DATABASE_URL']
if db_uri.startswith("postgres://"):
    db_uri = db_uri.replace("postgres://", "postgresql://", 1)
engine = create_engine(db_uri)
session_factory = sessionmaker(bind=engine)
session = session_factory()

Base.metadata.create_all(bind=engine)


def add_pgc(link):
    pgc_data = PGC(url = link)
    session.add(pgc_data)
    session.commit()

def is_exist(link):
    result = session.query(PGC.url).filter(PGC.url == link).all()
    if result != []:
        return True
    else:
        return False
