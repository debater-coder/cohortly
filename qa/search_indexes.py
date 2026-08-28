import datetime

from haystack import indexes

from qa.models import Answer, Question


class QuestionIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    created_at = indexes.DateTimeField(model_attr="created_at")

    def get_model(self):
        return Question


class AnswerString(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    created_at = indexes.DateTimeField(model_attr="created_at")

    def get_model(self):
        return Answer
