from django import forms
from django.utils import timezone
from .models import TodoItem, Category, Tag, Comment, Attachment


class TodoItemForm(forms.ModelForm):
    """Form for creating and updating todo items"""
    
    new_tags = forms.CharField(required=False)
    
    class Meta:
        model = TodoItem
        fields = [
            'title', 'description', 'category', 'tags', 'priority',
            'status', 'due_date', 'parent', 'is_recurring',
            'recurrence_pattern', 'reminder_datetime'
        ]
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Limit parent task choices to the user's own tasks
        if user:
            self.fields['parent'].queryset = TodoItem.objects.filter(user=user, parent__isnull=True)
            
            # Exclude the current task from parent options when editing
            if self.instance.pk:
                self.fields['parent'].queryset = self.fields['parent'].queryset.exclude(pk=self.instance.pk)
        
        # Add recurrence pattern choices
        self.fields['recurrence_pattern'].widget = forms.Select(choices=(
            ('', '---------'),
            ('daily', 'Daily'),
            ('weekly', 'Weekly'),
            ('monthly', 'Monthly'),
            ('yearly', 'Yearly'),
        ))
    
    def clean_due_date(self):
        """Validate that due date is not in the past"""
        due_date = self.cleaned_data.get('due_date')
        if due_date and due_date < timezone.now():
            self.add_error('due_date', 'Due date cannot be in the past')
        return due_date
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Process new tags
        new_tags_str = self.cleaned_data.get('new_tags', '')
        if new_tags_str:
            new_tag_names = [tag.strip() for tag in new_tags_str.split(',') if tag.strip()]
            
            if commit:  # Only process tags if we're committing
                for tag_name in new_tag_names:
                    tag, created = Tag.objects.get_or_create(name=tag_name)
                    instance.tags.add(tag)
        
        if commit:
            instance.save()
            self.save_m2m()
        
        return instance


class CategoryForm(forms.ModelForm):
    """Form for creating and updating categories"""
    class Meta:
        model = Category
        fields = ['name', 'color', 'icon']


class CommentForm(forms.ModelForm):
    """Form for adding comments to todo items"""
    class Meta:
        model = Comment
        fields = ['text']


class AttachmentForm(forms.ModelForm):
    """Form for adding attachments to todo items"""
    class Meta:
        model = Attachment
        fields = ['file']


class FilterForm(forms.Form):
    """Form for filtering todo items"""
    STATUS_CHOICES = [('', 'All')] + list(TodoItem.STATUS_CHOICES)
    PRIORITY_CHOICES = [('', 'All')] + list(TodoItem.PRIORITY_CHOICES)
    
    status = forms.ChoiceField(choices=STATUS_CHOICES, required=False)
    priority = forms.ChoiceField(choices=PRIORITY_CHOICES, required=False)
    category = forms.ModelChoiceField(queryset=Category.objects.all(), required=False, empty_label="All Categories")
    tag = forms.ModelChoiceField(queryset=Tag.objects.all(), required=False, empty_label="All Tags")
    due_date_start = forms.DateField(required=False)
    due_date_end = forms.DateField(required=False)
    search = forms.CharField(required=False)