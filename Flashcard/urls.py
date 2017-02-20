"""Flashcard URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin

import API.views as views
import Web.views as web_views

# router.register(r'users', views.UserViewSet)
# router.register(r'groups', views.GroupViewSet)

urlpatterns = [
    # Admin
    url(r'^admin/', admin.site.urls),

    # API Stuff
    url(r'^cards/$', views.card_list),
    url(r'^cards/(?P<pk>[0-9]+)$', views.card_detail),
    url(r'^login/$', views.login),
    url(r'^register/$', views.create_user),
    url(r'^decks/$', views.get_users_deck),
    url(r'^decks/create/$', views.create_deck),
    url(r'^decks/(?P<pk>[0-9]+)$', views.card_list),

    # Web Stuff
    url(r'^web/$', web_views.index, name='index'),
    url(r'^web/logout/$', web_views.logout, name='logout'),
    url(r'^web/register/$', web_views.register, name='register'),
    url(r'^web/deck/create', web_views.deck_create, name='deck_create'),
    url(r'^web/deck/edit$', web_views.deck_edit, name='deck_edit'),
    url(r'^web/deck/delete$', web_views.deck_delete, name='deck_delete'),

    url(r'^api-auth/', include('rest_framework.urls')),
]
