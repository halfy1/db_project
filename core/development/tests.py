import time
import random
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
                Employee.objects.all().delete()
                print(f"\nТесты для {size} записей:")

                self.create_dataset(size)

                self.measure("Поиск по pk", lambda: Employee.objects.first())

                example_email = Employee.objects.first().email
                self.measure("Поиск по email", lambda: Employee.objects.get(email=example_email))

                self.measure("Поиск по маске email", lambda: list(Employee.objects.filter(email__icontains="user_1")))

                self.measure("Добавление одной записи", lambda: Employee.objects.create(
                    first_name="New",
                    last_name="User",
                    email=f"unique_{random.randint(1, 1_000_000)}@example.com",
                    position='tester'
                ))

                self.measure("Добавление группы (100 записей)", lambda: Employee.objects.bulk_create(
                    self.generate_employees(100)
                ))

                self.measure("Изменение по pk", lambda: Employee.objects.filter(pk=1).update(first_name="Updated"))

                self.measure("Изменение по email", lambda: Employee.objects.filter(email=example_email).update(last_name="Changed"))

                self.measure("Удаление по pk", lambda: Employee.objects.filter(pk=1).delete())

                self.measure("Удаление по email", lambda: Employee.objects.filter(email=example_email).delete())

                self.measure("Удаление группы (200 записей)", lambda: Employee.objects.filter(id__lte=200).delete())  # Удаляем по id

                self.measure("Сжатие после удаления 200", self.vacuum)

                Employee.objects.exclude(id__lte=200).delete()
                self.measure("Сжатие после удаления до 200 строк", self.vacuum)

    def vacuum(self):
        with connection.cursor() as cursor:
            cursor.execute("VACUUM;")
