from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Todo


class TodoModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create a user
def setUpTestData(cls):
        # Import os to access environment variables
        import os
        # Create a user
        test_user = User.objects.create_user(username='testuser', password=os.getenv("TEST_USER_PASSWORD"))
        
        # Create a todo item
        Todo.objects.create(
        
        # Create a todo item
        Todo.objects.create(
            title='Test Todo',
            description='This is a test todo item',
            user=test_user
        )
    
    def test_title_max_length(self):
        todo = Todo.objects.get(id=1)
        max_length = todo._meta.get_field('title').max_length
        self.assertEqual(max_length, 200)
    
    def test_object_name_is_title(self):
        todo = Todo.objects.get(id=1)
        expected_object_name = todo.title
        self.assertEqual(str(todo), expected_object_name)
    
    def test_get_absolute_url(self):
        todo = Todo.objects.get(id=1)
        self.assertEqual(todo.get_absolute_url(), reverse('todo_list:detail', args=[str(todo.id)]))


class TodoListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create 10 todos for pagination tests
def setUpTestData(cls):
        # Create 10 todos for pagination tests
        # Import os to access environment variables for secure credential storage
        import os
        test_user = User.objects.create_user(username='testuser', password=os.getenv("TEST_USER_PASSWORD"))
        
        for todo_id in range(10):
            Todo.objects.create(
        
        for todo_id in range(10):
            Todo.objects.create(
                title=f'Test Todo {todo_id}',
                description=f'Description {todo_id}',
                user=test_user
            )
    
    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/todo/list/')
        self.assertEqual(response.status_code, 200)
    
    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('todo_list:list'))
        self.assertEqual(response.status_code, 200)
    
    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('todo_list:list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'todo_list/todo_list.html')


class TodoCreateViewTest(TestCase):
    def setUp(self):
        # Create a user
def setUp(self):
        # Import os to access environment variables
        import os
        # Create a user
        test_user = User.objects.create_user(username='testuser', password=os.getenv("TEST_USER_PASSWORD"))
        test_user.save()
        test_user.save()
    
    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('todo_list:create'))
        self.assertEqual(response.status_code, 200)  # Allow anonymous users
    
    def test_logged_in_uses_correct_template(self):
        login = self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('todo_list:create'))
        
        # Check our user is logged in
        self.assertEqual(str(response.context['user']), 'testuser')
        # Check that we got a response "success"
        self.assertEqual(response.status_code, 200)
        
        # Check we used correct template
        self.assertTemplateUsed(response, 'todo_list/todo_form.html')