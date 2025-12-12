from django import forms
from .models import Order

class OrderCreateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['full_name', 'phone_number', 'address']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3, 'class': 'w-full p-2 border rounded-lg'}),
            'full_name': forms.TextInput(attrs={'class': 'w-full p-2 border rounded-lg'}),
            'phone_number': forms.TextInput(attrs={'class': 'w-full p-2 border rounded-lg'}),
        }