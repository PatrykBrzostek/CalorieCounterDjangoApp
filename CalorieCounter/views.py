from django.shortcuts import render, redirect, reverse
from django.http import Http404
from django.contrib.auth import views as auth_views
from django.views import View

import re
from datetime import date, datetime, timedelta
import pandas as pd
from .models import Day, Meal, Product
from .forms import *

class ProfileView(View):
    template_name = 'profile.html'

    def dispatch(self, request, *args, **kwargs):
        self.url_date=kwargs['url_date']
        self.username=request.user.username #kwargs['username']
        self.__is_correct_url(self.username, kwargs['username'], self.url_date)
        self.date_form = DateForm(request.POST or None, initial={'date': self.url_date})
        self.quick_meal_form = QuickMealForm(request.POST or None, initial={'carbohydrates': 0.0, 'protein': 0.0, 'fat':0.0})

        self.dates = self.__get_new_dates(self.url_date)
        self.meals = self.__get_meals_from_date(self.url_date, request.user)

        return super(ProfileView, self).dispatch(request, *args, **kwargs)

    def __is_correct_url(self, request_user_username, url_username, url_date):
        if request_user_username == url_username:
            try:
                datetime.strptime(url_date, '%Y-%m-%d')
            except ValueError:
                raise Http404
        else:
            raise Http404

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {'date_form':self.date_form, 'quick_meal_form': self.quick_meal_form, 'dates': self.dates, 'meals': self.meals})

    def post(self, request, *args, **kwargs):
        is_redirected=False
        new_date = self.url_date
        if request.POST.get('quick_meal'):
            if self.quick_meal_form.is_valid():  # change to detect submit
                self.__add_quick_meal(request.user.id, self.url_date, self.quick_meal_form.cleaned_data['carbohydrates'], self.quick_meal_form.cleaned_data['protein'], self.quick_meal_form.cleaned_data['fat'])
                is_redirected=True
            else:
                self.date_form.errors.clear()
        elif request.POST.get("previous"):
            new_date = self.dates['previous']
            is_redirected = True
        elif request.POST.get("next"):
            new_date = self.dates['next']
            is_redirected = True
        elif request.POST.get('gotodate'):
            if self.date_form.is_valid():
                if self.date_form.cleaned_data['date']:
                    new_date = str(self.date_form.cleaned_data['date'])
                    is_redirected = True
            else:
                self.quick_meal_form.errors.clear() #temporary - error shows, when name_form is not valid
        else:
            pass

        if is_redirected:
            return redirect('/profile/{}/{}/'.format(self.username, new_date))
        else:
            return render(request, self.template_name, {'date_form':self.date_form,'quick_meal_form': self.quick_meal_form, 'dates': self.dates, 'meals': self.meals})

    def __add_quick_meal(self, request_user_id, url_date, c, p, f):
        unique_ean = 'N' + re.sub(r"[^0-9]", "", str(datetime.now()))[2:]
        new_product = Product.objects.create(ean=unique_ean, name='Quick Meal',
                                             carbohydrates=c,
                                             protein=p,
                                             fat=f)
        quick_meal = Meal.objects.create(product_id=new_product.id)
        updated_day, _ = Day.objects.get_or_create(user_id=request_user_id, date=url_date)
        updated_day.save()
        updated_day.meal.add(quick_meal)

    def __get_meals_from_date(self, url_date, request_user):
        day = Day.objects.filter(date=url_date).filter(user=request_user).first()

        if day:
            meals = day.meal.all()
            # df = pd.DataFrame(list(meals.values('product__ean', 'product__fat', 'weight')))
        else:
            meals = []
        return meals

    def __get_new_dates(self, url_date):
        datetime_object = datetime.strptime(url_date, '%Y-%m-%d').date()
        next_datetime_object=datetime_object+timedelta(days=1)
        next_date=next_datetime_object.strftime("%Y-%m-%d")

        previous_datatime_object=datetime_object-timedelta(days=1)
        previous_date=previous_datatime_object.strftime("%Y-%m-%d")

        new_dates = {'previous':previous_date, 'current': url_date, 'next': next_date}
        return new_dates

class MyLoginView(auth_views.LoginView):

    def get_success_url(self):
        today=date.today().strftime("%Y-%m-%d")
        url ='/profile/{}/{}'.format(self.request.user.username,today)
        return url
