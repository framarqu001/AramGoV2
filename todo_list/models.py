from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import os


class TaskCategory(models.Model):
    """Model for task categories"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    color = models.CharField(max_length=7, default="#007bff")  # Hex color code
    icon = models.CharField(max_length=50, blank=True, null=True)  # Icon class (e.g., Font Awesome)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='task_categories')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Task Categories"
        ordering = ['name']
        unique_together = ['name', 'user']

    def __str__(self):
        return self.name
    
    def task_count(self):
        return self.tasks.count()


class TaskTag(models.Model):
    """Model for task tags"""
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=7, default="#6c757d")  # Hex color code
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='task_tags')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        unique_together = ['name', 'user']

    def __str__(self):
        return self.name


class Task(models.Model):
    """Model for tasks"""
    # Status choices
    STATUS_TODO = 'todo'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_COMPLETED = 'completed'
    STATUS_DEFERRED = 'deferred'
    STATUS_CANCELLED = 'cancelled'
    
    STATUS_CHOICES = [
        (STATUS_TODO, 'To Do'),
        (STATUS_IN_PROGRESS, 'In Progress'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_DEFERRED, 'Deferred'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]
    
    # Priority choices
    PRIORITY_LOW = 'low'
    PRIORITY_MEDIUM = 'medium'
    PRIORITY_HIGH = 'high'
    PRIORITY_URGENT = 'urgent'
    
    PRIORITY_CHOICES = [
        (PRIORITY_LOW, 'Low'),
        (PRIORITY_MEDIUM, 'Medium'),
        (PRIORITY_HIGH, 'High'),
        (PRIORITY_URGENT, 'Urgent'),
    ]
    
    # Recurrence choices
    RECURRENCE_NONE = 'none'
    RECURRENCE_DAILY = 'daily'
    RECURRENCE_WEEKLY = 'weekly'
    RECURRENCE_BIWEEKLY = 'biweekly'
    RECURRENCE_MONTHLY = 'monthly'
    RECURRENCE_YEARLY = 'yearly'
    
    RECURRENCE_CHOICES = [
        (RECURRENCE_NONE, 'None'),
        (RECURRENCE_DAILY, 'Daily'),
        (RECURRENCE_WEEKLY, 'Weekly'),
        (RECURRENCE_BIWEEKLY, 'Bi-weekly'),
        (RECURRENCE_MONTHLY, 'Monthly'),
        (RECURRENCE_YEARLY, 'Yearly'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    category = models.ForeignKey(TaskCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks')
    tags = models.ManyToManyField(TaskTag, blank=True, related_name='tasks')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_TODO)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default=PRIORITY_MEDIUM)
    
    # Dates
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    due_date = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Recurrence
    is_recurring = models.BooleanField(default=False)
    recurrence_pattern = models.CharField(max_length=10, choices=RECURRENCE_CHOICES, default=RECURRENCE_NONE)
    recurrence_end_date = models.DateField(null=True, blank=True)
    
    # Task relationships
    parent_task = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subtasks')
    depends_on = models.ManyToManyField('self', symmetrical=False, blank=True, related_name='dependent_tasks')
    
    # Sharing
    shared_with = models.ManyToManyField(User, blank=True, related_name='shared_tasks')
    
    # Time tracking
    estimated_time = models.PositiveIntegerField(null=True, blank=True, help_text="Estimated time in minutes")
    actual_time = models.PositiveIntegerField(null=True, blank=True, help_text="Actual time spent in minutes")
    
    # Ordering
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order', 'due_date', '-priority', 'created_at']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        # If task is marked as completed, set completed_at
        if self.status == self.STATUS_COMPLETED and not self.completed_at:
            self.completed_at = timezone.now()
        # If task is unmarked as completed, clear completed_at
        elif self.status != self.STATUS_COMPLETED and self.completed_at:
            self.completed_at = None
        super().save(*args, **kwargs)
    
    def is_overdue(self):
        if self.due_date and self.status != self.STATUS_COMPLETED:
            return timezone.now() > self.due_date
        return False
    
    def progress(self):
        """Calculate progress based on completed subtasks"""
        subtasks = self.subtasks.all()
        if not subtasks:
            return 100 if self.status == self.STATUS_COMPLETED else 0
        
        completed = subtasks.filter(status=self.STATUS_COMPLETED).count()
        return int((completed / subtasks.count()) * 100)
    
    def create_next_recurring_task(self):
        """Create the next instance of a recurring task"""
        if not self.is_recurring or self.recurrence_pattern == self.RECURRENCE_NONE:
            return None
        
        # Only create next recurring task if this one is completed
        if self.status != self.STATUS_COMPLETED:
            return None
            
        # Check if recurrence has ended
        if self.recurrence_end_date and timezone.now().date() > self.recurrence_end_date:
            return None
            
        # Calculate next due date based on recurrence pattern
        if not self.due_date:
            next_due = timezone.now()
        else:
            next_due = self.due_date
            
        if self.recurrence_pattern == self.RECURRENCE_DAILY:
            next_due = next_due + timezone.timedelta(days=1)
        elif self.recurrence_pattern == self.RECURRENCE_WEEKLY:
            next_due = next_due + timezone.timedelta(weeks=1)
        elif self.recurrence_pattern == self.RECURRENCE_BIWEEKLY:
            next_due = next_due + timezone.timedelta(weeks=2)
        elif self.recurrence_pattern == self.RECURRENCE_MONTHLY:
            # Add a month (approximately)
            if next_due.month == 12:
                next_due = next_due.replace(year=next_due.year + 1, month=1)
            else:
                next_due = next_due.replace(month=next_due.month + 1)
        elif self.recurrence_pattern == self.RECURRENCE_YEARLY:
            next_due = next_due.replace(year=next_due.year + 1)
            
        # Create new task
        new_task = Task.objects.create(
            title=self.title,
            description=self.description,
            user=self.user,
            category=self.category,
            status=self.STATUS_TODO,
            priority=self.priority,
            due_date=next_due,
            is_recurring=self.is_recurring,
            recurrence_pattern=self.recurrence_pattern,
            recurrence_end_date=self.recurrence_end_date,
            estimated_time=self.estimated_time,
            order=self.order
        )
        
        # Copy tags
        new_task.tags.set(self.tags.all())
        
        # Copy shared users
        new_task.shared_with.set(self.shared_with.all())
        
        return new_task


class SubTask(models.Model):
    """Model for subtasks"""
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='sub_tasks')
    title = models.CharField(max_length=200)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order', 'created_at']
    
    def __str__(self):
        return self.title


def task_attachment_path(instance, filename):
    """Generate file path for task attachments"""
    # File will be uploaded to MEDIA_ROOT/task_attachments/user_<id>/<task_id>/<filename>
    return f'task_attachments/user_{instance.task.user.id}/{instance.task.id}/{filename}'


class TaskAttachment(models.Model):
    """Model for task attachments"""
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to=task_attachment_path)
    filename = models.CharField(max_length=255)
    file_type = models.CharField(max_length=100, blank=True)
    file_size = models.PositiveIntegerField(help_text="File size in bytes")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.filename
    
    def save(self, *args, **kwargs):
        if not self.filename:
            self.filename = os.path.basename(self.file.name)
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        # Delete the file when the model instance is deleted
        storage, path = self.file.storage, self.file.path
        super().delete(*args, **kwargs)
        storage.delete(path)


class TaskComment(models.Model):
    """Model for task comments"""
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='task_comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Comment by {self.user.username} on {self.task.title}"


class TaskNotification(models.Model):
    """Model for task notifications"""
    NOTIFICATION_TYPE_DUE_SOON = 'due_soon'
    NOTIFICATION_TYPE_OVERDUE = 'overdue'
    NOTIFICATION_TYPE_ASSIGNED = 'assigned'
    NOTIFICATION_TYPE_COMMENTED = 'commented'
    NOTIFICATION_TYPE_STATUS_CHANGED = 'status_changed'
    
    NOTIFICATION_TYPE_CHOICES = [
        (NOTIFICATION_TYPE_DUE_SOON, 'Due Soon'),
        (NOTIFICATION_TYPE_OVERDUE, 'Overdue'),
        (NOTIFICATION_TYPE_ASSIGNED, 'Assigned'),
        (NOTIFICATION_TYPE_COMMENTED, 'Commented'),
        (NOTIFICATION_TYPE_STATUS_CHANGED, 'Status Changed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='task_notifications')
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPE_CHOICES)
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.notification_type} notification for {self.user.username}"


class TimeLog(models.Model):
    """Model for tracking time spent on tasks"""
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='time_logs')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='time_logs')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    duration = models.PositiveIntegerField(null=True, blank=True, help_text="Duration in minutes")
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-start_time']
    
    def __str__(self):
        return f"Time log for {self.task.title}"
    
    def save(self, *args, **kwargs):
        # Calculate duration if start and end times are provided
        if self.start_time and self.end_time and not self.duration:
            delta = self.end_time - self.start_time
            self.duration = int(delta.total_seconds() / 60)
        super().save(*args, **kwargs)
        
        # Update task's actual time
        if self.duration:
            total_time = self.task.time_logs.exclude(duration=None).aggregate(
                total=models.Sum('duration'))['total'] or 0
            self.task.actual_time = total_time
            self.task.save(update_fields=['actual_time'])