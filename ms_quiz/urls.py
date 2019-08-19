from django.contrib import admin
from django.urls import path, include

from main.views import index

# from quiz.views import

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index),
    path('quiz/', include('quiz.urls'))
]
