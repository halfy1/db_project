from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


class Project(models.Model):
    PRIORITY_CHOICES = [
        ('high', 'Высокий'),
        ('medium', 'Средний'),
        ('low', 'Низкий'),
    ]

    name = models.CharField(max_length=255, unique=True, verbose_name="Название проекта")
    description = models.TextField(blank=True, verbose_name="Описание")
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='medium',
        verbose_name="Приоритет"
    )
    date_start = models.DateTimeField(
        default=timezone.now,
        verbose_name="Дата начала"
    )
    date_end = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Дата окончания"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Активный проект"
    )

    def clean(self):
        if self.date_end and self.date_start > self.date_end:
            raise ValidationError("Дата окончания проекта не может быть раньше даты начала")

    @property
    def status(self):
        if self.date_end and self.date_end < timezone.now():
            return "Завершен"
        return "Активный" if self.is_active else "Неактивный"

    def __str__(self):
        return f"{self.name} ({self.get_priority_display()})"

    class Meta:
        verbose_name = "Проект"
        verbose_name_plural = "Проекты"
        ordering = ['-date_start']


class Employee(models.Model):
    POSITION_CHOICES = [
        ('developer', 'Разработчик'),
        ('tester', 'Тестировщик'),
        ('manager', 'Менеджер'),
        ('analyst', 'Аналитик'),
    ]

    first_name = models.CharField(max_length=100, verbose_name="Имя")
    last_name = models.CharField(max_length=100, verbose_name="Фамилия")
    email = models.EmailField(verbose_name="Email", unique=True)
    position = models.CharField(
        max_length=20,
        choices=POSITION_CHOICES,
        verbose_name="Должность"
    )
    date_employment = models.DateTimeField(
        default=timezone.now,
        verbose_name="Дата приема"
    )
    date_dismissal = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Дата увольнения"
    )

    def clean(self):
        if self.pk:  # Проверяем, что объект уже сохранён
            active_participations = self.projectmanagement_set.filter(
                date_out__isnull=True
            ).count()
            if active_participations >= 2:
                raise ValidationError("Сотрудник не может участвовать более чем в 2 проектах одновременно")

    @property
    def is_active(self):
        return self.date_dismissal is None

    def __str__(self):
        return f"{self.last_name} {self.first_name} ({self.get_position_display()})"

    class Meta:
        verbose_name = "Сотрудник"
        verbose_name_plural = "Сотрудники"
        ordering = ['last_name', 'first_name']


class ProjectManagement(models.Model):
    ROLE_CHOICES = [
        ('developer', 'Разработчик'),
        ('tester', 'Тестировщик'),
        ('manager', 'Менеджер'),
        ('analyst', 'Аналитик'),
    ]

    user = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        verbose_name="Сотрудник"
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        verbose_name="Проект"
    )
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='developer',
        verbose_name="Роль в проекте"
    )
    date_in = models.DateTimeField(
        default=timezone.now,
        verbose_name="Дата включения в проект"
    )
    date_out = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Дата выхода из проекта"
    )

    class Meta:
        unique_together = ('user', 'project')
        verbose_name = "Участие в проекте"
        verbose_name_plural = "Участия в проектах"
        ordering = ['-date_in']

    @property
    def is_active(self):
        return self.date_out is None

    def __str__(self):
        return f"{self.user} - {self.get_role_display()} в {self.project}"


class Feature(models.Model):
    STATUS_CHOICES = [
        ('planned', 'Запланировано'),
        ('in_progress', 'В разработке'),
        ('completed', 'Завершено'),
        ('postponed', 'Отложено'),
    ]

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='features',
        verbose_name="Проект"
    )
    creator = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='created_features',
        verbose_name="Создатель"
    )
    name = models.CharField(
        max_length=255,
        verbose_name="Название фичи"
    )
    description = models.TextField(
        blank=True,
        verbose_name="Описание"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='planned',
        verbose_name="Статус"
    )
    date_start = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Дата начала разработки"
    )
    date_end = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Дата завершения разработки"
    )

    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"

    class Meta:
        verbose_name = "Фича"
        verbose_name_plural = "Фичи"
        ordering = ['project', '-date_start']


def default_deadline():
    return timezone.now() + timedelta(days=7)


class Bug(models.Model):
    CATEGORY_CHOICES = [
        ('UI', 'UI Issue'),
        ('backend', 'Backend Issue'),
        ('performance', 'Performance Issue'),
        ('security', 'Security Vulnerability'),
        ('database', 'Database Issue'),
    ]

    PRIORITY_CHOICES = [
        ('critical', 'Критичный'),
        ('high', 'Высокий'),
        ('medium', 'Средний'),
        ('low', 'Низкий'),
    ]

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='bugs',
        verbose_name="Проект"
    )
    feature = models.ForeignKey(
        Feature,
        on_delete=models.CASCADE,
        related_name='bugs',
        verbose_name="Фича"
    )
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='backend',
        verbose_name="Категория"
    )
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='medium',
        verbose_name="Приоритет"
    )
    reported_by = models.ForeignKey(
        Employee,
        related_name='reported_bugs',
        on_delete=models.CASCADE,
        verbose_name="Кто сообщил"
    )
    reported_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата сообщения"
    )
    assigned_to = models.ForeignKey(
        Employee,
        related_name='assigned_bugs',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Назначено"
    )
    deadline = models.DateTimeField(
        default=default_deadline,  # Используем функцию вместо lambda
        verbose_name="Срок исправления"
    )
    fixed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Фактическая дата исправления"
    )
    description = models.TextField(
        default="No description provided",  # Добавляем значение по умолчанию
        verbose_name="Описание проблемы"
    )
    steps_to_reproduce = models.TextField(
        blank=True,
        verbose_name="Шаги воспроизведения"
    )

    @property
    def status(self):
        if self.fixed_at:
            return "Исправлен"
        if self.assigned_to:
            return "В работе"
        return "Открыт"

    @property
    def is_overdue(self):
        return self.deadline < timezone.now() and not self.fixed_at

    def clean(self):
        if self.fixed_at and self.fixed_at < self.reported_at:
            raise ValidationError("Дата исправления не может быть раньше даты сообщения")

    def __str__(self):
        return f"{self.get_category_display()} ({self.get_priority_display()}): {self.description[:50]}"

    class Meta:
        verbose_name = "Баг"
        verbose_name_plural = "Баги"
        ordering = ['-reported_at']