from django.db import models


class Quiz(models.Model):
    name = models.CharField(max_length=255, unique=True)

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

    def update(self):
        self.counter += 1
        self.save()

    def __str__(self):  # для корректного отображения в админке
        return self.answer


class CurrentlyDoing(models.Model):
    ip_address = models.GenericIPAddressField()
    stage = models.IntegerField(default=1)

    quiz = models.ForeignKey(Quiz, related_name='currently_doing', on_delete=models.SET_NULL, blank=True, null=True)

    def update_stage(self, stage):
        self.stage = stage
        self.save()
