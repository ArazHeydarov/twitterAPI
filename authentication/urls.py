from django.contrib import admin
from django.urls import path, include
from authentication import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('signin/', views.signin, name='signin'),
    path('signout/', views.sign_out, name='sign_out'),
]
