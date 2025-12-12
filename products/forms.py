from django import forms
from .models import Review


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['score', 'recommendation', 'comment']  # recommendation اضافه شد
        widgets = {
            'comment': forms.Textarea(attrs={
                'class': 'w-full p-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-red-500 focus:border-red-500 outline-none resize-none text-sm',
                'placeholder': 'متن دیدگاه خود را بنویسید...',
                'rows': 4
            }),
            'score': forms.Select(attrs={
                'class': 'w-full p-2 border border-gray-300 rounded-lg focus:ring-red-500 mb-4 text-sm'
            }, choices=[(i, f'{i} از 5') for i in range(5, 0, -1)]),

            'recommendation': forms.RadioSelect(attrs={'class': 'peer sr-only'})
        }