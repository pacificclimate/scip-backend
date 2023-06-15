# sets up database for tests

import pytest
import testing.postgresql

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy_sqlschema import maintain_schema

# test data
from sample_data import WAT1, WAT2, WAT3, BAS1, make_region

# import salmon_occurrence
from salmon_occurrence import salmon_db, Region


# create database
@pytest.fixture()
def db_uri():
    with testing.postgresql.Postgresql() as pg:
        yield pg.url()


# initialize database with postgis and sqlalchemy
@pytest.fixture()
def db_engine(db_uri):
    engine = create_engine(db_uri)

    connection = engine.connect()
    connection.execute(text("CREATE EXTENSION postgis;"))
    connection.execute(text("CREATE SCHEMA IF NOT EXISTS salmon_geometry;"))
    connection.execute(text("GRANT CREATE ON SCHEMA salmon_geometry TO postgres"))
    connection.execute(text("SET search_path TO salmon_geometry, public;"))
    salmon_db.Base.metadata.create_all(bind=connection)
    connection.commit()
    connection.close()

    yield engine


# add some sample region data to database
@pytest.fixture()
def db_populated_session(db_engine):
    session = sessionmaker(bind=db_engine)()
    with maintain_schema("salmon_geometry, public", session):
        # add two square watersheds with some overlap
        session.add(make_region(WAT1))
        session.add(make_region(WAT2))

        # add a third watershed with no overlap with the other two
        session.add(make_region(WAT3))

        # add a basin that includes the first two watersheds, but not the third
        session.add(make_region(BAS1))

        # TODO: add salmon species, conservation units

    session.commit()
    yield session
    session.close()


# get a database session for testing, reset changes afterwards
@pytest.fixture()
def populated_db_session(db_populated_engine):
    session = sessionmaker(bind=db_populated_engine)
    yield session
    session.rollback()
    session.close()
