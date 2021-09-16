from django.shortcuts import render, redirect, reverse
from django.http import Http404
from django.contrib.auth import views as auth_views
from django.views import View

import openfoodfacts
from tools.caloriecalculator import Calculator
import re
import itertools
from datetime import date, datetime, timedelta
import pandas as pd
from .models import Day, Meal, Product
from .forms import *

class ProfileView(View):
    template_name = 'profile.html'
    calculator = Calculator()

    def dispatch(self, request, *args, **kwargs):
        self.url_date=kwargs['url_date']
        self.username=request.user.username #kwargs['username']
        self.__is_correct_url(self.username, kwargs['username'], self.url_date)
        self.date_form = DateForm(request.POST or None, initial={'date': self.url_date})
        self.quick_meal_form = QuickMealForm(request.POST or None, initial={'carbohydrates': 0.0, 'protein': 0.0, 'fat':0.0})
        self.search_form = SearchForm(request.POST or None)
        self.meal_form = MealForm(request.POST or None, initial={'portion': 100.0})

        self.dates = self.__get_new_dates(self.url_date)
        self.meals, self.df = self.__get_meals_from_date(self.url_date, request.user)
        self.products = []

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

        return render(request, self.template_name, {'search_form':self.search_form,'date_form':self.date_form, 'meal_form': self.meal_form,
                                                    'quick_meal_form': self.quick_meal_form, 'dates': self.dates,
                                                    'meals': self.meals, 'df': self.df, 'products': self.products})

    def post(self, request, *args, **kwargs):
        is_redirected=False
        new_date = self.url_date
        if request.POST.get('quick_meal'):
            if self.quick_meal_form.is_valid():
                self.__add_quick_meal(request.user.id, self.url_date, self.quick_meal_form.cleaned_data['carbohydrates'], self.quick_meal_form.cleaned_data['protein'], self.quick_meal_form.cleaned_data['fat'])
                is_redirected=True
            else:
                self.date_form.errors.clear()
                self.search_form.errors.clear()
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
                self.quick_meal_form.errors.clear() # temporary - change the main logic of post method
                self.search_form.errors.clear()
        elif request.POST.get('search'):
            if self.search_form.is_valid():
                self.__search(request.user.id, self.url_date, self.search_form.cleaned_data['query'])
                #is_redirected = True
            self.date_form.errors.clear() # temporary - change the main logic of post method
            self.quick_meal_form.errors.clear()
            self.meal_form.errors.clear()
        elif request.POST.get('add_meal'):
            if self.meal_form.is_valid():
                chosen_product_ean = request.POST.get('id')
                self.__add_meal(request.user.id, self.url_date, Product.objects.get(ean=chosen_product_ean), portion=self.meal_form.cleaned_data['portion'])
                is_redirected = True
        else:
            pass

        if is_redirected:
            return redirect('/profile/{}/{}/'.format(self.username, new_date))
        else:
            return render(request, self.template_name,
                          {'search_form': self.search_form, 'date_form': self.date_form, 'meal_form': self.meal_form,
                           'quick_meal_form': self.quick_meal_form, 'dates': self.dates,
                           'meals': self.meals, 'df': self.df, 'products': self.products})

    def __search(self, request_user_id, url_date, query):
        if query.isdigit():
            self.__search_by_ean(request_user_id, url_date, query)
        else:
            self.__search_by_name(request_user_id, url_date, query)

    def __search_by_name(self, request_user_id, url_date, name, max_number=5):
        internal_products=list(Product.objects.filter(name__icontains=name))[:max_number]
        self.products.extend(internal_products)

        try:
            results = openfoodfacts.products.search_all(name)
            remaining_space = max_number - len(internal_products)
        except Exception:
            remaining_space=0
        while(remaining_space):
            try:
                off_product = next(results)
                try:
                    product = Product.objects.get(ean=off_product['code'])
                    if not self.__is_in_products_list(product):
                        self.products.append(product)
                        remaining_space-=1
                    else:
                        continue
                except Product.DoesNotExist:
                    try:
                        product = Product.objects.create(name=off_product['product_name'], ean=off_product['_id'],
                                                         carbohydrates=off_product['nutriments']['carbohydrates_100g'],
                                                         protein=off_product['nutriments']['proteins_100g'],
                                                         fat=off_product['nutriments']['fat_100g'],
                                                         kcal=off_product['nutriments']['energy-kcal_100g'])
                        self.products.append(product)
                        remaining_space -= 1
                    except KeyError as e:
                        print('KeyError: {}'.format(e))
            except StopIteration:
                break

    def __is_in_products_list(self, new_product):
        for product in self.products:
            if product.ean==new_product.ean:
                return True
        return False

    def __search_by_ean(self, request_user_id, url_date, ean):#function name to change
        try:
            product=Product.objects.get(ean=ean)
        except Product.DoesNotExist:
            product=None

        if not product:
            off_product = openfoodfacts.products.get_product(ean) #should be in try
            if off_product['status']:
                product = Product.objects.create(name=off_product['product']['product_name'], ean=ean,
                                                 carbohydrates=off_product['product']['nutriments']['carbohydrates_100g'], protein=off_product['product']['nutriments']['proteins_100g'],
                                                 fat=off_product['product']['nutriments']['fat_100g'], kcal=off_product['product']['nutriments']['energy-kcal_100g'])

        if product:
            self.products.append(product)
        else:
            print('no such ean in database')

    def __add_meal(self, request_user_id, url_date, product, portion=100):
        new_meal = Meal.objects.create(product_id=product.id, weight=portion)
        updated_day, _ = Day.objects.get_or_create(user_id=request_user_id, date=url_date)
        updated_day.save()
        updated_day.meal.add(new_meal)

    def __add_quick_meal(self, request_user_id, url_date, c, p, f):
        unique_ean = 'N' + re.sub(r"[^0-9]", "", str(datetime.now()))[2:]
        new_product = Product.objects.create(ean=unique_ean, name='Quick Meal',
                                             carbohydrates=c,
                                             protein=p,
                                             fat=f,
                                             kcal=self.calculator.count_calories(c,p,f))
        self.__add_meal(request_user_id, url_date, new_product)

    def __get_meals_from_date(self, url_date, request_user):
        day = Day.objects.filter(date=url_date).filter(user=request_user).first()

        if day:
            meals = day.meal.all()
            df = pd.DataFrame(list(meals.values('product__name', 'product__ean', 'weight', 'product__carbohydrates', 'product__protein', 'product__fat', 'product__kcal')))

            columns_to_calculate= ['product__carbohydrates', 'product__protein', 'product__fat', 'product__kcal']
            for column in columns_to_calculate:
                df[column] = [round(self.calculator.get_portions_scale(row['weight'])*row[column],2) for index, row in df.iterrows()]
            df['weight']=[str(row['weight'])+' g' if row['product__ean'][0]!='N' else '-' for index, row in df.iterrows()]
            df.loc['Total'] = round(df[columns_to_calculate].sum(),2)
            df.loc['Total'] = df.loc['Total'].fillna('')
            df = df.to_dict('index')
        else:
            meals = []
            df = []
        return meals, df

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
