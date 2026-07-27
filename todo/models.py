from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Category(models.Model):
    """Model for categorizing todo items"""
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=20, default="#3498db")  # Hex color code
    icon = models.CharField(max_length=50, blank=True, null=True)  # Font awesome icon name
    
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Tag(models.Model):
    """Model for tagging todo items"""
    name = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return self.name


class TodoItem(models.Model):
    """Main model for todo items"""
    PRIORITY_CHOICES = [
        (1, 'Low'),
        (2, 'Medium'),
        (3, 'High'),
        (4, 'Urgent'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('deferred', 'Deferred'),
        ('cancelled', 'Cancelled'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    due_date = models.DateTimeField(blank=True, null=True)
    completed_date = models.DateTimeField(blank=True, null=True)
    priority = models.IntegerField(choices=PRIORITY_CHOICES, default=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Relationships
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='todo_items')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='todo_items')
    tags = models.ManyToManyField(Tag, blank=True, related_name='todo_items')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subtasks')
    
    # Additional features
    is_recurring = models.BooleanField(default=False)
    recurrence_pattern = models.CharField(max_length=50, blank=True, null=True)  # e.g., "daily", "weekly", "monthly"
    reminder_datetime = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-priority', 'due_date', 'created_date']
    
    def __str__(self):
        return self.title
    
    def mark_completed(self):
        """Mark the todo item as completed"""
        self.status = 'completed'
        self.completed_date = timezone.now()
        self.save()
    
    def is_overdue(self):
        """Check if the todo item is overdue"""
        if self.due_date and self.status != 'completed':
            return self.due_date < timezone.now()
        return False
    
    def days_until_due(self):
        """Calculate days until due date"""
        if self.due_date:
            delta = self.due_date - timezone.now()
            return delta.days
        return None


class Attachment(models.Model):
    """Model for file attachments to todo items"""
    todo_item = models.ForeignKey(TodoItem, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='todo_attachments/')
    filename = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.filename


class Comment(models.Model):
    """Model for comments on todo items"""
    todo_item = models.ForeignKey(TodoItem, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Comment by {self.user.username} on {self.todo_item.title}"