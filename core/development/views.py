from django.shortcuts import render
from django.views.decorators.cache import cache_page
from django.db.models import Prefetch, Count, Q
from .models import Project, Employee, Feature, Bug, ProjectManagement
from django.utils import timezone

@cache_page(60 * 15)  # Кеширование на 15 минут
def reports_view(request):
    # Оптимизированный запрос для активных проектов
    active_projects = Project.objects.filter(is_active=True).annotate(
        developers_count=Count('projectmanagement',
                            filter=Q(projectmanagement__role='developer') &
                                   Q(projectmanagement__date_out__isnull=True)),
        testers_count=Count('projectmanagement',
                          filter=Q(projectmanagement__role='tester') &
                                 Q(projectmanagement__date_out__isnull=True)),
        bug_count=Count('bugs')
    ).prefetch_related(
        Prefetch(
            'projectmanagement_set',
            queryset=ProjectManagement.objects.filter(date_out__isnull=True)
                        .select_related('project'),
            to_attr='current_members'
        )
    )[:20]

    # Сотрудники с их активными проектами
    employees = Employee.objects.annotate(
        active_projects_count=Count('projectmanagement',
                                 filter=Q(projectmanagement__date_out__isnull=True)),
        reported_bugs_count=Count('reported_bugs'),
        assigned_bugs_count=Count('assigned_bugs')
    ).prefetch_related(
        Prefetch(
            'projectmanagement_set',
            queryset=ProjectManagement.objects.filter(date_out__isnull=True)
                        .select_related('project'),
            to_attr='current_projects'
        )
    )[:50]

    # Фичи с количеством связанных багов
    features = Feature.objects.select_related('project', 'creator').annotate(
        bug_count=Count('bugs')
    )[:100]

    # Баги с информацией о просрочке
    bugs = Bug.objects.select_related(
        'project', 'feature', 'reported_by', 'assigned_to'
    ).annotate(
        is_overdue=Q(deadline__lt=timezone.now()) & Q(fixed_at__isnull=True)
    ).order_by('-reported_at')[:100]

    context = {
        'active_projects': active_projects,
        'employees': employees,
        'features': features,
        'bugs': bugs,
        'metrics': {
            'total_active_projects': Project.objects.filter(is_active=True).count(),
            'total_active_employees': Employee.objects.filter(date_dismissal__isnull=True).count(),
            'open_bugs_count': Bug.objects.filter(fixed_at__isnull=True).count(),
        }
    }

    return render(request, 'development/reports.html', context)
