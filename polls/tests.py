import datetime
from urllib import response

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from .models import Question


def create_question(question_text, days):
    '''
    Создает вопрос с заданным `question_text` и показывает заданное количество
    за указанный промежутов времени `days` (отрицательное значение для вопросов, 
    опубликованных в прошлом, положительное значение для вопросов, которые еще не опубликованы).
    '''
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


class QuestionModelTests(TestCase):

    def test_was_published_recently_with_future_question(self):
        '''
        was_published_recently() возвращает False для вопросов,
        у которых pub_date находится в будущем.
        '''
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        '''
        was_published_recently() возвращает False для вопросов,
        у которых pub_date больше 1 дня.
        '''
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        '''
        was_published_recently() возвращает True для вопросов,
        у которых pub_date приходиться на последний день.
        '''
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), False)


class QuestionIndexViewTest(TestCase):
    def test_no_question(self):
        '''
        Если вопросов нет, воводим соответствующее сообщение.
        '''
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_past_question(self):
        '''
        Вопросы с датой публикации в прошлом отображаются на главной странице.
        '''
        question = create_question(question_text="Past question.", days=-30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'], [question])

    def test_future_question(self):
        '''
        Вопросы с датой публикации в будущем не отображаются на главной странице.
        '''
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_future_question_and_past_question(self):
        '''
        Еслисуществуют вопросы созданные в прошлом и будущем, 
        отображаются только вопросы созданные в прошлом.
        '''
        question = create_question(question_text="Past question.", days=-30)
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'], [question],)

    def test_two_past_questions(self):
        '''
        Несколько вопросов может отображаться на индоксной строке.
        '''
        question1 = create_question(question_text="Past question 1.", days=-30)
        question2 = create_question(question_text="Past question 2.", days=-5)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'], [question2, question1],)


class QuestionDetailViewTests(TestCase):
    def test_future_question(self):
        '''
        Вопрос с датой публикации в будущем возвращает 404 не найдено.
        '''
        future_question = create_question(question_text='Future question.', days=5)
        url = reverse('polls:detail', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        '''
        Вопроса с датой публикации в прошлом отображается текст вопроса.
        '''
        past_question = create_question(question_text='Past Question.', days=-5)
        url = reverse('polls:detail', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)