from django.urls import path

from bot import views

app_name = 'bot'

urlpatterns = [
    path('verify', views.VerificationCodeView.as_view(), name='verify'),
]
