import time
from datetime import datetime

from config import SETTINGS, ES_HOST, dsl, index, logger
from elasticsearch_store import ElasticLoader, EsIndexCreator
from psql_extractor import PostgresExtractor
from state_handler import State
from query import get_query

state = State()
postgres_extractor = PostgresExtractor(dsl=dsl)
elastic_loader = ElasticLoader(config=ES_HOST, state=state)
es_index_creator = EsIndexCreator()


def etl(query: str, index: str) -> None:

    data_generator = postgres_extractor.get_generator(query)
    elastic_loader.upload_data(data_generator, index)


if __name__ == "__main__":
    es_index_creator.create_index(SETTINGS, index)
    while True:
        logger.info("Starting sync...")

        load_from = state.get_state(f"load_from_{index}",
                                    default=str(datetime.min))

        try:
            query = get_query(load_from)
            etl(query, index)

        except ValueError as ex:
            logger.error("Skipping index %s: %s", index, ex)
            continue

        logger.info("Sleep for %s seconds", 30)
        time.sleep(30)
