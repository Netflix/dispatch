from enum import Enum


class FeedbackRating(str, Enum):
    very_satisfied = "Very satisfied"
    somewhat_satisfied = "Somewhat satisfied"
    neither_satisfied_nor_dissatisfied = "Neither satisfied nor dissatisfied"
    somewhat_dissatisfied = "Somewhat dissatisfied"
    very_dissatisfied = "Very dissatisfied"
