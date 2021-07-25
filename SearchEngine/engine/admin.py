from django.contrib import admin
from .models import Rank, Link, Searches, Words

# Register your models here.
admin.site.register(Rank)
admin.site.register(Link)
admin.site.register(Searches)
admin.site.register(Words)
