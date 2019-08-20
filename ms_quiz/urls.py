from django.contrib import admin
from django.urls import path, include

from main.views import index

from decouple import config

urlpatterns = [
    path(config('ADMIN_URL'), admin.site.urls),
    path('', index),
    path('quiz/', include('quiz.urls'))
]
