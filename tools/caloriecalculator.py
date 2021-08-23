class Macronutrients:
    def __init__(self, name, calories_per_gram):
        self.name=name
        self.calories_per_gram=calories_per_gram

    def count_calories(self, grams):
        return grams*self.calories_per_gram

    def get_info(self):
        print('1 gram of {} has {} calories.'.format(self.name, self.calories_per_gram))


class Calculator:
    '''
    The calculator includes helpful methods to count calories in a meal.
    '''
    def __init__(self):
        self.carbohydrates=Macronutrients("carbohydrates", 4)
        self.protein=Macronutrients("protein", 4)
        self.fat=Macronutrients("fat", 9)

    def count_calories(self, amt_of_c, amt_of_p, amt_of_f):
        '''
        :param amt_of_c: grams of carbohydrates
        :param amt_of_p: grams of protein
        :param amt_of_f: grams of fat
        :return: amount of calories
        '''
        calories=self.carbohydrates.count_calories(amt_of_c)+self.protein.count_calories(amt_of_p)+self.fat.count_calories(amt_of_f)
        return calories

    @staticmethod
    def get_macro_per_100gram(amt_of_c, amt_of_p, amt_of_f, weight):
        '''
        :param amt_of_c: grams of carbohydrates in a meal
        :param amt_of_p: grams of protein in a meal
        :param amt_of_f: grams of fat in a meal
        :param weight: weight of a meal
        :return: grams of carbohydrates, protein and fat per 100gram
        '''
        ratio=weight/100
        return round(amt_of_c/ratio,2), round(amt_of_p/ratio,2), round(amt_of_f/ratio,2)

    @staticmethod
    def get_portions_scale(weight):
        '''
        Default weigth = 100g
        '''
        return weight/100