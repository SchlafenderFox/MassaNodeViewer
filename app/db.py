from datetime import datetime

import psycopg2
from psycopg2.extras import RealDictCursor

from app.settings import PG_HOST, PG_PORT, POSTGRES_PASSWORD, POSTGRES_DB, POSTGRES_USER


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class DB(metaclass=Singleton):
    def __init__(self):
        self.conn = psycopg2.connect(dbname=POSTGRES_DB,
                                     user=POSTGRES_USER,
                                     password=POSTGRES_PASSWORD,
                                     host=PG_HOST,
                                     port=PG_PORT)
        self.conn.autocommit = True
        self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)

        self.__create_data_base()

    def __create_data_base(self):
        with open('./cycles.sql', 'rt') as f:
            self.cursor.execute(f.read())

    def __del__(self):
        self.conn.close()

    def insert_new_cycles(self, cycles: list):
        for cycle in cycles:
            self.__insert_new_cycle(cycle)

    def __insert_new_cycle(self, cycle: dict):
        self.cursor.execute(
            "INSERT INTO cycles (cycles_id, produce_blocks, failed_blocks, added_time) VALUES(%s, %s, %s, %s) ON CONFLICT DO NOTHING",
            (cycle['id'], cycle['produce_blocks'], cycle['failed_blocks'], datetime.now()))

    def get_all_cycles(self):
        self.cursor.execute("""SELECT * FROM cycles""")
        cycles = list()
        for cycle in self.cursor.fetchall():
            cycles.append(cycle)

        return cycles
