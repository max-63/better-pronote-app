from django.urls import path
from .views import *


urlpatterns = [
    path('', index, name='index'),
    path('login', login, name='login'),
    path('register', register, name='register'),
    path('dashboard', dashboard, name='dashboard'),
    path('check_pronote_lie', check_pronote_lie, name='check_pronote_lie'),
    path('url_liee_pronote', url_liee_pronote, name='url_liee_pronote'),
    path('get_devoirs_database/', get_devoirs_database, name='get_devoirs_database'),
    path('get_notes', get_notes, name='get_notes'),
]
