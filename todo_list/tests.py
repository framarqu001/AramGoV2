from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone

from .models import (
    TaskCategory, TaskTag, Task, SubTask, 
    TaskAttachment, TaskComment, TaskNotification
)

import json
from datetime import timedelta


class TaskModelTests(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
        # Create a test category
        self.category = TaskCategory.objects.create(
            name='Test Category',
            description='Test category description',
            color='#007bff',
            user=self.user
        )
        
        # Create a test tag
        self.tag = TaskTag.objects.create(
            name='Test Tag',
            color='#6c757d',
            user=self.user
        )
        
        # Create a test task
        self.task = Task.objects.create(
            title='Test Task',
            description='Test task description',
            user=self.user,
            category=self.category,
            status=Task.STATUS_TODO,
            priority=Task.PRIORITY_MEDIUM,
            due_date=timezone.now() + timedelta(days=1)
        )
        self.task.tags.add(self.tag)
        
        # Create test subtasks
        self.subtask1 = SubTask.objects.create(
            task=self.task,
            title='Test Subtask 1',
            is_completed=False,
            order=0
        )
        
        self.subtask2 = SubTask.objects.create(
            task=self.task,
            title='Test Subtask 2',
            is_completed=True,
            order=1
        )
    
    def test_task_creation(self):
        """Test that a task can be created with proper attributes"""
        self.assertEqual(self.task.title, 'Test Task')
        self.assertEqual(self.task.description, 'Test task description')
        self.assertEqual(self.task.user, self.user)
        self.assertEqual(self.task.category, self.category)
        self.assertEqual(self.task.status, Task.STATUS_TODO)
        self.assertEqual(self.task.priority, Task.PRIORITY_MEDIUM)
        self.assertFalse(self.task.is_recurring)
        self.assertIsNotNone(self.task.due_date)
    
    def test_task_str_representation(self):
        """Test the string representation of a task"""
        self.assertEqual(str(self.task), 'Test Task')
    
    def test_task_progress(self):
        """Test the progress calculation of a task"""
        # 1 out of 2 subtasks completed = 50% progress
        self.assertEqual(self.task.progress(), 50)
        
        # Mark all subtasks as completed
        self.subtask1.is_completed = True
        self.subtask1.save()
        
        # 2 out of 2 subtasks completed = 100% progress
        self.assertEqual(self.task.progress(), 100)
        
        # Delete all subtasks and check progress
        SubTask.objects.filter(task=self.task).delete()
        
        # No subtasks, task not completed = 0% progress
        self.assertEqual(self.task.progress(), 0)
        
        # Mark task as completed
        self.task.status = Task.STATUS_COMPLETED
        self.task.save()
        
        # No subtasks, task completed = 100% progress
        self.assertEqual(self.task.progress(), 100)
    
    def test_task_is_overdue(self):
        """Test the is_overdue method of a task"""
        # Task is not overdue
        self.assertFalse(self.task.is_overdue())
        
        # Set due date to yesterday
        self.task.due_date = timezone.now() - timedelta(days=1)
        self.task.save()
        
        # Task is now overdue
        self.assertTrue(self.task.is_overdue())
        
        # Mark task as completed
        self.task.status = Task.STATUS_COMPLETED
        self.task.save()
        
        # Completed tasks are not overdue
        self.assertFalse(self.task.is_overdue())
    
    def test_recurring_task_creation(self):
        """Test the creation of recurring tasks"""
        # Set task as recurring
        self.task.is_recurring = True
        self.task.recurrence_pattern = Task.RECURRENCE_WEEKLY
        self.task.save()
        
        # Mark task as completed
        self.task.status = Task.STATUS_COMPLETED
        self.task.save()
        
        # Create next recurring task
        next_task = self.task.create_next_recurring_task()
        
        # Check that next task was created with correct attributes
        self.assertIsNotNone(next_task)
        self.assertEqual(next_task.title, self.task.title)
        self.assertEqual(next_task.description, self.task.description)
        self.assertEqual(next_task.user, self.task.user)
        self.assertEqual(next_task.category, self.task.category)
        self.assertEqual(next_task.status, Task.STATUS_TODO)
        self.assertEqual(next_task.priority, self.task.priority)
        self.assertEqual(next_task.is_recurring, True)
        self.assertEqual(next_task.recurrence_pattern, Task.RECURRENCE_WEEKLY)
        
        # Due date should be one week later
        due_date_diff = next_task.due_date - self.task.due_date
        self.assertEqual(due_date_diff.days, 7)


class TaskViewTests(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
        # Create a test client
        self.client = Client()
        
        # Create a test category
        self.category = TaskCategory.objects.create(
            name='Test Category',
            description='Test category description',
            color='#007bff',
            user=self.user
        )
        
        # Create a test task
        self.task = Task.objects.create(
            title='Test Task',
            description='Test task description',
            user=self.user,
            category=self.category,
            status=Task.STATUS_TODO,
            priority=Task.PRIORITY_MEDIUM,
            due_date=timezone.now() + timedelta(days=1)
        )
    
    def test_dashboard_view_requires_login(self):
        """Test that the dashboard view requires login"""
        response = self.client.get(reverse('todo_list:dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect to login page
    
    def test_dashboard_view_with_login(self):
        """Test that the dashboard view works with login"""
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('todo_list:dashboard'))
        self.assertEqual(response.status_code, 200)
    
    def test_task_list_view(self):
        """Test the task list view"""
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('todo_list:task_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Task')
    
    def test_task_detail_view(self):
        """Test the task detail view"""
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('todo_list:task_detail', args=[self.task.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Task')
        self.assertContains(response, 'Test task description')
    
    def test_task_create_view(self):
        """Test the task create view"""
        self.client.login(username='testuser', password='testpassword')
        
        # Get the create form
        response = self.client.get(reverse('todo_list:task_create'))
        self.assertEqual(response.status_code, 200)
        
        # Submit the form
        task_data = {
            'title': 'New Test Task',
            'description': 'New test task description',
            'category': self.category.pk,
            'status': Task.STATUS_TODO,
            'priority': Task.PRIORITY_HIGH,
        }
        response = self.client.post(reverse('todo_list:task_create'), task_data)
        
        # Check that the task was created
        self.assertEqual(Task.objects.filter(title='New Test Task').count(), 1)
    
    def test_task_update_view(self):
        """Test the task update view"""
        self.client.login(username='testuser', password='testpassword')
        
        # Get the update form
        response = self.client.get(reverse('todo_list:task_update', args=[self.task.pk]))
        self.assertEqual(response.status_code, 200)
        
        # Submit the form
        task_data = {
            'title': 'Updated Test Task',
            'description': 'Updated test task description',
            'category': self.category.pk,
            'status': Task.STATUS_IN_PROGRESS,
            'priority': Task.PRIORITY_HIGH,
        }
        response = self.client.post(reverse('todo_list:task_update', args=[self.task.pk]), task_data)
        
        # Check that the task was updated
        self.task.refresh_from_db()
        self.assertEqual(self.task.title, 'Updated Test Task')
        self.assertEqual(self.task.status, Task.STATUS_IN_PROGRESS)
    
    def test_task_delete_view(self):
        """Test the task delete view"""
        self.client.login(username='testuser', password='testpassword')
        
        # Get the delete confirmation page
        response = self.client.get(reverse('todo_list:task_delete', args=[self.task.pk]))
        self.assertEqual(response.status_code, 200)
        
        # Submit the delete form
        response = self.client.post(reverse('todo_list:task_delete', args=[self.task.pk]))
        
        # Check that the task was deleted
        self.assertEqual(Task.objects.filter(pk=self.task.pk).count(), 0)