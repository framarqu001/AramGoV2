from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden
from django.db.models import Q, Count, Sum
from django.utils import timezone
from django.contrib import messages
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from django.urls import reverse

from .models import (
    TaskCategory, TaskTag, Task, SubTask, 
    TaskAttachment, TaskComment, TaskNotification, TimeLog
)
from .forms import (
    TaskCategoryForm, TaskTagForm, TaskForm, SubTaskForm, 
    TaskAttachmentForm, TaskCommentForm, TimeLogForm, TaskFilterForm,
    SubTaskInlineFormSet
)

import json
from datetime import timedelta


@login_required
def dashboard(request):
    """Dashboard view showing task statistics and overview"""
    user = request.user
    
    # Get task counts by status
    status_counts = Task.objects.filter(user=user).values('status').annotate(count=Count('status'))
    status_data = {item['status']: item['count'] for item in status_counts}
    
    # Get overdue tasks
    overdue_tasks = Task.objects.filter(
        user=user,
        due_date__lt=timezone.now(),
        status__in=[Task.STATUS_TODO, Task.STATUS_IN_PROGRESS]
    ).order_by('due_date')[:5]
    
    # Get upcoming tasks (due in the next 7 days)
    upcoming_tasks = Task.objects.filter(
        user=user,
        due_date__gte=timezone.now(),
        due_date__lte=timezone.now() + timedelta(days=7),
        status__in=[Task.STATUS_TODO, Task.STATUS_IN_PROGRESS]
    ).order_by('due_date')[:5]
    
    # Get recently completed tasks
    completed_tasks = Task.objects.filter(
        user=user,
        status=Task.STATUS_COMPLETED,
        completed_at__gte=timezone.now() - timedelta(days=7)
    ).order_by('-completed_at')[:5]
    
    context = {
        'status_data': status_data,
        'overdue_tasks': overdue_tasks,
        'upcoming_tasks': upcoming_tasks,
        'completed_tasks': completed_tasks,
        'total_tasks': Task.objects.filter(user=user).count(),
        'total_completed': Task.objects.filter(user=user, status=Task.STATUS_COMPLETED).count(),
    }
    
    return render(request, 'todo_list/dashboard.html', context)


@login_required
def task_list(request):
    """View for listing tasks with filtering options"""
    user = request.user
    
    # Initialize the filter form with user's categories and tags
    filter_form = TaskFilterForm(user=user, data=request.GET or None)
    
    # Start with all user's tasks
    tasks = Task.objects.filter(user=user)
    
    # Apply filters if form is valid
    if filter_form.is_valid():
        data = filter_form.cleaned_data
        
        if data.get('status'):
            tasks = tasks.filter(status=data['status'])
        
        if data.get('priority'):
            tasks = tasks.filter(priority=data['priority'])
        
        if data.get('category'):
            tasks = tasks.filter(category=data['category'])
        
        if data.get('tags'):
            for tag in data['tags']:
                tasks = tasks.filter(tags=tag)
        
        if data.get('due_date_start'):
            tasks = tasks.filter(due_date__gte=data['due_date_start'])
        
        if data.get('due_date_end'):
            tasks = tasks.filter(due_date__lte=data['due_date_end'])
        
        if data.get('search'):
            search_query = data['search']
            tasks = tasks.filter(
                Q(title__icontains=search_query) | 
                Q(description__icontains=search_query)
            )
    
    # Default ordering
    tasks = tasks.order_by('order', 'due_date', '-priority', 'created_at')
    
    # Pagination
    paginator = Paginator(tasks, 10)  # Show 10 tasks per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'tasks': page_obj,
        'filter_form': filter_form,
    }
    
    return render(request, 'todo_list/task_list.html', context)


@login_required
def task_detail(request, pk):
    """View for displaying task details"""
    task = get_object_or_404(Task, pk=pk)
    
    # Check if user has permission to view this task
    if task.user != request.user and request.user not in task.shared_with.all():
        return HttpResponseForbidden("You don't have permission to view this task.")
    
    # Get subtasks
    subtasks = task.sub_tasks.all().order_by('order', 'created_at')
    
    # Get attachments
    attachments = task.attachments.all().order_by('-uploaded_at')
    
    # Get comments
    comments = task.comments.all().order_by('-created_at')
    
    # Get time logs
    time_logs = task.time_logs.all().order_by('-start_time')
    total_time = time_logs.aggregate(total=Sum('duration'))['total'] or 0
    
    # Forms
    comment_form = TaskCommentForm()
    attachment_form = TaskAttachmentForm()
    time_log_form = TimeLogForm()
    
    context = {
        'task': task,
        'subtasks': subtasks,
        'attachments': attachments,
        'comments': comments,
        'time_logs': time_logs,
        'total_time': total_time,
        'comment_form': comment_form,
        'attachment_form': attachment_form,
        'time_log_form': time_log_form,
    }
    
    return render(request, 'todo_list/task_detail.html', context)


