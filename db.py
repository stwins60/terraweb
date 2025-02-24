import mysql.connector as mysql
from mysql.connector import Error
import os
import psycopg2
from dotenv import load_dotenv
import logging
import datetime

debug_logger = logging.getLogger('debug')
debug_logger.setLevel(logging.DEBUG)
debug_handler = logging.FileHandler('db.log')
debug_logger.addHandler(debug_handler)

info_logger = logging.getLogger('info')
info_logger.setLevel(logging.INFO)
info_handler = logging.FileHandler('db.log')
info_logger.addHandler(info_handler)

load_dotenv()


def create_table(sql):
    try:
        conn = psycopg2.connect(os.getenv("DATABASE_URL"))
        with conn.cursor() as cur:
            cur.execute(sql)
            conn.commit()
            debug_logger.debug("Table created successfully")
    except Exception as e:
        debug_logger.debug(e)
        conn.rollback()
    finally:
        conn.close()

def insert(sql, values):
    try:
        conn = psycopg2.connect(os.getenv("DATABASE_URL"))
        with conn.cursor() as cur:
            cur.execute(sql, values)
            conn.commit()
            debug_logger.debug("Record inserted successfully")
    except Exception as e:
        debug_logger.debug(e)
        conn.rollback()
    finally:
        conn.close()

def select(sql):
    try:
        conn = psycopg2.connect(os.getenv("DATABASE_URL"))
        with conn.cursor() as cur:
            cur.execute(sql)
            rows = cur.fetchall()
            debug_logger.debug("Record selected successfully")
            return rows
    except Exception as e:
        debug_logger.debug(e)
        conn.rollback()
    finally:
        conn.close()