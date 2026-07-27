from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Todo
from .forms import TodoForm


class TodoListView(ListView):
    model = Todo
    template_name = 'todo_list/todo_list.html'
    context_object_name = 'todos'
    
    def get_queryset(self):
        # Show all todos if user is not authenticated, otherwise show only user's todos
        if self.request.user.is_authenticated:
            return Todo.objects.filter(user=self.request.user)
        return Todo.objects.filter(user__isnull=True)


class TodoDetailView(DetailView):
    model = Todo
    template_name = 'todo_list/todo_detail.html'
    context_object_name = 'todo'


class TodoCreateView(CreateView):
    model = Todo
    form_class = TodoForm
    template_name = 'todo_list/todo_form.html'
    success_url = reverse_lazy('todo_list:list')
    
    def form_valid(self, form):
        if self.request.user.is_authenticated:
            form.instance.user = self.request.user
        return super().form_valid(form)


class TodoUpdateView(UpdateView):
    model = Todo
    form_class = TodoForm
    template_name = 'todo_list/todo_form.html'
    success_url = reverse_lazy('todo_list:list')


class TodoDeleteView(DeleteView):
    model = Todo
    template_name = 'todo_list/todo_confirm_delete.html'
    success_url = reverse_lazy('todo_list:list')


@login_required
def toggle_complete(request, pk):
    """Toggle the completed status of a todo item"""
    if request.method == 'POST':
        todo = get_object_or_404(Todo, pk=pk)
        if request.user == todo.user or todo.user is None:
            todo.completed = not todo.completed
            todo.save()
            return JsonResponse({'status': 'success', 'completed': todo.completed})
    return JsonResponse({'status': 'error'}, status=400)


def todo_home(request):
    """Home view for the todo list app"""
    return render(request, 'todo_list/todo_home.html')