@login_required
def task_create(request):
    """View for creating a new task"""
    if request.method == 'POST':
        form = TaskForm(request.user, request.POST)
        formset = SubTaskInlineFormSet(request.POST, prefix='subtasks')
        
        if form.is_valid() and formset.is_valid():
            # Save the task
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            form.save_m2m()  # Save many-to-many relationships
            
            # Save subtasks
            formset.instance = task
            formset.save()
            
            messages.success(request, 'Task created successfully!')
            return redirect('todo_list:task_detail', pk=task.pk)
    else:
        form = TaskForm(request.user)
        formset = SubTaskInlineFormSet(prefix='subtasks')
    
    context = {
        'form': form,
        'formset': formset,
        'title': 'Create Task',
    }
    
    return render(request, 'todo_list/task_form.html', context)


@login_required
def task_update(request, pk):
    """View for updating an existing task"""
    task = get_object_or_404(Task, pk=pk)
    
    # Check if user has permission to edit this task
    if task.user != request.user:
        return HttpResponseForbidden("You don't have permission to edit this task.")
    
    if request.method == 'POST':
        form = TaskForm(request.user, request.POST, instance=task)
        formset = SubTaskInlineFormSet(request.POST, instance=task, prefix='subtasks')
        
        if form.is_valid() and formset.is_valid():
            # Save the task
            task = form.save()
            
            # Save subtasks
            formset.save()
            
            messages.success(request, 'Task updated successfully!')
            return redirect('todo_list:task_detail', pk=task.pk)
    else:
        form = TaskForm(request.user, instance=task)
        formset = SubTaskInlineFormSet(instance=task, prefix='subtasks')
    
    context = {
        'form': form,
        'formset': formset,
        'task': task,
        'title': 'Update Task',
    }
    
    return render(request, 'todo_list/task_form.html', context)


@login_required
def task_delete(request, pk):
    """View for deleting a task"""
    task = get_object_or_404(Task, pk=pk)
    
    # Check if user has permission to delete this task
    if task.user != request.user:
        return HttpResponseForbidden("You don't have permission to delete this task.")
    
    if request.method == 'POST':
        task.delete()
        messages.success(request, 'Task deleted successfully!')
        return redirect('todo_list:task_list')
    
    context = {
        'task': task,
    }
    
    return render(request, 'todo_list/task_confirm_delete.html', context)


@login_required
@require_POST
def task_status_update(request, pk):
    """AJAX view for updating task status"""
    task = get_object_or_404(Task, pk=pk)
    
    # Check if user has permission to update this task
    if task.user != request.user and request.user not in task.shared_with.all():
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    status = request.POST.get('status')
    if status and status in dict(Task.STATUS_CHOICES):
        old_status = task.status
        task.status = status
        task.save()
        
        # If task is recurring and was marked as completed, create next instance
        if status == Task.STATUS_COMPLETED and old_status != Task.STATUS_COMPLETED and task.is_recurring:
            next_task = task.create_next_recurring_task()
            if next_task:
                return JsonResponse({
                    'success': True, 
                    'message': 'Task marked as completed. Next recurring task created.',
                    'next_task_id': next_task.id
                })
        
        return JsonResponse({'success': True})
    
    return JsonResponse({'error': 'Invalid status'}, status=400)


@login_required
@require_POST
def subtask_toggle(request, pk):
    """AJAX view for toggling subtask completion"""
    subtask = get_object_or_404(SubTask, pk=pk)
    
    # Check if user has permission to update this subtask
    if subtask.task.user != request.user and request.user not in subtask.task.shared_with.all():
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    subtask.is_completed = not subtask.is_completed
    subtask.save()
    
    # Calculate and return the task progress
    progress = subtask.task.progress()
    
    return JsonResponse({
        'success': True, 
        'is_completed': subtask.is_completed,
        'progress': progress
    })


