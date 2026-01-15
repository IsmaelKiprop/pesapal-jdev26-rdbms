"""
URL configuration for the app.

This module defines the URL patterns for the web demo API endpoints.
"""
from django.urls import path
from . import views

urlpatterns = [
    # Home page
    path('', views.home, name='home'),
    
    # User endpoints
    path('api/users/', views.api_users, name='api_users'),
    path('api/users/create/', views.api_create_user, name='api_create_user'),
    
    # Todo endpoints
    path('api/todos/', views.api_todos, name='api_todos'),
    path('api/todos/create/', views.api_create_todo, name='api_create_todo'),
    path('api/todos/<int:todo_id>/update/', views.api_update_todo, name='api_update_todo'),
    path('api/todos/<int:todo_id>/delete/', views.api_delete_todo, name='api_delete_todo'),
    
    # Demo endpoints
    path('api/join-demo/', views.api_join_demo, name='api_join_demo'),
    path('api/stats/', views.api_stats, name='api_stats'),
]
