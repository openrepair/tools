#!/usr/bin python3

import os
from funcs import *
import sqlalchemy as db
import sqlalchemy.dialects.mysql as my


def dbords():

    constr = "mysql+mysqldb://{ORDS_DB_USER}:{ORDS_DB_PWD}@{ORDS_DB_HOST}/{ORDS_DB_DATABASE}".format(
        **os.environ)

    try:
        engine = db.create_engine(constr, echo=True, pool_recycle=600)
        conn = engine.connect()
        meta = db.MetaData()
        atable = db.Table('OpenRepairData_v0.3_aggregate_202309', meta,
        db.Column("id", my.VARCHAR(255, collation='utf8mb4_unicode_ci'), primary_key=False,  nullable=True, default="None"),
        db.Column("data_provider", my.VARCHAR(255, collation='utf8mb4_unicode_ci'), primary_key=False,  nullable=True, default="None"),
        db.Column("country", my.VARCHAR(255, collation='utf8mb4_unicode_ci'), primary_key=False,  nullable=True, default="None"),
        db.Column("partner_product_category", my.VARCHAR(255, collation='utf8mb4_unicode_ci'), primary_key=False,  nullable=True, default="None"),
        db.Column("product_category", my.VARCHAR(255, collation='utf8mb4_unicode_ci'), primary_key=False,  nullable=True, default="None"),
        db.Column("product_category_id", my.VARCHAR(255, collation='utf8mb4_unicode_ci'), primary_key=False,  nullable=True, default="None"),
        db.Column("brand", my.VARCHAR(255, collation='utf8mb4_unicode_ci'), primary_key=False,  nullable=True, default="None"),
        db.Column("year_of_manufacture", my.VARCHAR(255, collation='utf8mb4_unicode_ci'), primary_key=False,  nullable=True, default="None"),
        db.Column("product_age", my.VARCHAR(255, collation='utf8mb4_unicode_ci'), primary_key=False,  nullable=True, default="None"),
        db.Column("repair_status", my.VARCHAR(255, collation='utf8mb4_unicode_ci'), primary_key=False,  nullable=True, default="None"),
        db.Column("repair_barrier_if_end_of_life", my.VARCHAR(255, collation='utf8mb4_unicode_ci'), primary_key=False,  nullable=True, default="None"),
        db.Column("group_identifier", my.VARCHAR(255, collation='utf8mb4_unicode_ci'), primary_key=False,  nullable=True, default="None"),
        db.Column("event_date", my.VARCHAR(255, collation='utf8mb4_unicode_ci'), primary_key=False,  nullable=True, default="None"),
        db.Column("problem", my.TEXT(collation='utf8mb4_unicode_ci'), primary_key=False,  nullable=True, default="None"),
        )
        db.Index("id", atable.c.id, unique=False)
        db.Index("data_provider", atable.c.data_provider, unique=False)
        db.Index("repair_barrier_if_end_of_life", atable.c.repair_barrier_if_end_of_life, unique=False)
        db.Index("brand", atable.c.brand, unique=False)
        db.Index("group_identifier", atable.c.group_identifier, unique=False)
        db.Index("event_date", atable.c.event_date, unique=False)
        db.Index("partner_product_category", atable.c.partner_product_category, unique=False)
        db.Index("product_age", atable.c.product_age, unique=False)
        db.Index("country", atable.c.country, unique=False)
        db.Index("repair_status", atable.c.repair_status, unique=False)
        db.Index("year_of_manufacture", atable.c.year_of_manufacture, unique=False)
        db.Index("product_category", atable.c.product_category, unique=False)
        db.Index("product_category_id", atable.c.product_category_id, unique=False)

        atable.drop(engine, checkfirst=True)
        atable.create(engine)

    except Exception as error:
        print("Exception: {}".format(error))

if __name__ == "__main__":

    logger = logfuncs.init_logger(__file__)
    dbords()