@login_required
@require_POST
def add_attachment(request, pk):
    """View for adding an attachment to a task"""
    task = get_object_or_404(Task, pk=pk)
    
    # Check if user has permission to add attachments to this task
    if task.user != request.user and request.user not in task.shared_with.all():
        return HttpResponseForbidden("You don't have permission to add attachments to this task.")
    
    form = TaskAttachmentForm(request.POST, request.FILES)
    if form.is_valid():
        attachment = form.save(commit=False)
        attachment.task = task
        attachment.file_size = attachment.file.size
        attachment.file_type = attachment.file.content_type
        attachment.save()
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'attachment_id': attachment.id,
                'attachment_name': attachment.filename,
                'attachment_size': attachment.file_size,
                'attachment_type': attachment.file_type,
                'attachment_date': attachment.uploaded_at.strftime('%b %d, %Y, %I:%M %p')
            })
        
        messages.success(request, 'Attachment added successfully!')
        return redirect('todo_list:task_detail', pk=task.pk)
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'error': 'Invalid form data'}, status=400)
    
    messages.error(request, 'Error adding attachment. Please try again.')
    return redirect('todo_list:task_detail', pk=task.pk)


@login_required
def delete_attachment(request, pk):
    """View for deleting an attachment"""
    attachment = get_object_or_404(TaskAttachment, pk=pk)
    task_id = attachment.task.id
    
    # Check if user has permission to delete this attachment
    if attachment.task.user != request.user:
        return HttpResponseForbidden("You don't have permission to delete this attachment.")
    
    if request.method == 'POST':
        attachment.delete()
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
        
        messages.success(request, 'Attachment deleted successfully!')
        return redirect('todo_list:task_detail', pk=task_id)
    
    context = {
        'attachment': attachment,
    }
    
    return render(request, 'todo_list/attachment_confirm_delete.html', context)


@login_required
@require_POST
def add_time_log(request, pk):
    """View for adding a time log to a task"""
    task = get_object_or_404(Task, pk=pk)
    
    # Check if user has permission to add time logs to this task
    if task.user != request.user and request.user not in task.shared_with.all():
        return HttpResponseForbidden("You don't have permission to add time logs to this task.")
    
    form = TimeLogForm(request.POST)
    if form.is_valid():
        time_log = form.save(commit=False)
        time_log.task = task
        time_log.user = request.user
        time_log.save()
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'time_log_id': time_log.id,
                'time_log_start': time_log.start_time.strftime('%b %d, %Y, %I:%M %p'),
                'time_log_end': time_log.end_time.strftime('%b %d, %Y, %I:%M %p') if time_log.end_time else '',
                'time_log_duration': time_log.duration or 0,
                'time_log_notes': time_log.notes or '',
                'total_time': task.actual_time or 0
            })
        
        messages.success(request, 'Time log added successfully!')
        return redirect('todo_list:task_detail', pk=task.pk)
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'error': 'Invalid form data'}, status=400)
    
    messages.error(request, 'Error adding time log. Please try again.')
    return redirect('todo_list:task_detail', pk=task.pk)


@login_required
def category_list(request):
    """View for listing task categories"""
    categories = TaskCategory.objects.filter(user=request.user).order_by('name')
    
    context = {
        'categories': categories,
    }
    
    return render(request, 'todo_list/category_list.html', context)


@login_required
def category_create(request):
    """View for creating a new task category"""
    if request.method == 'POST':
        form = TaskCategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.user = request.user
            category.save()
            
            messages.success(request, 'Category created successfully!')
            return redirect('todo_list:category_list')
    else:
        form = TaskCategoryForm()
    
    context = {
        'form': form,
        'title': 'Create Category',
    }
    
    return render(request, 'todo_list/category_form.html', context)


@login_required
def category_delete(request, pk):
    """View for deleting a task category"""
    category = get_object_or_404(TaskCategory, pk=pk, user=request.user)
    
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Category deleted successfully!')
        return redirect('todo_list:category_list')
    
    context = {
        'category': category,
    }
    
    return render(request, 'todo_list/category_confirm_delete.html', context)


@login_required
def tag_list(request):
    """View for listing task tags"""
    tags = TaskTag.objects.filter(user=request.user).order_by('name')
    
    context = {
        'tags': tags,
    }
    
    return render(request, 'todo_list/tag_list.html', context)


