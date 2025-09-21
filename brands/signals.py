from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from elasticsearch import Elasticsearch
from .models import Product

es = Elasticsearch("http://127.0.0.1:9200")

INDEX = "products"

@receiver(post_save, sender=Product)
def index_product(sender, instance, **kwargs):
    doc = {
        "id": instance.id,
        "name": instance.name,
        "description": instance.description,
        "category": instance.category,
        "created_at": instance.created_at.isoformat(),
    }
    es.index(index=INDEX, id=instance.id, body=doc)

@receiver(post_delete, sender=Product)
def delete_product(sender, instance, **kwargs):
    es.delete(index=INDEX, id=instance.id, ignore=[404])
