from django.core.management.base import BaseCommand
from brands.models import Product
from elasticsearch import Elasticsearch

es = Elasticsearch("http://127.0.0.1:9200")
INDEX = "products"

class Command(BaseCommand):
    help = "Reindex all products into Elasticsearch with autocomplete mapping"

    def handle(self, *args, **options):
        # Удаляем старый индекс
        if es.indices.exists(index=INDEX):
            es.indices.delete(index=INDEX)
            self.stdout.write(self.style.WARNING("Old index deleted."))

        # Создаём новый индекс с n-gram анализатором
        settings = {
            "settings": {
                "analysis": {
                    "analyzer": {
                        "autocomplete": {
                            "tokenizer": "autocomplete",
                            "filter": ["lowercase"]
                        }
                    },
                    "tokenizer": {
                        "autocomplete": {
                            "type": "edge_ngram",
                            "min_gram": 2,
                            "max_gram": 15,
                            "token_chars": ["letter", "digit"]
                        }
                    }
                }
            },
            "mappings": {
                "properties": {
                    "name": {
                        "type": "text",
                        "analyzer": "autocomplete",
                        "search_analyzer": "standard"
                    },
                    "description": {"type": "text"},
                    "category": {"type": "text"},
                    "created_at": {"type": "date"}
                }
            }
        }

        es.indices.create(index=INDEX, body=settings)
        self.stdout.write(self.style.SUCCESS("New index created with autocomplete mapping."))

        # Индексируем продукты
        for product in Product.objects.all():
            doc = {
                "id": product.id,
                "name": product.name,
                "description": product.description,
                "category": product.category,
                "created_at": product.created_at.isoformat(),
            }
            es.index(index=INDEX, id=product.id, body=doc)

        self.stdout.write(self.style.SUCCESS(f"{Product.objects.count()} products reindexed."))
