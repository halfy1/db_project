import time
import statistics
from django.test import TransactionTestCase
from benchmarkdb.models import TestData
from django.db import connection, reset_queries
from django.conf import settings
import random


class RealisticDatabaseBenchmarkTests(TransactionTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.sizes = [1000, 10000, 100000]
        cls.repeats = 20
        cls.bulk_size = 200

        settings.DEBUG = True
        connection.queries_log.clear()

    def _prepare_test_data(self, size):
        TestData.objects.all().delete()
        data_to_create = [
            TestData(value=f"data:{i:06d}", non_key_field=i % 100)
            for i in range(size)
        ]
        TestData.objects.bulk_create(data_to_create)
        time.sleep(0.5)

    def _measure_complex_operation(self, operation_name, prepare_func, main_func):
        times = []

        for _ in range(self.repeats):
            reset_queries()
            time.sleep(0.05)

            obj = prepare_func()

            start_time = time.perf_counter()
            result = main_func(obj)
            end_time = time.perf_counter()

            times.append(end_time - start_time)

        avg_time = statistics.median(times) * 1000
        min_time = min(times) * 1000
        max_time = max(times) * 1000
        print(f"{operation_name}: {avg_time:.3f} ms (min: {min_time:.3f}, max: {max_time:.3f})")
        return avg_time

    def test_realistic_operations(self):
        for size in self.sizes:
            print(f"\n=== Размер таблицы: {size} записей ===")
            print("Подготовка данных...")
            self._prepare_test_data(size)

            self._measure_complex_operation(
                "1. Поиск по ключевому полю",
                lambda: random.choice(TestData.objects.values_list('id', flat=True)),
                lambda obj_id: TestData.objects.get(id=obj_id)
            )

            self._measure_complex_operation(
                "2. Поиск по неключевому полю",
                lambda: 50,
                lambda val: TestData.objects.filter(non_key_field=val).first()
            )

            self._measure_complex_operation(
                "3. Поиск по маске (LIKE)",
                lambda: "data:00",
                lambda pattern: TestData.objects.filter(value__icontains=pattern).first()
            )

            self._measure_complex_operation(
                "4. Добавление одной записи",
                lambda: None,
                lambda _: TestData.objects.create(
                    value=f"single_insert_{random.randint(1, 1000)}",
                    non_key_field=random.randint(0, 99)
                )
            )

            self._measure_complex_operation(
                "5. Групповое добавление",
                lambda: None,
                lambda _: TestData.objects.bulk_create([
                    TestData(value=f"bulk_insert_{i}_{random.randint(1, 1000)}", non_key_field=random.randint(0, 99))
                    for i in range(self.bulk_size)
                ])
            )

            self._measure_complex_operation(
                "6. Изменение по ключевому полю",
                lambda: random.choice(TestData.objects.values_list('id', flat=True)),
                lambda obj_id: TestData.objects.filter(id=obj_id).update(
                    value=f"updated_{random.randint(1, 1000)}"
                )
            )

            self._measure_complex_operation(
                "7. Изменение по неключевому полю",
                lambda: 50,
                lambda val: TestData.objects.filter(non_key_field=val).update(
                    value=f"updated_{random.randint(1, 1000)}"
                )
            )

            self._measure_complex_operation(
                "8. Удаление по ключевому полю",
                lambda: random.choice(TestData.objects.values_list('id', flat=True)),
                lambda obj_id: TestData.objects.filter(id=obj_id).delete()
            )

            self._measure_complex_operation(
                "9. Удаление по неключевому полю",
                lambda: 75,
                lambda val: TestData.objects.filter(non_key_field=val).delete()
            )

            self._measure_complex_operation(
                "10. Удаление группы записей",
                lambda: list(TestData.objects.values_list('id', flat=True))[:self.bulk_size],
                lambda ids: TestData.objects.filter(id__in=ids).delete()
            )

            print("\nТестирование сжатия БД...")
            if size >= 1000:
                ids_to_delete = list(TestData.objects.values_list('id', flat=True))[:200]
                TestData.objects.filter(id__in=ids_to_delete).delete()

                start_time = time.perf_counter()
                with connection.cursor() as cursor:
                    cursor.execute("VACUUM")
                vacuum_time = (time.perf_counter() - start_time) * 1000
                print(f"11. Сжатие после удаления 200 строк: {vacuum_time:.3f} ms")

            if size >= 1000:
                preserved_ids = random.sample(
                    list(TestData.objects.values_list('id', flat=True)), 200)
                TestData.objects.exclude(id__in=preserved_ids).delete()

                start_time = time.perf_counter()
                with connection.cursor() as cursor:
                    cursor.execute("VACUUM")
                vacuum_time = (time.perf_counter() - start_time) * 1000
                print(f"12. Сжатие (остаётся 200 строк): {vacuum_time:.3f} ms")
