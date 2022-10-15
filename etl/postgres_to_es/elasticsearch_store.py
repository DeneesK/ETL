import time
from typing import Iterator, Tuple

import backoff
from elasticsearch import Elasticsearch, helpers

from config import BACKOFF_CONFIG, ES_HOST, logger
from state_handler import State
from models import MoviesES

es = Elasticsearch([ES_HOST])


class EsIndexCreator:
    def __init__(self, es_object: Elasticsearch = es) -> None:
        self.es_object = es_object

    def create_index(self, settings: dict, index: str) -> None:
        """
        Создаем индекс movies, метод принимает settings - настройки индекса
        и index -название самого индекса
        """
        if not self.es_object.indices.exists(index):
            self.es_object.indices.create(index=index, body=settings)
            logger.info('Index Created')
        else:
            logger.info('Index already created')


class ElasticLoader:
    def __init__(
        self,
        config: str,
        state: State,
        elastic_conn=None,
    ) -> None:
        self.config = config
        self.state = state
        self._elastic_conn = elastic_conn

    @property
    def elastic_conn(self) -> Elasticsearch:
        """
        Вернуть текущее подключение для Elasticsearch или
        инициализировать новое
        """
        if self._elastic_conn is None or not self._elastic_conn.ping():
            self._elastic_conn = self.create_conn()

        return self._elastic_conn

    @backoff.on_exception(backoff.expo, **BACKOFF_CONFIG)
    def create_conn(self) -> Elasticsearch:
        """Создать новое подключение для ES"""
        return Elasticsearch([self.config])

    @backoff.on_exception(backoff.expo, **BACKOFF_CONFIG)
    def create_docs(
        self, data: Iterator[Tuple[MoviesES, str]], index: str, itersize: int = 999
    ):
        """
        Возвращает итератор документов для Elasticsearch.
        Так же во время продуцирования фильмов записывает
        в стейт updated_at каждого n-го фильма (n=itersize)
        После продуцирования всех фильмов записывает в стейт
        последний updated_at
        """
        i = 0
        last_updated_at = ""
        key = f"load_from_{index}"

        for movie, updated_at in data:
            i += 1
            last_updated_at = updated_at
            movies_data = movie.dict()
            movies_data['_id'] = movies_data['id']
            yield movies_data

            if i % itersize == 0:
                self.state.set_state(key, last_updated_at)

        # Записываем в стейт только если у нас были какие-то записи
        if last_updated_at:
            self.state.set_state(key, last_updated_at)

    @backoff.on_exception(backoff.expo, **BACKOFF_CONFIG)
    def upload_data(self, data: Iterator[Tuple[MoviesES, str]], index: str, itersize: int = 999) -> None:
        """Загружает данные в ES используя итератор"""
        t = time.perf_counter()

        docs_generator = self.create_docs(data, index, itersize)

        lines, _ = helpers.bulk(
            client=self.elastic_conn,
            actions=docs_generator,
            index=index,
            chunk_size=itersize,
        )

        elapsed = time.perf_counter() - t

        if lines == 0:
            logger.info("Nothing to update for index %s", index)
        else:
            logger.info(
                "%s lines saved in %s for index %s",
                lines, elapsed, index
                )
