from celery import shared_task
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from datetime import timedelta

from .models import TodoItem


@shared_task
def send_due_reminders():
    """
    Send reminder emails for todo items that are due soon
    This task should be scheduled to run periodically
    """
    # Find todo items with reminders set for the next hour
    now = timezone.now()
    one_hour_from_now = now + timedelta(hours=1)
    
    reminder_items = TodoItem.objects.filter(
        reminder_datetime__gte=now,
        reminder_datetime__lte=one_hour_from_now,
        status__in=['pending', 'in_progress']
    )
    
    for item in reminder_items:
        if item.user.email:
            # Send email reminder
            subject = f"Reminder: '{item.title}' is due soon"
            
            # Format the due date
            due_date_str = item.due_date.strftime("%B %d, %Y at %I:%M %p") if item.due_date else "No due date"
            
            # Create message body
            message = f"""
            Hello {item.user.username},
            
            This is a reminder that your task "{item.title}" is due soon.
            
            Due date: {due_date_str}
            Priority: {item.get_priority_display()}
            Status: {item.get_status_display()}
            
            You can view this task at: {settings.BASE_URL}/todo/{item.id}/
            
            Thank you,
            Todo App
            """
            
            # Send the email
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [item.user.email],
                fail_silently=True,
            )
    
    return f"Processed {reminder_items.count()} reminders"


@shared_task
def create_recurring_tasks():
    """
    Create new instances of recurring tasks
    This task should be scheduled to run daily
    """
    now = timezone.now()
    
    # Find completed recurring tasks
    recurring_tasks = TodoItem.objects.filter(
        is_recurring=True,
        status='completed',
        recurrence_pattern__isnull=False
    )
    
    created_count = 0
    
    for task in recurring_tasks:
        # Check if we need to create a new instance based on recurrence pattern
        if task.completed_date:
            create_new = False
            
            if task.recurrence_pattern == 'daily':
                # Create new task if completed more than 20 hours ago
                if now - task.completed_date > timedelta(hours=20):
                    create_new = True
            
            elif task.recurrence_pattern == 'weekly':
                # Create new task if completed more than 6 days ago
                if now - task.completed_date > timedelta(days=6):
                    create_new = True
            
            elif task.recurrence_pattern == 'monthly':
                # Create new task if completed more than 28 days ago
                if now - task.completed_date > timedelta(days=28):
                    create_new = True
            
            elif task.recurrence_pattern == 'yearly':
                # Create new task if completed more than 364 days ago
                if now - task.completed_date > timedelta(days=364):
                    create_new = True
            
            if create_new:
                # Create a new instance of the task
                new_task = TodoItem.objects.create(
                    title=task.title,
                    description=task.description,
                    user=task.user,
                    category=task.category,
                    priority=task.priority,
                    status='pending',
                    is_recurring=True,
                    recurrence_pattern=task.recurrence_pattern,
                    parent=task.parent
                )
                
                # Set due date if the original task had one
                if task.due_date:
                    if task.recurrence_pattern == 'daily':
                        new_task.due_date = now + timedelta(days=1)
                    elif task.recurrence_pattern == 'weekly':
                        new_task.due_date = now + timedelta(days=7)
                    elif task.recurrence_pattern == 'monthly':
                        new_task.due_date = now + timedelta(days=30)
                    elif task.recurrence_pattern == 'yearly':
                        new_task.due_date = now + timedelta(days=365)
                    new_task.save()
                
                # Copy tags
                for tag in task.tags.all():
                    new_task.tags.add(tag)
                
                created_count += 1
    
    return f"Created {created_count} recurring tasks"