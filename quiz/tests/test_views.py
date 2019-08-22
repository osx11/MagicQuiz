from django.test import TestCase, Client

from quiz.models import *
from quiz.exceptions.CheatDetectedException import CheatDetectedException
from main.common import strptime


class TestViews(TestCase):
    def setUp(self):
        self.ip_address = '127.0.0.1'
        self.nickname = 'test_user'

        self.quiz = Quiz(name='TestQuiz', expires=strptime('2100-01-01 00:00:00'))
        self.quiz.save()

        # в тесте будет 4 вопроса и 4 варианта ответа на каждый из них
        for i in range(1, 5):
            QuizQuestions(quiz_id=self.quiz.id, question='Test Question #%s' % i).save()

            for j in range(1, 5):
                QuestionAnswers(quiz_questions_id=i, answer='Test Answer #%s' % j).save()

        self.question_ids = [question.id for question in QuizQuestions.objects.all()]

        # принудительно зарегистрируемся на тест
        CurrentlyDoing(quiz_id=1,
                       ip_address=self.ip_address,
                       nickname=self.nickname,
                       stage=1).save()

    def slice_questions_ids(self, index):
        """
        обрезать все в questions_id до определенного индекса
        """

        return self.question_ids[self.question_ids.index(index):]

    def testFirstStart(self):
        """
        пользователь начинает проходить тест первый раз
        """

        client = Client()

        response = client.get('/quiz/1/?start')

        currently_doing = CurrentlyDoing.objects.get(ip_address=self.ip_address)

        self.assertEquals(currently_doing.quiz_id, 1)
        self.assertEquals(currently_doing.stage, 1)
        self.assertEquals(response.context['start_stage'], 1)
        self.assertEquals(response.context['question_ids'], self.question_ids)

    def testPageReload(self):
        """
        имитация перезагрузки страницы
        """

        client = Client()

        for i in range(1, 5):
            if i != 1:
                cd = CurrentlyDoing.objects.get(ip_address=self.ip_address)
                cd.stage = i
                cd.save()

            response = client.get('/quiz/1/?start')
            question_ids = self.slice_questions_ids(i)

            self.assertEquals(response.context['start_stage'], i)

            self.assertEquals(response.context['question_ids'], question_ids)

    def testStartCompleted(self):
        """
        пользователь пытается пройти заново уже завершенный тест
        """

        client = Client()

        cd = CurrentlyDoing.objects.get(ip_address=self.ip_address, quiz=1)
        cd.stage = -1
        cd.save()

        response = client.get('/quiz/1/?start')

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'quiz/already_completed.html')

    def testUpdateAnswer(self):
        """
        нормальное обновление счетчика ответа в БД
        """

        client = Client()

        client.get('/quiz/1/?start')

        for i in range(11):
            client.post('/quiz/1/update_answer/', {'csrfmiddlewaretoken': '', 'answer_id': 4})

            cd = CurrentlyDoing.objects.get(ip_address=self.ip_address)
            cd.stage = 1  # чтобы не попасть под проверку на читера, сбрасываем текущий этап
            cd.save()

        self.assertEquals(QuestionAnswers.objects.get(id=4).counter, 11)

        for i in range(25):
            cd = CurrentlyDoing.objects.get(ip_address=self.ip_address)
            cd.stage = 2  # чтобы не попасть под проверку на читера, сбрасываем текущий этап
            cd.save()

            client.post('/quiz/1/update_answer/', {'csrfmiddlewaretoken': '', 'answer_id': 6})

        self.assertEquals(QuestionAnswers.objects.get(id=6).counter, 25)

    def testCheatAttempt(self):
        """
        пользователь пытается дать ответ на вопрос, на который уже давал ответ ранее
        """

        client = Client()

        client.get('/quiz/1/?start')

        cd = CurrentlyDoing.objects.get(ip_address=self.ip_address)

        self.assertEquals(cd.stage, 1)

        with self.assertRaises(CheatDetectedException):
            for i in range(2):
                client.post('/quiz/1/update_answer/', {'csrfmiddlewaretoken': '', 'answer_id': 1})

        cd.refresh_from_db()
        self.assertEquals(cd.stage, 2)

        with self.assertRaises(CheatDetectedException):
            for i in range(2):
                client.post('/quiz/1/update_answer/', {'csrfmiddlewaretoken': '', 'answer_id': 5})

        cd.refresh_from_db()
        self.assertEquals(cd.stage, 3)

        with self.assertRaises(CheatDetectedException):
            client.post('/quiz/1/update_answer/', {'csrfmiddlewaretoken': '', 'answer_id': 16})

        cd.refresh_from_db()
        self.assertEquals(cd.stage, 3)

    def testQuizFinished(self):
        """
        пользователь закончил прохождение теста
        """

        client = Client()

        client.get('/quiz/1/?start')

        client.post('/quiz/1/update_answer/', {'csrfmiddlewaretoken': '', 'answer_id': 1})   # 1 вопрос
        client.post('/quiz/1/update_answer/', {'csrfmiddlewaretoken': '', 'answer_id': 5})   # 2 вопрос
        client.post('/quiz/1/update_answer/', {'csrfmiddlewaretoken': '', 'answer_id': 9})   # 3 вопрос
        client.post('/quiz/1/update_answer/', {'csrfmiddlewaretoken': '', 'answer_id': 13})  # 4 вопрос

        cd = CurrentlyDoing.objects.get(ip_address=self.ip_address)

        self.assertEquals(cd.stage, -1)
