from django.db import models


class TestData(models.Model):
    id = models.AutoField(primary_key=True)
    value = models.CharField(max_length=100)
    non_key_field = models.IntegerField()

    class Meta:
        db_table = 'test_data'