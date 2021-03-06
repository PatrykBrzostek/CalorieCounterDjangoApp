from django import forms
from crispy_forms.helper import FormHelper, Layout
from crispy_forms.layout import Submit, Div
from crispy_forms.bootstrap import FieldWithButtons

class DateForm(forms.Form):
    date = forms.DateField()

    def __init__(self, *args, **kwargs):
        super(DateForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_show_labels = False
        self.helper.layout = Layout(
            Div(
                FieldWithButtons('date', Submit(css_class="btn btn-dark", value="->", name="gotodate")),
                css_class='row',
            ),
        )


class QuickMealForm(forms.Form):
    carbohydrates = forms.FloatField(widget=forms.TextInput(attrs={'placeholder': '0.0'})) #placeholder looks the same as true text, so delete it or change style
    protein = forms.FloatField(widget=forms.TextInput(attrs={'placeholder': '0.0'}))
    fat = forms.FloatField(widget=forms.TextInput(attrs={'placeholder': '0.0'}))

    def __init__(self, *args, **kwargs):
        super(QuickMealForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col'
        self.helper.field_class = 'col-5'
        self.helper.layout = Layout(
            Div(
                Div('carbohydrates', css_class='col', ),
                Div('protein', css_class='col', ),
                Div('fat', css_class='col', ),
                Submit(css_class="btn btn-dark col", name='quick_meal', value="Add quick meal"),
                css_class='col',
            ),
        )

class SearchForm(forms.Form):
    query = forms.CharField()

    def __init__(self, *args, **kwargs):
        super(SearchForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_show_labels = False
        self.helper.layout = Layout(
            Div(
                FieldWithButtons('query', Submit(css_class="btn btn-dark", value="Search", name="search")),
            ),
        )


class MealForm(forms.Form):
    portion = forms.FloatField(widget=forms.TextInput(attrs={'placeholder': '100.0'}))

    def __init__(self, *args, **kwargs):
        super(MealForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_show_labels = False
        self.helper.layout = Layout(
            Div(
                FieldWithButtons('portion', Submit(css_class="btn btn-dark", value="Add meal", name="add_meal")),
            ),
        )