# Todo List App

A simple and effective Django-based to-do list application that allows users to manage their tasks.

## Features

- Create, view, update, and delete to-do items
- Mark tasks as completed/incomplete
- Set due dates for tasks
- User-specific to-do lists (when authenticated)
- Responsive design using Bootstrap

## Usage

1. Navigate to the Todo List app from the main navigation menu
2. View your existing to-do items on the list page
3. Create new to-do items using the "Add New Todo" button
4. View details of a to-do item by clicking the "View" button
5. Edit a to-do item by clicking the "Edit" button
6. Delete a to-do item by clicking the "Delete" button
7. Mark a to-do item as completed/incomplete using the toggle button

## Models

### Todo

- `title`: The title of the to-do item
- `description`: A detailed description of the to-do item (optional)
- `created_date`: The date and time when the to-do item was created
- `due_date`: The date and time when the to-do item is due (optional)
- `completed`: A boolean indicating whether the to-do item is completed
- `user`: The user who created the to-do item (optional, for authenticated users)

## Views

- `TodoListView`: Displays a list of to-do items
- `TodoDetailView`: Displays details of a specific to-do item
- `TodoCreateView`: Creates a new to-do item
- `TodoUpdateView`: Updates an existing to-do item
- `TodoDeleteView`: Deletes a to-do item
- `toggle_complete`: Toggles the completed status of a to-do item
- `todo_home`: Displays the home page of the to-do list app

## URLs

- `/todo/`: Home page of the to-do list app
- `/todo/list/`: List of to-do items
- `/todo/detail/<int:pk>/`: Details of a specific to-do item
- `/todo/create/`: Create a new to-do item
- `/todo/update/<int:pk>/`: Update an existing to-do item
- `/todo/delete/<int:pk>/`: Delete a to-do item
- `/todo/toggle/<int:pk>/`: Toggle the completed status of a to-do item