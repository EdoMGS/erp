from datetime import date
from decimal import Decimal

from celery import shared_task

from .models import Bonus, Meal, Travel


@shared_task
def check_annual_limits():
    current_year = date.today().year
    meals = Meal.objects.filter(date__year=current_year)
    travels = Travel.objects.filter(date__year=current_year)
    bonuses = Bonus.objects.filter(year=current_year)

    meal_total = sum(meal.amount for meal in meals)
    travel_total = sum(travel.amount for travel in travels)
    bonus_total = sum(bonus.amount for bonus in bonuses)

    meal_limit = Decimal("5000.00")
    travel_limit = Decimal("10000.00")
    bonus_limit = Decimal("15000.00")

    if meal_total > meal_limit:
        print(f"Meal limit exceeded: {meal_total} > {meal_limit}")
    if travel_total > travel_limit:
        print(f"Travel limit exceeded: {travel_total} > {travel_limit}")
    if bonus_total > bonus_limit:
        print(f"Bonus limit exceeded: {bonus_total} > {bonus_limit}")
