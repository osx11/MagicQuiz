from django.shortcuts import render, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import *
from .forms import RegistrationForm
from main.common import get_ip_address


def redirect_to_main(request):
    return HttpResponseRedirect('/')


def quiz_ready(request, quiz_id):

    if 'success' in request.GET.keys():
        return render(request, 'quiz/success.html')

    quiz = Quiz.objects.get(id=quiz_id)
    quiz_name = quiz.name

    if quiz.is_expired():  # если тест просрочен
        return render(request, 'quiz/expired.html', {'quiz_name': quiz_name, 'title': quiz_name})

    if 'start' in request.GET.keys():
        # список айди всех вопросов для теста (нужно, чтобы загружать вопросы из фронтенда)
        question_ids = [question.id for question in QuizQuestions.objects.filter(quiz_id=quiz_id)]

        ip_address = get_ip_address(request.META)

        if not CurrentlyDoing.objects.filter(ip_address=ip_address, quiz_id=quiz_id).exists():  # если еще не проходил
            return render(request, 'quiz/registration.html', {'quiz_id': quiz_id,
                                                              'title': quiz_name,
                                                              'messages': messages.get_messages(request)})
        else:
            currently_doing = CurrentlyDoing.objects.get(ip_address=ip_address, quiz_id=quiz_id)

            if currently_doing.stage == -1:
                return render(request, 'quiz/already_completed.html')

            # айди вопроса, на котором остановился пользователь
            start_stage = currently_doing.stage

            # обрезать список до айди, на котором остановился пользователь
            question_ids = question_ids[question_ids.index(start_stage):]

        return render(request, 'quiz/QA.html', {'quiz_id': quiz_id,
                                                'question_ids': question_ids,
                                                'start_stage': start_stage,
                                                'title': quiz_name})

    if 'question' in request.GET.keys():  # отрендерить только определенный вопрос и варианты ответа на него
        question_id = request.GET['question']
        question = QuizQuestions.objects.get(id=question_id)
        answers = QuestionAnswers.objects.filter(quiz_questions_id=question_id)

        return render(request, 'quiz/question.html', {'question': question,
                                                      'answers': answers})

    return render(request, 'quiz/quiz.html', {'quiz_name': quiz_name, 'title': quiz_name})


def register(request, quiz_id):
    """
    что-то типа регистрации
    """

    if not request.POST:
        return HttpResponseRedirect('/')

    if Quiz.objects.get(id=quiz_id).is_expired():  # на всякий пожарный
        return HttpResponseRedirect('/')

    form = RegistrationForm(request.POST)

    if form.is_valid():
        nickname = request.POST['nickname']

        if not CurrentlyDoing.objects.filter(quiz_id=quiz_id, nickname=nickname).exists():
            first_stage = QuizQuestions.objects.filter(quiz_id=quiz_id)[0].id
            CurrentlyDoing(quiz_id=quiz_id,
                           ip_address=get_ip_address(request.META),
                           nickname=nickname,
                           stage=first_stage).save()
        else:
            messages.error(request, "Такой ник уже зарегистрирован на этот тест")

    return HttpResponseRedirect('/quiz/%s/?start' % quiz_id)


def update_answer(request, quiz_id):
    """
    только для post запросов с помощью ajax
    """

    if not request.POST:
        return HttpResponseRedirect('/')

    answer_id = request.POST['answer_id']

    answer = QuestionAnswers.objects.get(id=answer_id)
    answer.update(get_ip_address(request.META))

    return HttpResponseRedirect('/quiz/%s/' % quiz_id)


@login_required
def quiz_results(request, quiz_id):
    total_completed = CurrentlyDoing.objects.filter(quiz_id=quiz_id, stage=-1).count()
    total_in_progress = CurrentlyDoing.objects.filter(quiz_id=quiz_id).exclude(stage=-1).count()

    questions = QuizQuestions.objects.filter(quiz_id=quiz_id)

    qa = dict()

    for question in questions:
        answers = QuestionAnswers.objects.filter(quiz_questions_id=question.id).order_by('-counter')
        qa[question] = answers

    return render(request, 'quiz/results.html', {'total_completed': total_completed,
                                                 'total_in_progress': total_in_progress,
                                                 'qa': qa})


# def import_spells(request, quiz_id):
#     spells = list()
#
#     with open('C:/Users/osx11/Desktop/spell_names.txt', 'rb') as f:
#         for line in f:
#             spells.append(line.decode('utf-8').replace('\n', ''))
#
#     for spell in spells:
#         question = 'Как часто вы используете заклинание %s?' % spell
#         QuizQuestions(quiz_id=quiz_id, question=question).save()
#
#     answers = ['Часто', 'Иногда', 'Вообще не использую']
#
#     for question in QuizQuestions.objects.filter(quiz_id=quiz_id):
#         for answer in answers:
#             QuestionAnswers(quiz_questions_id=question.id, answer=answer).save()
#
