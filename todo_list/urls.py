from django.urls import path
from . import views

app_name = 'todo_list'

urlpatterns = [
    path('', views.todo_home, name='home'),
    path('list/', views.TodoListView.as_view(), name='list'),
    path('detail/<int:pk>/', views.TodoDetailView.as_view(), name='detail'),
    path('create/', views.TodoCreateView.as_view(), name='create'),
    path('update/<int:pk>/', views.TodoUpdateView.as_view(), name='update'),
    path('delete/<int:pk>/', views.TodoDeleteView.as_view(), name='delete'),
    path('toggle/<int:pk>/', views.toggle_complete, name='toggle'),
]