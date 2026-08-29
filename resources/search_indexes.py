from haystack import indexes

from resources.models import Resource


class ResourceIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    created_at = indexes.DateTimeField(model_attr="created_at")

    def get_model(self):
        return Resource
