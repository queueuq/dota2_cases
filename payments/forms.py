from django import forms


class TopUpForm(forms.Form):
    amount = forms.IntegerField(label="Сумма, ₽", min_value=10, max_value=100000)
