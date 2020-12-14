from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import render

import math
from django.urls import reverse_lazy
from django.views.generic import ListView, DeleteView
from spam_email.models import Email
from tabulate import tabulate
import pickle
import string

from nltk.corpus import stopwords


class HistoryView(LoginRequiredMixin, ListView):
    model = Email
    template_name = 'history.html'
    login_url = 'login'


class EmailDeleteView(LoginRequiredMixin, DeleteView):
    model = Email
    template_name = 'email_delete.html'
    success_url = reverse_lazy('history')
    login_url = 'login'

    def dispatch(self, request, *args, **kwargs):  # new
        obj = self.get_object()
        if obj.author != self.request.user:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


def home(request):
    if request.method == 'POST':
        message = request.POST.get('message')
        message_cp = message
        message = [message]
        message = text_process(message)
        message = [' '.join(message)]
        result, accuracy = predict(message)

        print('result is ', result, 'with accuracy ', accuracy)
        print("\n")

        if request.user.is_authenticated:
            # Save information to database
            email = Email()
            email.content = request.POST.get('message')
            email.result = result
            email.accuracy = accuracy
            email.author = request.user
            email.save()

        return render(request, 'home.html', {'result': result, 'message': message_cp, 'accuracy': accuracy})
    return render(request, 'home.html')


def predict(message):
    pipeline = importPipelines()

    test = pipeline.predict(message)
    test_prob = pipeline.predict_proba(message)

    value_spam = test_prob[0][1]
    value_ham = test_prob[0][0]

    print(tabulate([['Spam (1)', test_prob[0][1]], ['Ham (0)', test_prob[0][0]], ['Result', test[0]]],
                   headers=['What', 'Prob']))

    if value_spam > 0.5:
        result = 'spam'
        accuracy = value_spam

    elif value_spam <= 0.5:
        result = 'ham'
        accuracy = value_ham

    elif value_spam > 0.5:
        value = math.fabs(test_prob[0][1])

        if value_spam + 0.1 > value_ham:
            accuracy = value_spam
            result = 'spam'
        else:
            result = 'ham'
            accuracy = value_ham
    else:
        result = 'ham'
        accuracy = value_ham

    accuracy = round(accuracy, 2) * 100

    return result, accuracy


def text_process(message):
    noPunctuation = [char for char in message if char not in string.punctuation]
    noPunctuation = ''.join(noPunctuation)
    clean_message = [word for word in noPunctuation.split() if word.lower() not in stopwords.words('english')]
    return clean_message


def importPipelines():
    pipeline = pickle.load(open('emailSpamClf.pkl', 'rb'))
    return pipeline
