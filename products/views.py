from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404
from .models import ProductAttribute, Category


@staff_member_required
def get_category_attributes(request, category_id):
    # 1. پیدا کردن دسته‌بندی انتخاب شده
    current_category = get_object_or_404(Category, id=category_id)

    # 2. پیدا کردن تمام اجداد (پدر، پدر بزرگ و...)
    category_family_ids = [current_category.id]
    parent = current_category.parent

    # تا وقتی که پدر وجود دارد، برو بالا
    while parent:
        category_family_ids.append(parent.id)
        parent = parent.parent

    # 3. گرفتن ویژگی‌هایی که متعلق به این خانواده هستند
    attributes = ProductAttribute.objects.filter(
        category_id__in=category_family_ids
    ).values('key', 'label')

    return JsonResponse({'attributes': list(attributes)})