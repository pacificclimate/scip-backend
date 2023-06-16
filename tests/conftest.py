# sets up database for tests

import pytest
import testing.postgresql

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy_sqlschema import maintain_schema

# test data and formatting functions
from sample_data import WAT1, WAT2, WAT3, BAS1, make_region
from sample_data import CHUM, PNKO, PNKE, make_taxon
from sample_data import CUC1, CUC2, CUPO, CUPE, make_cu, make_population

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


# add some sample data to database
@pytest.fixture()
def db_populated_session(db_engine):
    session = sessionmaker(bind=db_engine)()
    with maintain_schema("salmon_geometry, public", session):
        # add regions
        session.add(make_region(WAT1))
        session.add(make_region(WAT2))
        session.add(make_region(WAT3))
        session.add(make_region(BAS1))

        # add salmon taxons
        chum = make_taxon(CHUM)
        pink_even = make_taxon(PNKE)
        pink_odd = make_taxon(PNKO)

        session.add(chum)
        session.add(pink_even)
        session.add(pink_odd)

        # add conservation units
        cuc1 = make_cu(CUC1)
        cuc2 = make_cu(CUC2)
        cupo = make_cu(CUPO)
        cupe = make_cu(CUPE)

        session.add(cuc1)
        session.add(cuc2)
        session.add(cupo)
        session.add(cupe)

        # commit conservation units and taxons so we can assign them to populations.
        session.commit()

        # add populations, each of which is a link between a taxon
        # and a conservation unit
        # note that for verification purposes, the populations created
        # here must match the verification objects in sample_data.py
        session.add(make_population(chum, cuc1))
        session.add(make_population(chum, cuc2))
        session.add(make_population(pink_odd, cupo))
        session.add(make_population(pink_even, cupe))

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
