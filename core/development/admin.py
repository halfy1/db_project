from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .models import Project, Employee, ProjectManagement, Feature, Bug


# Кастомный UserAdmin без связи с Employee
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'priority', 'date_start', 'date_end', 'status', 'bug_count')
    list_filter = ('priority', 'is_active')
    search_fields = ('name', 'description')
    actions = ['close_projects', 'reopen_projects']

    def status(self, obj):
        return "Активен" if obj.is_active else "Завершен"

    status.short_description = 'Статус'

    def bug_count(self, obj):
        return obj.bugs.count()

    bug_count.short_description = 'Баги'

    def close_projects(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"Закрыто {updated} проектов")

    close_projects.short_description = "Закрыть проекты"

    def reopen_projects(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"Открыто {updated} проектов")

    reopen_projects.short_description = "Открыть проекты"


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'email', 'position', 'date_employment', 'is_active')
    list_filter = ('position',)
    search_fields = ('last_name', 'first_name', 'email')
    ordering = ('last_name', 'first_name')

    @admin.display(boolean=True)
    def is_active(self, obj):
        return obj.date_dismissal is None


@admin.register(ProjectManagement)
class ProjectManagementAdmin(admin.ModelAdmin):
    list_display = ('user', 'project', 'role', 'date_in', 'date_out', 'is_active')
    list_filter = ('role', 'project')
    search_fields = ('user__username', 'project__name')  # Убрал лишний __user

    def is_active(self, obj):
        return obj.date_out is None

    is_active.boolean = True

    def remove_from_projects(self, request, queryset):
        updated = queryset.update(date_out=timezone.now())
        self.message_user(request, f"Удалено {updated} сотрудников из проектов")

    remove_from_projects.short_description = "Удалить из проектов"


@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    list_display = ('name', 'project', 'status', 'creator', 'date_start', 'bug_count')
    list_filter = ('status', 'project')
    search_fields = ('name', 'description')

    def bug_count(self, obj):
        return obj.bugs.count()

    bug_count.short_description = 'Баги'


@admin.register(Bug)
class BugAdmin(admin.ModelAdmin):
    list_display = ('id', 'project', 'feature', 'category', 'priority', 'status', 'is_overdue')
    list_filter = ('category', 'project', 'priority')
    search_fields = ('description',)
    list_editable = ('priority',)
    actions = ['mark_as_fixed']

    def status(self, obj):
        return "Исправлен" if obj.fixed_at else "Открыт"

    def is_overdue(self, obj):
        return obj.deadline < timezone.now() if not obj.fixed_at else False

    is_overdue.boolean = True

    def mark_as_fixed(self, request, queryset):
        updated = queryset.update(fixed_at=timezone.now())
        self.message_user(request, f"Отмечено {updated} багов как исправленные")

    mark_as_fixed.short_description = "Отметить как исправленные"
