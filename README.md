# Calorie Counter App

## Idea
Calorie Counter App is a Django web app, which is based on apps like Fitatu or Yazio. 
Currently the app is still in development mode and provides the basic features: user login, searching meals by ean or name, 
adding meals to a chosen date and showing all meals and total sum of macronutriens and kcal for chosen date.
The app uses an internal database (SQLite) and connects to external database using [Open Food Facts API](https://github.com/openfoodfacts/openfoodfacts-python).


Upcoming features and tasks:
- the app deployment
- user registration
- change of main logic of the post method in ProfileView
- improvement of the profile.html template
- showing stats for a given period
- removing meals

![Alt text](images/example3.png?raw=true "example.png")


