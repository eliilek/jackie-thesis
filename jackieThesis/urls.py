"""jackieThesis URL Configuration

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
from django.conf.urls import include, url
from django.contrib import admin
admin.autodiscover()

import experiments.views

urlpatterns = [
    url(r'^$', experiments.views.index, name="index"),
    url(r'^session', experiments.views.session, name='session'),
    url(r'^admin/', admin.site.urls, name="admin"),
    url(r'^trial', experiments.views.trial, name='trial'),
    url(r'^myself', experiments.views.myself, name='myself'),
    url(r'^results', experiments.views.index_results, name='index_results'),
    url(r'^view_results/(?P<subid>[0-9]+)/$', experiments.views.results, name='results'),
    url(r'^report_results', experiments.views.report_results, name='report_results'),
]
