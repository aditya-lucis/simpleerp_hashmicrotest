"""
URL configuration for myerp project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.contrib import admin
from django.urls import path
from core import views as core_views
from accounting import views as acc_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', core_views.dashboard, name='dashboard'),
    path('login/', core_views.login_view, name='login'),
    path('logout/', core_views.logout_view, name='logout'),

    # General Journal
    path('journal/', acc_views.journal_list, name='journal_list'),
    path('journal/json/', acc_views.journal_json, name='journal_json'),
    path('journal/add/', acc_views.journal_create, name='journal_create'),

    # Chart of Accounts (CoA)
    path('coa/', acc_views.coa_page, name='coa_list'),
    path('coa/json/', acc_views.coa_json, name='coa_json'),
    path('coa/save/', acc_views.coa_save_ajax, name='coa_save_ajax'),
    path('coa/delete/<int:pk>/', acc_views.coa_delete_ajax, name='coa_delete_ajax'),

    # Tools Analyzer
    path('tools/analyzer/', acc_views.string_analyzer, name='string_analyzer'),
    path('tools/analyzer/process/', acc_views.string_analyzer_ajax, name='string_analyzer_ajax'),
]
