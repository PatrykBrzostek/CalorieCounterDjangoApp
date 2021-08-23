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

    def get(self, request, *args, **kwargs):
        current_user = request.user
        if current_user.username == self.kwargs['username']: #change logic
            try:
                datetime.strptime(self.kwargs['url_date'], '%Y-%m-%d')
            except ValueError:
                raise Http404
        else:
            raise Http404

        return render(request, self.template_name, {'name_form':self.name_form, 'dates': self.dates, 'quick_meal_form': self.quick_meal_form, 'meals': self.meals})

    def post(self, request, *args, **kwargs):
        #change schemat of below conditions to saving final date in variable and return redirect at the end
        if request.POST.get('quick_meal'):
            if self.quick_meal_form.is_valid():  # change to detect submit
                unique_ean = 'N' + re.sub(r"[^0-9]", "", str(datetime.now()))[2:]
                new_product = Product.objects.create(ean=unique_ean, name='Quick Meal',
                                                     carbohydrates=self.quick_meal_form.cleaned_data['carbohydrates'],
                                                     protein=self.quick_meal_form.cleaned_data['protein'],
                                                     fat=self.quick_meal_form.cleaned_data['fat'])
                quick_meal = Meal.objects.create(product_id=new_product.id)
                updated_day, _ = Day.objects.get_or_create(user_id=request.user.id, date=self.url_date)
                updated_day.save()
                updated_day.meal.add(quick_meal)
                return redirect('/profile/{}/{}/'.format(self.username, self.url_date))
            else:
                self.name_form.errors.clear()
        elif request.POST.get("yesterday"):
            return redirect('/profile/{}/{}/'.format(self.username,self.dates['yesterday']))
        elif request.POST.get("tommorow"):
            return redirect('/profile/{}/{}/'.format(self.username,self.dates['tomorrow']))
        elif request.POST.get('gotodate'): # change this condition to detect button
            if self.name_form.is_valid():
                if self.name_form.cleaned_data['name']:
                    new_date = str(self.name_form.cleaned_data['name'])
                    return redirect('/profile/{}/{}/'.format(self.username, new_date))
            else:
                self.quick_meal_form.errors.clear() # temporary - error shows, when name_form is not valid
                pass

        else:
            pass
        return render(request, self.template_name, {'name_form':self.name_form, 'dates': self.dates, 'quick_meal_form': self.quick_meal_form, 'meals': self.meals})

    def dispatch(self, request, *args, **kwargs):
        self.url_date=kwargs['url_date']
        self.name_form = NameForm(request.POST or None, initial={'name': kwargs['url_date']})
        self.quick_meal_form = QuickMealForm(request.POST or None, initial={'carbohydrates': 0.0, 'protein': 0.0, 'fat':0.0})

        self.username=request.user.username
        day = Day.objects.filter(date=self.url_date).filter(user=request.user).first()

        if day:
            self.meals = day.meal.all()
            # df = pd.DataFrame(list(meals.values('product__ean', 'product__fat', 'weight')))
            # html_df = df.to_html()
            # print(html_df)
        else:
            self.meals = []
            html_df = 0

        datetime_object = datetime.strptime(self.url_date, '%Y-%m-%d').date()
        tomorrow_datetime_object=datetime_object+timedelta(days=1)
        yesterday_datatime_object=datetime_object-timedelta(days=1)
        tomorrow_date=tomorrow_datetime_object.strftime("%Y-%m-%d")
        yesterday_date=yesterday_datatime_object.strftime("%Y-%m-%d")

        self.dates = {'yesterday':yesterday_date, 'today': self.url_date, 'tomorrow': tomorrow_date}
        return super(ProfileView, self).dispatch(request, *args, **kwargs)


# def test_view(request, username, url_date):
#     current_user = request.user
#     if current_user.username == username:
#         try:
#             datetime.strptime(url_date, '%Y-%m-%d')
#         except ValueError:
#             raise Http404
#
#         name_form = NameForm(request.POST or None, initial={'name': url_date})
#
#         datetime_object = datetime.strptime(url_date, '%Y-%m-%d').date()
#         tomorrow_datetime_object=datetime_object+timedelta(days=1)
#         yesterday_datatime_object=datetime_object-timedelta(days=1)
#         tomorrow_date=tomorrow_datetime_object.strftime("%Y-%m-%d")
#         yesterday_date=yesterday_datatime_object.strftime("%Y-%m-%d")
#
#         dates = {'yesterday':yesterday_date, 'today': url_date, 'tomorrow': tomorrow_date}
#
#         quick_meal_form = QuickMealForm(request.POST or None, initial={'carbohydrates': 0.0, 'protein': 0.0, 'fat':0.0})
#
#         if request.method == 'POST':
#             #change schemat of below conditions to saving final date in variable and return redirect at the end
#             if request.POST.get('quick_meal'):
#                 print('here')
#                 if quick_meal_form.is_valid(): #change to detect submit
#                     unique_ean='N'+re.sub(r"[^0-9]","",str(datetime.now()))[2:]
#                     new_product = Product.objects.create(ean=unique_ean, name='Quick Meal', carbohydrates=quick_meal_form.cleaned_data['carbohydrates'], protein=quick_meal_form.cleaned_data['protein'], fat=quick_meal_form.cleaned_data['fat'])
#                     quick_meal = Meal.objects.create(product_id=new_product.id)
#                     updated_day, _ = Day.objects.get_or_create(user_id=current_user.id, date=url_date)
#                     updated_day.save()
#                     updated_day.meal.add(quick_meal)
#                     return redirect('/profile/{}/{}/'.format(username,url_date))
#             elif request.POST.get("yesterday"):
#                 return redirect('/profile/{}/{}/'.format(username,yesterday_date))
#             elif request.POST.get("tommorow"):
#                 return redirect('/profile/{}/{}/'.format(username,tomorrow_date))
#             elif request.POST.get('gotodate'): # change this condition to detect button
#                 if name_form.is_valid():
#                     if name_form.cleaned_data['name']:
#                         new_date = str(name_form.cleaned_data['name'])
#                         return redirect('/profile/{}/{}/'.format(username, new_date))
#                 else:
#                     quick_meal_form.errors.clear() # temporary - error shows, when name_form is not valid
#                     pass
#
#             else:
#                 pass
#
#
#
#
#         day = Day.objects.filter(date=url_date).filter(user=current_user).first()
#
#         if day:
#             meals = day.meal.all()
#             print(meals)
#             df = pd.DataFrame(list(meals.values('product__ean', 'product__fat', 'weight')))
#             html_df=df.to_html()
#             print(html_df)
#         else:
#             meals = []
#             html_df=0
#
#     else:
#         raise Http404
#
#     return render(request, 'profile.html', {'user':current_user.username, 'dates': dates, 'meals':meals, 'name_form':name_form, 'quick_meal_form': quick_meal_form, 'df': html_df})


class MyLoginView(auth_views.LoginView):

    def get_success_url(self):
        today=date.today().strftime("%Y-%m-%d")
        url ='/profile/{}/{}'.format(self.request.user.username,today)
        return url
