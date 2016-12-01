import asyncio
from . import models
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.schema import CreateTable
import aiomysql.sa
import logging
from blaiog.exceptions import NotConnectedError
log = logging.getLogger('blaiog.db.engine')
log.addHandler(logging.NullHandler())


def get_db_engine(host, user, password, db):
    url = "mysql+pymysql://{user}:{password}@{host}/{db}"

    log.debug("Creating connection to {}".format(
        url.format(
            user=user, password="*********", host=host, db=db)))
    url = url.format(
        user=user, password=password, host=host, db=db)
    engine = create_engine(url)
    return engine


def get_db_session(engine):
    log.debug("initialize new db session")
    Session = sessionmaker(bind=engine)
    return Session()


def init_db(engine):
    log.debug("Creating tables")
    tables = models.metadata.tables.keys()
    conn = engine.connect()
    for table in ('permission','user','page','post'):
        Q = 'DROP TABLE IF EXISTS {}'.format(table)
        conn.execute(Q)
        conn.execute(CreateTable(models.metadata.tables[table]))
    conn.close()  
    #models.MetaData.create_all(engine)


class Engine(object):
    """
    The async DB Engine
    """

    def __init__(self, config):
        self._config = config
        self.engine = None

    @asyncio.coroutine
    def connect(self):
        self.engine = yield from aiomysql.sa.create_engine(
            user=self._config["db"]["user"],
            password=self._config["db"]["password"],
            host=self._config["db"]["host"],
            db=self._config["db"]["database"],
            echo=True,
            autocommit=True)
    

