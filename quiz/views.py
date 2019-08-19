from django.shortcuts import render, HttpResponseRedirect
from django.conf import settings
from django.contrib.auth.decorators import login_required

from .models import *
from .exceptions.CheatDetectedException import CheatDetectedException


def redirect_to_main(request):
    return HttpResponseRedirect('/')


def quiz_ready(request, quiz_id):

    if 'success' in request.GET.keys():
        return render(request, 'quiz/success.html')

    if 'start' in request.GET.keys():
        question_ids = [question.id for question in QuizQuestions.objects.filter(quiz_id=quiz_id)]

        ip_address = get_ip_address(request.META)

        if not CurrentlyDoing.objects.filter(ip_address=ip_address, quiz_id=quiz_id).exists():  # если еще не проходил
            first_stage = QuizQuestions.objects.filter(quiz_id=quiz_id)[0].id

            # add an ip address and the first question's id into the database
            CurrentlyDoing(quiz_id=quiz_id,
                           ip_address=ip_address,
                           stage=first_stage).save()

            start_stage = first_stage
        else:
            currently_doing = CurrentlyDoing.objects.get(ip_address=ip_address, quiz_id=quiz_id)

            if currently_doing.stage == -1:
                return render(request, 'quiz/already_completed.html')

            # айди вопроса, на котором остановился пользователь
            start_stage = currently_doing.stage

            # обрезать список до айди, на котором остановился пользователь
            question_ids = question_ids[question_ids.index(start_stage):]

        quiz_name = Quiz.objects.get(id=quiz_id).name

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

    quiz_name = Quiz.objects.get(id=quiz_id).name

    return render(request, 'quiz/quiz.html', {'quiz_name': quiz_name, 'title': quiz_name})


def update_answer(request, quiz_id):
    """
    только для post запросов с помощью ajax
    """

    if not request.POST:
        return HttpResponseRedirect('/')

    currently_doing = CurrentlyDoing.objects.get(ip_address=get_ip_address(request.META), quiz_id=quiz_id)

    answer_id = request.POST['answer_id']

    answer = QuestionAnswers.objects.get(id=answer_id)

    if currently_doing.stage > answer.quiz_questions_id or currently_doing.stage == -1:  # проверки на попытку накрутить
        raise CheatDetectedException

    answer.update()

    questions_ids = [question.id for question in QuizQuestions.objects.filter(quiz_id=quiz_id)]

    try:
        next_question_id = questions_ids[questions_ids.index(answer.quiz_questions_id) + 1]  # получить айди след. вопр.
    except IndexError:
        currently_doing.update_stage(-1)  # -1 = пользователь уже прошел тест ранее
    else:
        currently_doing.update_stage(next_question_id)

    return HttpResponseRedirect('/quiz/%s/' % quiz_id)


@login_required
def quiz_results(request, quiz_id):
    questions = QuizQuestions.objects.filter(quiz_id=quiz_id)
    # answers = QuestionAnswers.objects.filter(quiz_questions__quiz_id=quiz_id)

    qa = dict()

    for question in questions:
        answers = QuestionAnswers.objects.filter(quiz_questions_id=question.id).order_by('-counter')
        qa[question] = answers

    # for question in questions:
    #     answers = QuestionAnswers.objects.filter(quiz_questions_id=question.id)

    return render(request, 'quiz/results.html', {'qa': qa})


def get_ip_address(request_meta):
    return '127.0.0.1' if settings.DEBUG or settings.TEST_IN_PROGRESS else request_meta.get('HTTP_X_FORWARDED_FOR')


# def import_spells(request, quiz_id):
    # spells = list()
    #
    # with open('C:/Users/osx11/Desktop/spell_names.txt', 'rb') as f:
    #     for line in f:
    #         spells.append(line.decode('utf-8').replace('\n', ''))

    # for spell in spells:
    #     question = 'Как часто вы используете заклинание %s?' % spell
    #     QuizQuestions(quiz_id=quiz_id, question=question).save()

    # answers = ['Часто', 'Иногда', 'Вообще не использую']
    #
    # for question in QuizQuestions.objects.filter(quiz_id=quiz_id):
    #     for answer in answers:
    #         QuestionAnswers(quiz_questions_id=question.id, answer=answer).save()

