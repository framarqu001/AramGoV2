from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class Todo(models.Model):
    """Model representing a to-do item"""
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField(null=True, blank=True)
    completed = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='todos', null=True, blank=True)
    
    class Meta:
        ordering = ['completed', 'due_date', '-created_date']
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('todo_list:detail', args=[str(self.id)])