from django.db import models

# Create your models here.
class Rank(models.Model):
    page_link = models.URLField(max_length = 5000)
    pagerank = models.DecimalField(max_digits=5, decimal_places=2)