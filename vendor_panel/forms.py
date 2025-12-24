from django import forms
from products.models import Product


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        # فیلدهایی که فروشنده مجاز است پر کند
        fields = ['category', 'brand', 'model_name', 'title_desc', 'description', 'image', 'price', 'discount_price', 'stock',
                  'is_available']

        widgets = {
            'model_name': forms.TextInput(attrs={'class': 'w-full p-2 border rounded-lg', 'placeholder': 'مثال: iPhone 13 Pro'}),
            'title_desc': forms.TextInput(attrs={'class': 'w-full p-2 border rounded-lg', 'placeholder': 'مثال: دو سیم‌کارت ظرفیت 256 گیگابایت'}),
            'slug': forms.TextInput(attrs={'class': 'w-full p-2 border rounded-lg'}),
            'price': forms.NumberInput(attrs={'class': 'w-full p-2 border rounded-lg'}),
            'discount_price': forms.NumberInput(attrs={'class': 'w-full p-2 border rounded-lg'}),
            'stock': forms.NumberInput(attrs={'class': 'w-full p-2 border rounded-lg'}),
            'category': forms.Select(attrs={'class': 'w-full p-2 border rounded-lg'}),
            'brand': forms.Select(attrs={'class': 'w-full p-2 border rounded-lg'}),
        }