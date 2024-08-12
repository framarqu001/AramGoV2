from django.db import models


class Champion(models.Model):
    champion_id = models.CharField(primary_key=True, max_length=30)
    name = models.CharField(max_length=30)
    title = models.CharField(max_length=200)
    image_path = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Items(models.Model):
    item_id = models.CharField(primary_key=True, max_length=30)
    name = models.CharField(max_length=30)
    image_path = models.CharField(max_length=100)