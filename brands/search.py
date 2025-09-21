# brands/search.py
from elasticsearch_dsl import Document, Text, Date, Keyword

class ProductIndex(Document):
    name = Text()
    description = Text()
    category = Keyword()
    video_categories = Keyword(multi=True)
    created_at = Date()

    class Index:
        name = "products"
