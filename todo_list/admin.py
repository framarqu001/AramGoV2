from django.contrib import admin
from .models import (
    TaskCategory, TaskTag, Task, SubTask, 
    TaskAttachment, TaskComment, TaskNotification, TimeLog
)


@admin.register(TaskCategory)
class TaskCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'color', 'task_count', 'created_at')
    list_filter = ('user',)
    search_fields = ('name', 'description', 'user__username')


@admin.register(TaskTag)
class TaskTagAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'color', 'created_at')
    list_filter = ('user',)
    search_fields = ('name', 'user__username')


class SubTaskInline(admin.TabularInline):
    model = SubTask
    extra = 1


class TaskAttachmentInline(admin.TabularInline):
    model = TaskAttachment
    extra = 1
    readonly_fields = ('file_size', 'file_type')


class TaskCommentInline(admin.TabularInline):
    model = TaskComment
    extra = 0
    readonly_fields = ('created_at',)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'category', 'status', 'priority', 'due_date', 'is_recurring', 'created_at')
    list_filter = ('status', 'priority', 'category', 'is_recurring', 'user')
    search_fields = ('title', 'description', 'user__username')
    date_hierarchy = 'created_at'
    filter_horizontal = ('tags', 'shared_with', 'depends_on')
    readonly_fields = ('created_at', 'updated_at', 'completed_at')
    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'user', 'category', 'tags', 'status', 'priority')
        }),
        ('Dates', {
            'fields': ('due_date', 'created_at', 'updated_at', 'completed_at')
        }),
        ('Recurrence', {
            'fields': ('is_recurring', 'recurrence_pattern', 'recurrence_end_date'),
            'classes': ('collapse',)
        }),
        ('Relationships', {
            'fields': ('parent_task', 'depends_on'),
            'classes': ('collapse',)
        }),
        ('Sharing', {
            'fields': ('shared_with',),
            'classes': ('collapse',)
        }),
        ('Time Tracking', {
            'fields': ('estimated_time', 'actual_time'),
            'classes': ('collapse',)
        }),
        ('Display', {
            'fields': ('order',),
            'classes': ('collapse',)
        }),
    )
    inlines = [SubTaskInline, TaskAttachmentInline, TaskCommentInline]


@admin.register(SubTask)
class SubTaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'task', 'is_completed', 'created_at')
    list_filter = ('is_completed', 'task__user')
    search_fields = ('title', 'task__title')


@admin.register(TaskAttachment)
class TaskAttachmentAdmin(admin.ModelAdmin):
    list_display = ('filename', 'task', 'file_type', 'file_size', 'uploaded_at')
    list_filter = ('task__user', 'uploaded_at')
    search_fields = ('filename', 'task__title')
    readonly_fields = ('file_size', 'file_type', 'uploaded_at')


@admin.register(TaskComment)
class TaskCommentAdmin(admin.ModelAdmin):
    list_display = ('task', 'user', 'content_preview', 'created_at')
    list_filter = ('user', 'created_at')
    search_fields = ('content', 'task__title', 'user__username')
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'


@admin.register(TaskNotification)
class TaskNotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'task', 'notification_type', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at', 'user')
    search_fields = ('message', 'task__title', 'user__username')
    actions = ['mark_as_read', 'mark_as_unread']
    
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
    mark_as_read.short_description = "Mark selected notifications as read"
    
    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False)
    mark_as_unread.short_description = "Mark selected notifications as unread"


@admin.register(TimeLog)
class TimeLogAdmin(admin.ModelAdmin):
    list_display = ('task', 'user', 'start_time', 'end_time', 'duration', 'created_at')
    list_filter = ('user', 'start_time')
    search_fields = ('task__title', 'user__username', 'notes')
    readonly_fields = ('duration', 'created_at')