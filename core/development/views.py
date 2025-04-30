from django.shortcuts import render
from django.db.models import Prefetch, Count, Q, Avg, F
from django.db.models import ExpressionWrapper, DurationField
from django.db import models
from django.utils import timezone
from .models import Project, Employee, Feature, Bug, ProjectManagement

def reports_view(request):
    # Активные проекты с участниками и количеством багов
    active_projects = Project.objects.filter(is_active=True).annotate(
        developers_count=Count(
            'projectmanagement',
            filter=Q(projectmanagement__role='developer', projectmanagement__date_out__isnull=True)
        ),
        testers_count=Count(
            'projectmanagement',
            filter=Q(projectmanagement__role='tester', projectmanagement__date_out__isnull=True)
        ),
        bug_count=Count('bugs')
    ).prefetch_related(
        Prefetch(
            'projectmanagement_set',
            queryset=ProjectManagement.objects.filter(date_out__isnull=True).select_related('user'),
            to_attr='current_members'
        )
    )[:20]

    # Сотрудники с активными проектами
    employees = Employee.objects.annotate(
        active_projects_count=Count(
            'projectmanagement',
            filter=Q(projectmanagement__date_out__isnull=True)
        ),
        reported_bugs_count=Count('reported_bugs'),
        assigned_bugs_count=Count('assigned_bugs')
    ).prefetch_related(
        Prefetch(
            'projectmanagement_set',
            queryset=ProjectManagement.objects.select_related('project').order_by('-date_in'),
            to_attr='current_projects'
        )
    )[:50]

    # Фичи с количеством багов
    features = Feature.objects.select_related('project', 'creator').annotate(
        bug_count=Count('bugs')
    )[:100]

    # Последние баги
    bugs = Bug.objects.select_related(
        'project', 'feature', 'reported_by', 'assigned_to'
    ).order_by('-reported_at')[:100]

    # Данные для графиков
    projects_for_charts = Project.objects.annotate(
        total_bugs=Count('bugs', distinct=True),
        open_bugs=Count('bugs', filter=Q(bugs__fixed_at__isnull=True), distinct=True),
        # Фильтруем только корректные даты (fixed_at >= reported_at)
        avg_fix_seconds=Avg(
            ExpressionWrapper(
                F('bugs__fixed_at') - F('bugs__reported_at'),
                output_field=DurationField()
            ),
            filter=Q(bugs__fixed_at__isnull=False) &
                   Q(bugs__fixed_at__gte=F('bugs__reported_at'))
        ),
        project_duration=F('date_end') - F('date_start'),
        active_members=Count('projectmanagement', filter=Q(projectmanagement__date_out__isnull=True))
    ).order_by('-date_start')[:5]

    fix_speeds = []
    for project in projects_for_charts:
        if project.avg_fix_seconds:
            days = project.avg_fix_seconds.total_seconds() / 86400
            # Округляем до десятых, но не показываем значения меньше 0.1 дня
            days_rounded = round(days, 1) if days >= 0.1 else 0.1
        else:
            days_rounded = 0  # Если нет данных

        fix_speeds.append((project.name, days_rounded))


    # Вычисляем показатель качества разработки (bugs per person-day)
    quality_scores = []
    for project in projects_for_charts:
        if project.project_duration and project.active_members:
            # Преобразуем продолжительность проекта в человеко-дни
            person_days = project.project_duration.days * project.active_members
            quality_score = project.total_bugs / person_days if person_days > 0 else 0
            quality_scores.append(round(quality_score, 2))
        else:
            quality_scores.append(0)

    context = {
        'active_projects': active_projects,
        'employees': employees,
        'features': features,
        'bugs': bugs,
        'metrics': {
            'total_active_projects': Project.objects.filter(is_active=True).count(),
            'total_active_employees': Employee.objects.filter(date_dismissal__isnull=True).count(),
            'open_bugs_count': Bug.objects.filter(fixed_at__isnull=True).count(),
        },
        'chart_data': {
            'projects': [p.name for p in projects_for_charts],
            'total_bugs': [p.total_bugs for p in projects_for_charts],
            'open_bugs': [p.open_bugs for p in projects_for_charts],
            'avg_fix_days': [
                round(p.avg_fix_seconds.total_seconds() / 86400, 1)
                if p.avg_fix_seconds else 0
                for p in projects_for_charts
            ],
            'quality_scores': quality_scores
        }
    }

    return render(request, 'development/reports.html', context)
