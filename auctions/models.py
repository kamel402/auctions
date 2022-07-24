from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Bid(models.Model):
    user = models.ForeignKey(User, on_delete= models.CASCADE)
    listing = models.ForeignKey('Listing', on_delete= models.CASCADE)
    value = models.DecimalField(max_digits=7, decimal_places=2)
    is_current = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user} places {self.value}'

class Category(models.Model):
    name = models.CharField(max_length=16)

    def __str__(self):
        return f'{self.name}'

class Listing(models.Model):
    author = models.ForeignKey(User, on_delete= models.CASCADE)
    title = models.CharField(max_length=64)
    description = models.TextField()
    price = models.DecimalField(max_digits=7, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, blank=True, null=True)
    image = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    def __str__(self):
        return f'{self.title} by {str(self.author)}'

class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete= models.CASCADE)
    listings = models.ManyToManyField(Listing, blank=True, null=True)

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    content = models.TextField()