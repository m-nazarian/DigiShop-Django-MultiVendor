document.addEventListener('DOMContentLoaded', function() {
    const categorySelect = document.querySelector('#id_category');
    const specsField = document.querySelector('#id_specifications'); // فیلد اصلی JSON

    // کانتینری که قراره اینپوت‌های ما توش ساخته بشه
    const container = document.createElement('div');
    container.id = 'dynamic-specs-container';
    container.style.marginTop = '10px';
    container.style.padding = '15px';
    container.style.border = '1px solid #e5e7eb';
    container.style.borderRadius = '8px';
    container.style.backgroundColor = '#f9fafb';

    // اضافه کردن کانتینر بعد از فیلد اصلی
    specsField.parentNode.insertBefore(container, specsField.nextSibling);

    // مخفی کردن فیلد اصلی JSON (اما پاکش نمی‌کنیم چون برای ذخیره لازمه)
    specsField.style.display = 'none'; // یا اگر میخوای ببینی چی میشه opacity 0.5 بذار

    // آبجکت برای نگهداری مقادیر فعلی
    let currentSpecs = {};
    try {
        currentSpecs = JSON.parse(specsField.value || '{}');
    } catch(e) {
        currentSpecs = {};
    }

    // تابع ساخت اینپوت
    function createInput(key, label, value = '') {
        const wrapper = document.createElement('div');
        wrapper.style.marginBottom = '10px';
        wrapper.style.display = 'flex';
        wrapper.style.flexDirection = 'column';

        const labelEl = document.createElement('label');
        labelEl.innerText = label;
        labelEl.style.marginBottom = '5px';
        labelEl.style.fontWeight = 'bold';
        labelEl.style.fontSize = '0.875rem';
        labelEl.style.color = '#374151';

        const inputEl = document.createElement('input');
        inputEl.type = 'text';
        inputEl.value = value;
        inputEl.dataset.key = key; // ذخیره کلید برای دسترسی بعدی
        inputEl.className = 'vTextField'; // کلاس استاندارد جنگو
        inputEl.style.width = '100%';
        inputEl.style.padding = '8px';
        inputEl.style.border = '1px solid #d1d5db';
        inputEl.style.borderRadius = '6px';

        // وقتی چیزی تایپ شد، JSON اصلی آپدیت بشه
        inputEl.addEventListener('input', updateJsonField);

        wrapper.appendChild(labelEl);
        wrapper.appendChild(inputEl);
        container.appendChild(wrapper);
    }

    // تابع آپدیت کردن فیلد مخفی JSON
    function updateJsonField() {
        const inputs = container.querySelectorAll('input');
        const newData = {};
        inputs.forEach(input => {
            if (input.value.trim()) {
                newData[input.dataset.key] = input.value.trim();
            }
        });
        specsField.value = JSON.stringify(newData, null, 4); // ذخیره در فیلد اصلی
    }

    // تابع گرفتن ویژگی‌ها از سرور
    function fetchAttributes(categoryId) {
        container.innerHTML = '<p style="color:#6b7280; font-size:12px;">در حال بارگذاری ویژگی‌ها...</p>';

        fetch(`/products/api/category-attributes/${categoryId}/`)
            .then(response => response.json())
            .then(data => {
                container.innerHTML = '';

                if (data.attributes.length === 0) {
                    container.innerHTML = '<p style="color:orange;">هیچ ویژگی خاصی برای این دسته‌بندی تعریف نشده است.</p>';
                    // اگر ویژگی نداشت، فیلد جیسون رو نشون بده شاید بخواد دستی بنویسه
                    specsField.style.display = 'block';
                    return;
                }

                specsField.style.display = 'none';

                data.attributes.forEach(attr => {
                    // اگر قبلا مقداری برای این ویژگی ذخیره شده بود، بیارش
                    const existingValue = currentSpecs[attr.key] || '';
                    createInput(attr.key, attr.label, existingValue);
                });
            })
            .catch(err => {
                console.error(err);
                container.innerHTML = '<p style="color:red;">خطا در دریافت ویژگی‌ها</p>';
                specsField.style.display = 'block';
            });
    }

    // ایونت تغییر دسته‌بندی
    if (categorySelect) {
        categorySelect.addEventListener('change', function() {
            if (this.value) {
                // اگر دسته‌بندی عوض شد، مقادیر قبلی رو پاک نکنیم بهتره؟
                // معمولا وقتی دسته‌بندی عوض میشه یعنی محصول کلا عوض شده، پس ریست میکنیم
                // اما اینجا برای UX بهتر، مقادیر قبلی رو نگه میداریم اگه کلید مشابه داشتن
                fetchAttributes(this.value);
            } else {
                container.innerHTML = '';
            }
        });

        // اجرای اولیه (برای حالت ویرایش محصول)
        if (categorySelect.value) {
            fetchAttributes(categorySelect.value);
        }
    }
});