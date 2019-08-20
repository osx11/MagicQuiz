from django.db import models

from .exceptions.CheatDetectedException import CheatDetectedException

from datetime import datetime


class Quiz(models.Model):
    name = models.CharField(max_length=255, unique=True)
    expires = models.DateTimeField()

    def is_expired(self):
        time_format = '%y-%m-%d %H:%M:%S'
        return datetime.now() > datetime.strptime(self.expires.strftime(time_format), time_format)

    def __str__(self):  # для корректного отображения в админке
        return self.name


class QuizQuestions(models.Model):
    question = models.CharField(max_length=255)

    quiz = models.ForeignKey(Quiz, related_name='questions', on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):  # для корректного отображения в админке
        return '%s (%s)' % (self.question, self.quiz.name)


class QuestionAnswers(models.Model):
    answer = models.CharField(max_length=255)
    counter = models.IntegerField(default=0)  # сколько всего человек выбрали этот ответ

    quiz_questions = models.ForeignKey(QuizQuestions, related_name='answers', on_delete=models.SET_NULL, blank=True,
                                       null=True)

    def update(self, ip_address):
        """
        обновляет счетчик ответа, а также активный этап для IP-адреса в CurrentlyDoing
        """

        quiz_id = self.quiz_questions.quiz_id

        currently_doing = CurrentlyDoing.objects.get(ip_address=ip_address, quiz_id=quiz_id)

        # проверки на попытку накрутить
        if currently_doing.stage > self.quiz_questions_id or currently_doing.stage == -1:
            raise CheatDetectedException

        self.counter += 1
        self.save()

        questions_ids = [question.id for question in QuizQuestions.objects.filter(quiz_id=quiz_id)]

        try:
            next_question_id = questions_ids[
                questions_ids.index(self.quiz_questions_id) + 1]  # получить айди след. вопр.
        except IndexError:
            currently_doing.update_stage(-1)  # -1 = пользователь уже прошел тест ранее
        else:
            currently_doing.update_stage(next_question_id)

    def __str__(self):  # для корректного отображения в админке
        return self.answer


class CurrentlyDoing(models.Model):
    ip_address = models.GenericIPAddressField()
    stage = models.IntegerField(default=1)
    nickname = models.CharField(max_length=255)

    quiz = models.ForeignKey(Quiz, related_name='currently_doing', on_delete=models.SET_NULL, blank=True, null=True)

    def update_stage(self, stage):
        self.stage = stage
        self.save()
