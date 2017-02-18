from django.contrib import admin
from .models import Card, Deck, User

# Register your models here.
admin.site.register(Card)
admin.site.register(User)
admin.site.register(Deck)
