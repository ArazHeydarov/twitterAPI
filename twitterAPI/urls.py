"""twitterAPI URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from twitterAPI import views

urlpatterns = [

    path('', include('authentication.urls')),
    path('', views.index, name='index'),
    path('dashboard', views.dashboard, name='dashboard'),
    path('twitter-auth/', views.twitter_auth, name='twitter_auth'),
    path('verify/', views.verify, name='twitter_verify'),
    path('twitter-followers/', views.twitter_followers, name='twitter_followers'),
    path('twitter-followers-update', views.update_twitter_followers, name='twitter_followers_update')
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
