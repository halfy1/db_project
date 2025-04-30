import time
import random
from datetime import timedelta
from django.test import TestCase
from django.utils import timezone
from django.db import connection
from development.models import Employee

class PerformanceTests(TestCase):
    sizes = [1000, 10000, 100000]

    def generate_employees(self, size):
        base_time = timezone.now()
        return [
            Employee(
                first_name=f"Name_{i}",
                last_name=f"Last_{i}",
                email=f"user_{i}_{random.randint(1, 1_000_000)}@example.com",  # уникальность
                position='developer',
                date_employment=base_time
            )
            for i in range(size)
        ]

    def create_dataset(self, size):
        # Для каждого размера создаем набор данных
        Employee.objects.bulk_create(self.generate_employees(size))

    def measure(self, description, func):
        start = time.perf_counter()
        func()
        duration = time.perf_counter() - start
        print(f"{description}: {duration:.2e} сек")
        return duration

    def test_performance_operations(self):
        for size in self.sizes:
            with self.subTest(size=size):
                # Удаляем все старые записи перед тестом
                Employee.objects.all().delete()
                print(f"\nТесты для {size} записей:")

                # Создание начального набора данных
                self.create_dataset(size)

                # 1. Поиск записи по ключевому полю (pk)
                self.measure("Поиск по pk", lambda: Employee.objects.first())  # используем first(), чтобы гарантированно получить запись

                # 2. Поиск записи по не ключевому полю (email)
                example_email = Employee.objects.first().email
                self.measure("Поиск по email", lambda: Employee.objects.get(email=example_email))

                # 3. Поиск записи по маске
                self.measure("Поиск по маске email", lambda: list(Employee.objects.filter(email__icontains="user_1")))

                # 4. Добавление записи
                self.measure("Добавление одной записи", lambda: Employee.objects.create(
                    first_name="New",
                    last_name="User",
                    email=f"unique_{random.randint(1, 1_000_000)}@example.com",
                    position='tester'
                ))

                # 5. Добавление группы записей (100)
                self.measure("Добавление группы (100 записей)", lambda: Employee.objects.bulk_create(
                    self.generate_employees(100)
                ))

                # 6. Изменение записи (по ключевому полю)
                self.measure("Изменение по pk", lambda: Employee.objects.filter(pk=1).update(first_name="Updated"))

                # 7. Изменение записи (по не ключевому полю)
                self.measure("Изменение по email", lambda: Employee.objects.filter(email=example_email).update(last_name="Changed"))

                # 8. Удаление записи (по ключевому полю)
                self.measure("Удаление по pk", lambda: Employee.objects.filter(pk=1).delete())

                # 9. Удаление записи (по не ключевому полю)
                self.measure("Удаление по email", lambda: Employee.objects.filter(email=example_email).delete())

                # 10. Удаление группы записей (например, 200 записей)
                self.measure("Удаление группы (200 записей)", lambda: Employee.objects.filter(id__lte=200).delete())  # Удаляем по id

                # 11. Сжатие базы данных после удаления 200 строк
                self.measure("Сжатие после удаления 200", self.vacuum)

                # 12. Сжатие базы данных после удаления, оставляя 200 строк
                Employee.objects.exclude(id__lte=200).delete()  # Удаляем все, оставив 200
                self.measure("Сжатие после удаления до 200 строк", self.vacuum)

    def vacuum(self):
        # Вставляем команду для сжатия базы данных SQLite
        with connection.cursor() as cursor:
            cursor.execute("VACUUM;")
