from django import forms
from .models import Customer


class CustomerForm(forms.ModelForm):
    email = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Ваш Емейл'}))

    class Meta:
        model = Customer
        fields = ('email',)
