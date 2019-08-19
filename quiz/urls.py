from django.urls import path

from . import views

urlpatterns = [
    path('', views.redirect_to_main),
    path('<int:quiz_id>/', views.quiz_ready, name='quiz_ready'),
    path('<int:quiz_id>/update_answer/', views.update_answer, name='update_answer'),
    path('<int:quiz_id>/results/', views.quiz_results, name='quiz_results'),
    # path('<int:quiz_id>/import/', views.import_spells)
]
