from django.contrib import admin
from .models import Category, Tag, TodoItem, Attachment, Comment


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'color')
    search_fields = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


class AttachmentInline(admin.TabularInline):
    model = Attachment
    extra = 1


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 1


@admin.register(TodoItem)
class TodoItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'category', 'priority', 'status', 'due_date', 'is_overdue')
    list_filter = ('status', 'priority', 'category', 'tags', 'created_date', 'due_date')
    search_fields = ('title', 'description', 'user__username')
    date_hierarchy = 'created_date'
    filter_horizontal = ('tags',)
    inlines = [AttachmentInline, CommentInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'user')
        }),
        ('Categorization', {
            'fields': ('category', 'tags')
        }),
        ('Status & Priority', {
            'fields': ('status', 'priority')
        }),
        ('Dates', {
            'fields': ('due_date', 'completed_date')
        }),
        ('Hierarchy', {
            'fields': ('parent',)
        }),
        ('Recurrence & Reminders', {
            'fields': ('is_recurring', 'recurrence_pattern', 'reminder_datetime'),
            'classes': ('collapse',)
        }),
    )
    
    def is_overdue(self, obj):
        return obj.is_overdue()
    
    is_overdue.boolean = True
    is_overdue.short_description = "Overdue"


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ('filename', 'todo_item', 'uploaded_at')
    search_fields = ('filename', 'todo_item__title')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('todo_item', 'user', 'created_at')
    list_filter = ('created_at', 'user')
    search_fields = ('text', 'todo_item__title', 'user__username')