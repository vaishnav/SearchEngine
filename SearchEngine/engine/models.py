from django.db import models

# Create your models here.
class Link(models.Model):
    link = models.URLField(max_length = 5000)
    title = models.CharField(max_length = 100)

    def __str__(self):
        return f"{self.title}"

class Rank(models.Model):
    page_link = models.OneToOneField(Link,on_delete = models.CASCADE)
    pagerank = models.DecimalField(max_digits=5, decimal_places=2)

