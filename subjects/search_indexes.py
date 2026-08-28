from haystack import indexes

from subjects.models import Subject, Topic


class SubjectIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    created_at = indexes.DateTimeField(model_attr="created_at")

    def get_model(self):
        return Subject


class TopicString(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    created_at = indexes.DateTimeField(model_attr="created_at")

    def get_model(self):
        return Topic
