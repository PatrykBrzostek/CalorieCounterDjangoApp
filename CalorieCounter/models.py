from django.db.models import *
from django.utils.timezone import localdate

class Product(Model):
    ean = CharField(unique=True, max_length=32)
    name = CharField(max_length=64)
    carbohydrates = FloatField(default=0)
    protein = FloatField(default=0)
    fat = FloatField(default=0)

    def __str__(self):
        return self.name

class Meal(Model):
    product = ForeignKey(Product, on_delete=CASCADE)
    weight = FloatField(default=100)

    def __str__(self):
        return self.product.name


class Day(Model):
    user = ForeignKey('auth.User', on_delete=CASCADE)
    date = DateField(default=localdate)
    meal = ManyToManyField(Meal)
    class Meta:
        constraints = [UniqueConstraint(fields=['user', 'date'],name='unique date')]

    def __str__(self):
        return '{} - {}'.format(str(self.date),self.user)

