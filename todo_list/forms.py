from django import forms
from django.contrib.auth.models import User
from .models import (
    TaskCategory, TaskTag, Task, SubTask, 
    TaskAttachment, TaskComment, TimeLog
)


class TaskCategoryForm(forms.ModelForm):
    class Meta:
        model = TaskCategory
        fields = ['name', 'description', 'color', 'icon']
        widgets = {
            'color': forms.TextInput(attrs={'type': 'color'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class TaskTagForm(forms.ModelForm):
    class Meta:
        model = TaskTag
        fields = ['name', 'color']
        widgets = {
            'color': forms.TextInput(attrs={'type': 'color'}),
        }


class SubTaskForm(forms.ModelForm):
    class Meta:
        model = SubTask
        fields = ['title', 'is_completed']


SubTaskInlineFormSet = forms.inlineformset_factory(
    Task, SubTask, 
    form=SubTaskForm, 
    extra=1, 
    can_delete=True
)


class TaskAttachmentForm(forms.ModelForm):
    class Meta:
        model = TaskAttachment
        fields = ['file']


class TaskCommentForm(forms.ModelForm):
    class Meta:
        model = TaskComment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Add a comment...'}),
        }


class TimeLogForm(forms.ModelForm):
    class Meta:
        model = TimeLog
        fields = ['start_time', 'end_time', 'notes']
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }


class TaskFilterForm(forms.Form):
    STATUS_CHOICES = [('', 'All')] + list(Task.STATUS_CHOICES)
    PRIORITY_CHOICES = [('', 'All')] + list(Task.PRIORITY_CHOICES)
    
    status = forms.ChoiceField(choices=STATUS_CHOICES, required=False)
    priority = forms.ChoiceField(choices=PRIORITY_CHOICES, required=False)
    category = forms.ModelChoiceField(queryset=None, required=False)
    tags = forms.ModelMultipleChoiceField(queryset=None, required=False)
    due_date_start = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    due_date_end = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    search = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Search tasks...'}))
    
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = TaskCategory.objects.filter(user=user)
        self.fields['tags'].queryset = TaskTag.objects.filter(user=user)


class TaskForm(forms.ModelForm):
    shared_with = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        required=False
    )
    
    depends_on = forms.ModelMultipleChoiceField(
        queryset=Task.objects.none(),
        required=False
    )
    
    class Meta:
        model = Task
        fields = [
            'title', 'description', 'category', 'tags', 'status', 'priority',
            'due_date', 'is_recurring', 'recurrence_pattern', 'recurrence_end_date',
            'estimated_time', 'shared_with', 'depends_on'
        ]
        widgets = {
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'recurrence_end_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 5}),
        }
    
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter categories and tags by user
        self.fields['category'].queryset = TaskCategory.objects.filter(user=user)
        self.fields['tags'].queryset = TaskTag.objects.filter(user=user)
        
        # For task dependencies, exclude the current task (if it exists) and only show user's tasks
        task_queryset = Task.objects.filter(user=user)
        if self.instance.pk:
            task_queryset = task_queryset.exclude(pk=self.instance.pk)
        self.fields['depends_on'].queryset = task_queryset