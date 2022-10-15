from typing import Optional

import backoff
import psycopg2
from psycopg2.extensions import connection as pg_conn
from psycopg2.extras import DictCursor

from config import BACKOFF_CONFIG
from models import MoviesES


class PostgresExtractor:
    def __init__(self, dsl: dict, conn: Optional[pg_conn] = None) -> None:
        self.postgres_conn = conn
        self.dsl = dsl

    @property
    def postgres_connection(self) -> pg_conn:
        """
        Создает новый объект подключения, если соеденение не создано,
        либо закрыто
        """
        if self.postgres_conn is None or self.postgres_conn.closed:
            self.postgres_conn = self.create_conn()

        return self.postgres_conn

    @backoff.on_exception(backoff.expo, **BACKOFF_CONFIG)
    def create_conn(self) -> pg_conn:
        """Закрывает старый connection и создает новый объект подключения"""
        if self.postgres_conn is not None:
            self.postgres_conn.close()

        return psycopg2.connect(**self.dsl, cursor_factory=DictCursor)

    @backoff.on_exception(backoff.expo, **BACKOFF_CONFIG)
    def get_generator(self, query: str, itersize: int = 999, model=MoviesES):
        """Возвращает итератор данных в нужном формате для ES"""
        cur = self.postgres_connection.cursor()
        cur.itersize = itersize
        cur.execute(query)

        for row in cur:
            instance = model(**row)
            yield instance, str(row["updated_at"])
