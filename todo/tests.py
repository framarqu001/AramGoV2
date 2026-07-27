from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

from .models import TodoItem, Category, Tag, Comment, Attachment


class TodoModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )
        
        self.category = Category.objects.create(
            name='Work',
            color='#ff0000'
        )
        
        self.tag = Tag.objects.create(name='Important')
        
        self.todo_item = TodoItem.objects.create(
            title='Test Todo',
            description='This is a test todo item',
            user=self.user,
            category=self.category,
            priority=3,
            due_date=timezone.now() + timedelta(days=1)
        )
        self.todo_item.tags.add(self.tag)
    
    def test_todo_item_creation(self):
        """Test that a todo item can be created with proper attributes"""
        self.assertEqual(self.todo_item.title, 'Test Todo')
        self.assertEqual(self.todo_item.description, 'This is a test todo item')
        self.assertEqual(self.todo_item.user, self.user)
        self.assertEqual(self.todo_item.category, self.category)
        self.assertEqual(self.todo_item.priority, 3)
        self.assertEqual(self.todo_item.status, 'pending')
        self.assertIsNotNone(self.todo_item.due_date)
        self.assertIn(self.tag, self.todo_item.tags.all())
    
    def test_mark_completed(self):
        """Test that a todo item can be marked as completed"""
        self.todo_item.mark_completed()
        self.assertEqual(self.todo_item.status, 'completed')
        self.assertIsNotNone(self.todo_item.completed_date)
    
    def test_is_overdue(self):
        """Test that a todo item can be identified as overdue"""
        # Not overdue
        self.assertFalse(self.todo_item.is_overdue())
        
        # Set due date to yesterday
        self.todo_item.due_date = timezone.now() - timedelta(days=1)
        self.todo_item.save()
        self.assertTrue(self.todo_item.is_overdue())
        
        # Completed items are not overdue
        self.todo_item.mark_completed()
        self.assertFalse(self.todo_item.is_overdue())
    
    def test_days_until_due(self):
        """Test that days until due date is calculated correctly"""
        self.todo_item.due_date = timezone.now() + timedelta(days=5)
        self.todo_item.save()
        self.assertEqual(self.todo_item.days_until_due(), 5)


class TodoViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )
        
        self.category = Category.objects.create(
            name='Work',
            color='#ff0000'
        )
        
        self.todo_item = TodoItem.objects.create(
            title='Test Todo',
            description='This is a test todo item',
            user=self.user,
            category=self.category,
            priority=3,
            due_date=timezone.now() + timedelta(days=1)
        )
        
        # Login the test client
        self.client.login(username='testuser', password='testpassword')
    
    def test_dashboard_view(self):
        """Test that the dashboard view works correctly"""
        response = self.client.get(reverse('todo:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'todo/dashboard.html')
        self.assertContains(response, 'Dashboard')
        self.assertEqual(response.context['pending_count'], 1)
    
    def test_todo_list_view(self):
        """Test that the todo list view works correctly"""
        response = self.client.get(reverse('todo:list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'todo/todo_list.html')
        self.assertContains(response, 'Test Todo')
        self.assertEqual(len(response.context['todo_items']), 1)
    
    def test_todo_detail_view(self):
        """Test that the todo detail view works correctly"""
        response = self.client.get(reverse('todo:detail', args=[self.todo_item.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'todo/todo_detail.html')
        self.assertContains(response, 'Test Todo')
        self.assertContains(response, 'This is a test todo item')
    
    def test_todo_create_view(self):
        """Test that the todo create view works correctly"""
        response = self.client.get(reverse('todo:create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'todo/todo_form.html')
        
        # Test POST request
        todo_count = TodoItem.objects.count()
        response = self.client.post(reverse('todo:create'), {
            'title': 'New Todo',
            'description': 'This is a new todo item',
            'priority': 2,
            'status': 'pending',
            'category': self.category.pk
        })
        
        # Should redirect after successful creation
        self.assertEqual(response.status_code, 302)
        
        # Check that a new todo was created
        self.assertEqual(TodoItem.objects.count(), todo_count + 1)
        new_todo = TodoItem.objects.latest('id')
        self.assertEqual(new_todo.title, 'New Todo')
        self.assertEqual(new_todo.user, self.user)
    
    def test_mark_completed_view(self):
        """Test that a todo item can be marked as completed via the view"""
        response = self.client.get(reverse('todo:complete', args=[self.todo_item.pk]))
        self.assertEqual(response.status_code, 302)  # Should redirect
        
        # Refresh from database
        self.todo_item.refresh_from_db()
        self.assertEqual(self.todo_item.status, 'completed')
        self.assertIsNotNone(self.todo_item.completed_date)
    
    def test_toggle_status_view(self):
        """Test that a todo item status can be toggled via the view"""
        # Initially pending
        self.assertEqual(self.todo_item.status, 'pending')
        
        # Toggle to in_progress
        response = self.client.post(reverse('todo:toggle_status', args=[self.todo_item.pk]))
        self.assertEqual(response.status_code, 302)  # Should redirect
        
        # Refresh from database
        self.todo_item.refresh_from_db()
        self.assertEqual(self.todo_item.status, 'in_progress')
        
        # Toggle back to pending
        response = self.client.post(reverse('todo:toggle_status', args=[self.todo_item.pk]))
        self.todo_item.refresh_from_db()
        self.assertEqual(self.todo_item.status, 'pending')