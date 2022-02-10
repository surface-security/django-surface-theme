from django.db import models


class Driver(models.Model):
    """
    model with default primary key `id`
    """

    last_name = models.CharField(max_length=50)


class Car(models.Model):
    """
    model with specific primary key
    """

    plate = models.CharField(max_length=10, primary_key=True)
    doors = models.IntegerField(default=5)
