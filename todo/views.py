from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q, Count
from django.http import JsonResponse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.core.paginator import Paginator

from .models import TodoItem, Category, Tag, Comment, Attachment
from .forms import TodoItemForm, CategoryForm, CommentForm, AttachmentForm, FilterForm


class DashboardView(LoginRequiredMixin, ListView):
    """Dashboard view showing todo statistics and upcoming items"""
    model = TodoItem
    template_name = 'todo/dashboard.html'
    context_object_name = 'todo_items'
    
    def get_queryset(self):
        return TodoItem.objects.filter(user=self.request.user).order_by('due_date')[:5]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get counts for different statuses
        context['pending_count'] = TodoItem.objects.filter(user=user, status='pending').count()
        context['in_progress_count'] = TodoItem.objects.filter(user=user, status='in_progress').count()
        context['completed_count'] = TodoItem.objects.filter(user=user, status='completed').count()
        
        # Get overdue items
        context['overdue_items'] = TodoItem.objects.filter(
            user=user,
            due_date__lt=timezone.now(),
            status__in=['pending', 'in_progress']
        ).order_by('due_date')
        
        # Get items due today
        today = timezone.now().date()
        context['due_today'] = TodoItem.objects.filter(
            user=user,
            due_date__date=today,
            status__in=['pending', 'in_progress']
        ).order_by('due_date')
        
        # Get items by priority
        context['priority_counts'] = TodoItem.objects.filter(user=user).exclude(
            status='completed'
        ).values('priority').annotate(count=Count('id'))
        
        # Get items by category
        context['category_counts'] = TodoItem.objects.filter(user=user).exclude(
            status='completed'
        ).values('category__name', 'category__color').annotate(count=Count('id'))
        
        return context


class TodoListView(LoginRequiredMixin, ListView):
    """List view for todo items with filtering and sorting"""
    model = TodoItem
    template_name = 'todo/todo_list.html'
    context_object_name = 'todo_items'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = TodoItem.objects.filter(user=self.request.user)
        
        # Apply filters from form
        filter_form = FilterForm(self.request.GET)
        if filter_form.is_valid():
            # Filter by status
            status = filter_form.cleaned_data.get('status')
            if status:
                queryset = queryset.filter(status=status)
            
            # Filter by priority
            priority = filter_form.cleaned_data.get('priority')
            if priority:
                queryset = queryset.filter(priority=priority)
            
            # Filter by category
            category = filter_form.cleaned_data.get('category')
            if category:
                queryset = queryset.filter(category=category)
            
            # Filter by tag
            tag = filter_form.cleaned_data.get('tag')
            if tag:
                queryset = queryset.filter(tags=tag)
            
            # Filter by due date range
            due_date_start = filter_form.cleaned_data.get('due_date_start')
            due_date_end = filter_form.cleaned_data.get('due_date_end')
            if due_date_start:
                queryset = queryset.filter(due_date__gte=due_date_start)
            if due_date_end:
                queryset = queryset.filter(due_date__lte=due_date_end)
            
            # Search by title or description
            search_query = filter_form.cleaned_data.get('search')
            if search_query:
                queryset = queryset.filter(
                    Q(title__icontains=search_query) | Q(description__icontains=search_query)
                )
        
        # Apply sorting
        sort_by = self.request.GET.get('sort_by', '-priority')
        return queryset.order_by(sort_by)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = FilterForm(self.request.GET)
        context['categories'] = Category.objects.all()
        context['tags'] = Tag.objects.all()
        return context


class TodoDetailView(LoginRequiredMixin, DetailView):
    """Detail view for a todo item"""
    model = TodoItem
    template_name = 'todo/todo_detail.html'
    context_object_name = 'todo_item'
    
    def get_queryset(self):
        return TodoItem.objects.filter(user=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_form'] = CommentForm()
        context['attachment_form'] = AttachmentForm()
        context['subtasks'] = TodoItem.objects.filter(parent=self.object)
        return context


class TodoCreateView(LoginRequiredMixin, CreateView):
    """Create view for a new todo item"""
    model = TodoItem
    form_class = TodoItemForm
    template_name = 'todo/todo_form.html'
    success_url = reverse_lazy('todo:list')
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Todo item created successfully!')
        return super().form_valid(form)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class TodoUpdateView(LoginRequiredMixin, UpdateView):
    """Update view for an existing todo item"""
    model = TodoItem
    form_class = TodoItemForm
    template_name = 'todo/todo_form.html'
    
    def get_queryset(self):
        return TodoItem.objects.filter(user=self.request.user)
    
    def get_success_url(self):
        return reverse_lazy('todo:detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, 'Todo item updated successfully!')
        return super().form_valid(form)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class TodoDeleteView(LoginRequiredMixin, DeleteView):
    """Delete view for a todo item"""
    model = TodoItem
    template_name = 'todo/todo_confirm_delete.html'
    success_url = reverse_lazy('todo:list')
    
    def get_queryset(self):
        return TodoItem.objects.filter(user=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Todo item deleted successfully!')
        return super().delete(request, *args, **kwargs)


class CategoryCreateView(LoginRequiredMixin, CreateView):
    """Create view for a new category"""
    model = Category
    form_class = CategoryForm
    template_name = 'todo/category_form.html'
    success_url = reverse_lazy('todo:list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Category created successfully!')
        return super().form_valid(form)


@login_required
def mark_completed(request, pk):
    """Mark a todo item as completed"""
    todo_item = get_object_or_404(TodoItem, pk=pk, user=request.user)
    todo_item.mark_completed()
    messages.success(request, f'"{todo_item.title}" marked as completed!')
    return redirect('todo:list')


@login_required
def add_comment(request, pk):
    """Add a comment to a todo item"""
    todo_item = get_object_or_404(TodoItem, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.todo_item = todo_item
            comment.user = request.user
            comment.save()
            messages.success(request, 'Comment added successfully!')
    
    return redirect('todo:detail', pk=pk)


@login_required
def add_attachment(request, pk):
    """Add an attachment to a todo item"""
    todo_item = get_object_or_404(TodoItem, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = AttachmentForm(request.POST, request.FILES)
        if form.is_valid():
            attachment = form.save(commit=False)
            attachment.todo_item = todo_item
            attachment.filename = request.FILES['file'].name
            attachment.save()
            messages.success(request, 'Attachment added successfully!')
    
    return redirect('todo:detail', pk=pk)


@login_required
def delete_attachment(request, pk):
    """Delete an attachment"""
    attachment = get_object_or_404(Attachment, pk=pk, todo_item__user=request.user)
    attachment.delete()
    messages.success(request, 'Attachment deleted successfully!')
    return redirect('todo:detail', pk=attachment.todo_item.pk)


@login_required
def toggle_status(request, pk):
    """Toggle the status of a todo item between pending and in_progress"""
    if request.method == 'POST':
        todo_item = get_object_or_404(TodoItem, pk=pk, user=request.user)
        
        if todo_item.status == 'pending':
            todo_item.status = 'in_progress'
            message = f'"{todo_item.title}" is now in progress!'
        elif todo_item.status == 'in_progress':
            todo_item.status = 'pending'
            message = f'"{todo_item.title}" is now pending!'
        
        todo_item.save()
        messages.success(request, message)
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success', 'new_status': todo_item.status})
    
    return redirect('todo:list')