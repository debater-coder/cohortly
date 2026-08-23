from .answer_views import (
    answer_delete,
    answer_edit_view,
    answer_upvote,
    mark_as_solution,
)
from .question_views import (
    question_ask_view,
    question_delete,
    question_detail_view,
    question_edit_view,
    question_list_view,
    question_upvote,
)

__all__ = [
    "question_ask_view",
    "question_detail_view",
    "question_list_view",
    "question_upvote",
    "question_edit_view",
    "answer_upvote",
    "mark_as_solution",
    "answer_edit_view",
    "answer_delete",
    "question_delete",
]
