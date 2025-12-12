from django import forms
from .models import Address

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['title', 'recipient_name', 'phone_number', 'province', 'city', 'postal_code', 'full_address']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full p-2 border rounded-lg', 'placeholder': 'مثال: خانه'}),
            'recipient_name': forms.TextInput(attrs={'class': 'w-full p-2 border rounded-lg'}),
            'phone_number': forms.TextInput(attrs={'class': 'w-full p-2 border rounded-lg'}),
            'province': forms.TextInput(attrs={'class': 'w-full p-2 border rounded-lg'}),
            'city': forms.TextInput(attrs={'class': 'w-full p-2 border rounded-lg'}),
            'postal_code': forms.TextInput(attrs={'class': 'w-full p-2 border rounded-lg'}),
            'full_address': forms.Textarea(attrs={'class': 'w-full p-2 border rounded-lg', 'rows': 3}),
        }