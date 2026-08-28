import datetime

from haystack import indexes

from tutoring.models import Session


class SessionIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    created_at = indexes.DateTimeField(model_attr="created_at")

    def get_model(self):
        return Session
