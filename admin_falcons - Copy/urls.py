# -*- coding: utf-8 -*-
"""
Created on Tue Jul 22 11:18:42 2025

@author: goranklasic
"""

from django.contrib import admin
from django.urls import path
from login import views
from django.conf import settings
from django.conf.urls.static import static
import os
from pathlib import Path
from login import views

BASE_DIR = Path(__file__).resolve().parent.parent

urlpatterns = [
    # 🧠 System & session routes
    path('admin/', admin.site.urls),
    path('admin-falcons/', views.login_view, name='login'),
    path('admin-falcons/dashboard/', views.dashboard_view, name='dashboard'),
    path('admin-falcons/logout/', views.logout_view, name='logout'),

    # 📇 Contacts
    path('admin-falcons/contacts/', views.contact_list_view, name='contact_list_view'),
    path('admin-falcons/contacts/edit/<int:pk>/', views.contact_edit_view, name='contact_edit_view'),
    path('admin-falcons/contacts/print/', views.contact_print_view, name='contact_print_view'),
    path('admin-falcons/contacts/print/<int:pk>/', views.print_single_contact_view, name='print_single_contact_view'),

    # 🧑‍🏫 Coaches
    path('admin-falcons/coaches/', views.coach_list_view, name='coach_list'),
    path('admin-falcons/coaches/edit/<int:pk>/', views.edit_coach_view, name='coach_edit'),
    path('admin-falcons/coaches/print/', views.print_coaches_view, name='coach_print'),
    path('admin-falcons/coaches/print/<int:pk>/', views.print_single_coach_view, name='print_single_coach_view'),
    path('admin-falcons/coaches/add/', views.add_coach_view, name='add_coach'),

    # 🗑️ Certificates
    path('admin-falcons/certificates/delete/<int:cert_id>/', views.delete_certificate_view, name='delete_certificate'),

    # 👥 Teams
    path('admin-falcons/teams/', views.team_list_view, name='team_list'),
    path('admin-falcons/teams/edit/<int:pk>/', views.team_edit_view, name='team_edit'),
    path('admin-falcons/teams/print/', views.team_print_all_view, name='team_print_all'),
    path('admin-falcons/teams/print/<int:pk>/', views.team_print_one_view, name='team_print_one'),
    path('admin-falcons/teams/add/', views.add_team_view, name='add_team'),

    # 👥 Parents
    path('admin-falcons/parents/add/', views.add_parent_view, name='add_parent'),
    path('admin-falcons/parents/<int:pk>/edit/', views.edit_parent_view, name='edit_parent'),
    path('admin-falcons/parents/<int:pk>/print/', views.print_parent_view, name='print_parent'),
    path('admin-falcons/parents/print_all/', views.print_all_parents_view, name='print_all_parents'),
    path('admin-falcons/parents/', views.parents_list_view, name='parents_list'),

    # 👥 Players
    path('admin-falcons/players/', views.player_list_view, name='player_list'),
    path('admin-falcons/players/add/', views.add_player_view, name='add_player'),
    path('admin-falcons/players/<int:pk>/edit/', views.edit_player_view, name='edit_player'),
    path('admin-falcons/players/<int:pk>/print/', views.print_player_view, name='print_player'),
    path('admin-falcons/players/print_all/', views.print_all_players_view, name='print_all_players'),
    path('admin-falcons/players/<int:player_id>/form/', views.generate_player_form, name='generate_player_form')

] + static(settings.STATIC_URL, document_root=os.path.join(BASE_DIR, 'static'))