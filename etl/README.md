# Для запуска:

1. Создать .env файл на основе .env.template в папке "postgres_to_es"
2. Потребуется уже запущенная postgres (локально или в другом докер контейнере)
3. Установить Elasticsearch командой: docker run -p 9200:9200 -e "discovery.type=single-node" docker.elastic.co/elasticsearch/elasticsearch:7.7.0
4. pip install -r requirements.txt
5. Запустить скрипт main.py в папке "postgres_to_es"