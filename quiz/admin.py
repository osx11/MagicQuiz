from django.contrib import admin

from .models import Quiz, QuizQuestions, QuestionAnswers


class QuizAdmin(admin.ModelAdmin):
    list_display = ('name', 'id')


class QuizQuestionsAdmin(admin.ModelAdmin):
    list_display = ('question', 'quiz_id', 'id')
    list_filter = ('quiz__name',)


class QuestionAnswersAdmin(admin.ModelAdmin):
    list_display = ('answer', 'quiz_questions_id', 'id')
    list_filter = ('quiz_questions__quiz__name', 'quiz_questions__question')


admin.site.register(Quiz, QuizAdmin)
admin.site.register(QuizQuestions, QuizQuestionsAdmin)
admin.site.register(QuestionAnswers, QuestionAnswersAdmin)
