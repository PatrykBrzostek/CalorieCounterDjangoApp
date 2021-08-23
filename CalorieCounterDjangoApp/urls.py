from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from CalorieCounter.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', MyLoginView.as_view()),
    path('logout/', auth_views.LogoutView.as_view()),
    path('profile/<username>/<str:url_date>/', ProfileView.as_view()),
]
