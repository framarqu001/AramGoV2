# Sophisticated Todo App

A feature-rich, sophisticated Todo application built with Django. This app helps users manage their tasks efficiently with advanced features like categorization, tagging, priorities, reminders, and more.

## Features

### Task Management
- Create, view, update, and delete tasks
- Set task priorities (Low, Medium, High, Urgent)
- Track task status (Pending, In Progress, Completed, Deferred, Cancelled)
- Set due dates and reminders
- Add detailed descriptions to tasks
- Organize tasks with categories and tags
- Create hierarchical tasks with parent-child relationships
- Add comments to tasks for collaboration
- Attach files to tasks

### Advanced Features
- Dashboard with task statistics and overview
- Filter and sort tasks by various criteria
- Recurring tasks (daily, weekly, monthly, yearly)
- Email reminders for upcoming tasks
- Task completion tracking
- Responsive design for mobile and desktop

## Technical Implementation

### Models
- `TodoItem`: The core model for tasks with fields for title, description, status, priority, etc.
- `Category`: For organizing tasks into categories with custom colors and icons
- `Tag`: For flexible tagging of tasks
- `Comment`: For adding comments to tasks
- `Attachment`: For attaching files to tasks

### Views
- Class-based views for CRUD operations
- Dashboard view with statistics
- List view with filtering and sorting
- Detail view with comments and attachments

### Celery Tasks
- `send_due_reminders`: Sends email reminders for upcoming tasks
- `create_recurring_tasks`: Automatically creates new instances of recurring tasks

## Usage

### Dashboard
The dashboard provides an overview of your tasks with statistics and quick access to important tasks:
- Task counts by status
- Overdue tasks
- Tasks due today
- Tasks by priority and category
- Quick action buttons

### Task List
The task list view shows all your tasks with filtering and sorting options:
- Filter by status, priority, category, tag, and date range
- Sort by due date, priority, or creation date
- Quick actions for completing tasks or changing status

### Task Details
The task detail view shows all information about a task:
- Complete task information
- Comments section
- Attachments
- Subtasks
- Actions for editing, deleting, or changing status

## Installation

1. Make sure the app is included in your project's `INSTALLED_APPS`:
   ```python
   INSTALLED_APPS = [
       # ...
       'todo.apps.TodoConfig',
       # ...
   ]
   ```

2. Include the app's URLs in your project's `urls.py`:
   ```python
   urlpatterns = [
       # ...
       path('todo/', include('todo.urls')),
       # ...
   ]
   ```

3. Run migrations:
   ```
   python manage.py makemigrations
   python manage.py migrate
   ```

4. Start the development server:
   ```
   python manage.py runserver
   ```

5. For email reminders and recurring tasks, make sure Celery is configured and running:
   ```
   celery -A your_project_name worker -l info
   celery -A your_project_name beat -l info
   ```

## License

This project is licensed under the MIT License - see the LICENSE file for details.