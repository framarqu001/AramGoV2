from django.urls import path
from . import views

app_name = 'todo_list'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Tasks
    path('tasks/', views.task_list, name='task_list'),
    path('tasks/create/', views.task_create, name='task_create'),
    path('tasks/<int:pk>/', views.task_detail, name='task_detail'),
    path('tasks/<int:pk>/update/', views.task_update, name='task_update'),
    path('tasks/<int:pk>/delete/', views.task_delete, name='task_delete'),
    path('tasks/<int:pk>/status/', views.task_status_update, name='task_status_update'),
    path('tasks/reorder/', views.task_reorder, name='task_reorder'),
    
    # Subtasks
    path('subtasks/<int:pk>/toggle/', views.subtask_toggle, name='subtask_toggle'),
    path('tasks/<int:task_pk>/subtasks/reorder/', views.subtask_reorder, name='subtask_reorder'),
    
    # Comments
    path('tasks/<int:pk>/comments/add/', views.add_comment, name='add_comment'),
    
    # Attachments
    path('tasks/<int:pk>/attachments/add/', views.add_attachment, name='add_attachment'),
    path('attachments/<int:pk>/delete/', views.delete_attachment, name='delete_attachment'),
    
    # Time logs
    path('tasks/<int:pk>/time-logs/add/', views.add_time_log, name='add_time_log'),
    
    # Categories
    path('categories/', views.category_list, name='category_list'),
    path('categories/create/', views.category_create, name='category_create'),
    path('categories/<int:pk>/update/', views.category_update, name='category_update'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),
    
    # Tags
    path('tags/', views.tag_list, name='tag_list'),
    path('tags/create/', views.tag_create, name='tag_create'),
    path('tags/<int:pk>/update/', views.tag_update, name='tag_update'),
    path('tags/<int:pk>/delete/', views.tag_delete, name='tag_delete'),
    
    # Notifications
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/<int:pk>/mark-read/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/mark-all-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
]