from django.contrib import admin
from django.urls import path
from .views import Author, EmailVerification, ResetPassword, Messages, GetUserMessages, \
    UserSignupEvent

urlpatterns = [
    path('email.verify', EmailVerification.as_view()),
    path('reset.password', ResetPassword.as_view()),
    path('author', Author.as_view()),
    path('messages', Messages.as_view()),
    path('get.messages', GetUserMessages.as_view()),
    path('event.user.signup', UserSignupEvent.as_view())
]