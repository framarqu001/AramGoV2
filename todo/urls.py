from django.urls import path
from . import views

app_name = 'todo'

urlpatterns = [
    # Dashboard
    path('', views.DashboardView.as_view(), name='dashboard'),
    
    # Todo item CRUD
    path('list/', views.TodoListView.as_view(), name='list'),
    path('create/', views.TodoCreateView.as_view(), name='create'),
    path('<int:pk>/', views.TodoDetailView.as_view(), name='detail'),
    path('<int:pk>/update/', views.TodoUpdateView.as_view(), name='update'),
    path('<int:pk>/delete/', views.TodoDeleteView.as_view(), name='delete'),
    
    # Todo item actions
    path('<int:pk>/complete/', views.mark_completed, name='complete'),
    path('<int:pk>/toggle-status/', views.toggle_status, name='toggle_status'),
    
    # Comments and attachments
    path('<int:pk>/comment/', views.add_comment, name='add_comment'),
    path('<int:pk>/attachment/', views.add_attachment, name='add_attachment'),
    path('attachment/<int:pk>/delete/', views.delete_attachment, name='delete_attachment'),
    
    # Categories
    path('category/create/', views.CategoryCreateView.as_view(), name='create_category'),
]