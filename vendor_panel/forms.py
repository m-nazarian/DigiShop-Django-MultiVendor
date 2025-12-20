from django import forms
from products.models import Product


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        # فیلدهایی که فروشنده مجاز است پر کند
        fields = ['category', 'brand', 'name', 'description', 'image', 'price', 'discount_price', 'stock',
                  'is_available']

        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full p-2 border rounded-lg'}),
            'slug': forms.TextInput(attrs={'class': 'w-full p-2 border rounded-lg'}),
            'price': forms.NumberInput(attrs={'class': 'w-full p-2 border rounded-lg'}),
            'discount_price': forms.NumberInput(attrs={'class': 'w-full p-2 border rounded-lg'}),
            'stock': forms.NumberInput(attrs={'class': 'w-full p-2 border rounded-lg'}),
            'category': forms.Select(attrs={'class': 'w-full p-2 border rounded-lg'}),
            'brand': forms.Select(attrs={'class': 'w-full p-2 border rounded-lg'}),
        }