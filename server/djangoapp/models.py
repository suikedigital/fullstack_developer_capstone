from django.db import models
from django.utils.timezone import now
from django.core.validators import MaxValueValidator, MinValueValidator


class CarMake(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name

# <HINT> Create a Car Model model `class CarModel(models.Model):`:
# - Many-To-One relationship to Car Make model (One Car Make has many
# Car Models, using ForeignKey field)
# - Name
# - Type (CharField with a choices argument to provide limited choices
# such as Sedan, SUV, WAGON, etc.)
# - Year (IntegerField) with min value 2015 and max value 2023
# - Any other fields you would like to include in car model
# - __str__ method to print a car make object

class CarModel(models.Model):
    car_make = models.ForeignKey(CarMake, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    dealer_id = models.IntegerField()

    CAR_TYPES = [
        ('SEDAN', 'Sedan'),
        ('SUV', 'Suv'),
        ('WAGON','Wagon'),
    ]

    type = models.CharField(max_length=10, choices=CAR_TYPES, default='SUV')

    year = models.IntegerField(default=2025,
        validators=[
            MaxValueValidator(2025),
            MinValueValidator(2015)
        ]
    )

    def __str__(self):
        return self.name
