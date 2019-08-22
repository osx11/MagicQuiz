from django.test import TestCase

from quiz.models import Quiz
from main.common import strptime


class TestModels(TestCase):
    def setUp(self):
        self.quiz = Quiz(name='TestQuiz', expires=strptime('2100-01-01 00:00:00'))
        self.quiz.save()

    def testQuizExpires(self):
        self.assertFalse(self.quiz.is_expired())

        self.quiz.expires = strptime('3150-05-10 17:06:00')
        self.quiz.save()

        self.assertFalse(self.quiz.is_expired())

        self.quiz.expires = strptime('1980-01-02 12:12:12')
        self.quiz.save()

        self.assertTrue(self.quiz.is_expired())

        self.quiz.expires = strptime('1980-01-02 12:12:12')

        self.assertTrue(self.quiz.is_expired())
