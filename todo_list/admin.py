from django.contrib import admin
from .models import Todo


@admin.register(Todo)
class TodoAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_date', 'due_date', 'completed', 'user')
    list_filter = ('completed', 'created_date', 'due_date', 'user')
    search_fields = ('title', 'description')
    date_hierarchy = 'created_date'