@login_required
def tag_create(request):
    """View for creating a new task tag"""
    if request.method == 'POST':
        form = TaskTagForm(request.POST)
        if form.is_valid():
            tag = form.save(commit=False)
            tag.user = request.user
            tag.save()
            
            messages.success(request, 'Tag created successfully!')
            return redirect('todo_list:tag_list')
    else:
        form = TaskTagForm()
    
    context = {
        'form': form,
        'title': 'Create Tag',
    }
    
    return render(request, 'todo_list/tag_form.html', context)


@login_required
def tag_update(request, pk):
    """View for updating an existing task tag"""
    tag = get_object_or_404(TaskTag, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = TaskTagForm(request.POST, instance=tag)
        if form.is_valid():
            form.save()
            
            messages.success(request, 'Tag updated successfully!')
            return redirect('todo_list:tag_list')
    else:
        form = TaskTagForm(instance=tag)
    
    context = {
        'form': form,
        'tag': tag,
        'title': 'Update Tag',
    }
    
    return render(request, 'todo_list/tag_form.html', context)


@login_required
def tag_delete(request, pk):
    """View for deleting a task tag"""
    tag = get_object_or_404(TaskTag, pk=pk, user=request.user)
    
    if request.method == 'POST':
        tag.delete()
        messages.success(request, 'Tag deleted successfully!')
        return redirect('todo_list:tag_list')
    
    context = {
        'tag': tag,
    }
    
    return render(request, 'todo_list/tag_confirm_delete.html', context)


@login_required
def notifications(request):
    """View for listing user notifications"""
    notifications = TaskNotification.objects.filter(user=request.user).order_by('-created_at')
    
    # Pagination
    paginator = Paginator(notifications, 20)  # Show 20 notifications per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'notifications': page_obj,
    }
    
    return render(request, 'todo_list/notifications.html', context)


@login_required
@require_POST
def mark_notification_read(request, pk):
    """AJAX view for marking a notification as read"""
    notification = get_object_or_404(TaskNotification, pk=pk, user=request.user)
    
    notification.is_read = True
    notification.save()
    
    return JsonResponse({'success': True})


@login_required
@require_POST
def mark_all_notifications_read(request):
    """AJAX view for marking all notifications as read"""
    TaskNotification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    
    return JsonResponse({'success': True})


@login_required
def task_reorder(request):
    """AJAX view for reordering tasks"""
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            data = json.loads(request.body)
            task_ids = data.get('task_ids', [])
            
            # Update task order
            for index, task_id in enumerate(task_ids):
                Task.objects.filter(pk=task_id, user=request.user).update(order=index)
            
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def subtask_reorder(request, task_pk):
    """AJAX view for reordering subtasks"""
    task = get_object_or_404(Task, pk=task_pk, user=request.user)
    
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            data = json.loads(request.body)
            subtask_ids = data.get('subtask_ids', [])
            
            # Update subtask order
            for index, subtask_id in enumerate(subtask_ids):
                SubTask.objects.filter(pk=subtask_id, task=task).update(order=index)
            
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
@require_POST
def add_comment(request, pk):
    """View for adding a comment to a task"""
    task = get_object_or_404(Task, pk=pk)
    
    # Check if user has permission to comment on this task
    if task.user != request.user and request.user not in task.shared_with.all():
        return HttpResponseForbidden("You don't have permission to comment on this task.")
    
    form = TaskCommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.task = task
        comment.user = request.user
        comment.save()
        
        # Create notification for task owner if commenter is not the owner
        if request.user != task.user:
            TaskNotification.objects.create(
                user=task.user,
                task=task,
                notification_type=TaskNotification.NOTIFICATION_TYPE_COMMENTED,
                message=f"{request.user.username} commented on your task: {task.title}"
            )
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'comment_id': comment.id,
                'comment_content': comment.content,
                'comment_user': comment.user.username,
                'comment_date': comment.created_at.strftime('%b %d, %Y, %I:%M %p')
            })
        
        messages.success(request, 'Comment added successfully!')
        return redirect('todo_list:task_detail', pk=task.pk)
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'error': 'Invalid form data'}, status=400)
    
    messages.error(request, 'Error adding comment. Please try again.')
    return redirect('todo_list:task_detail', pk=task.pk)