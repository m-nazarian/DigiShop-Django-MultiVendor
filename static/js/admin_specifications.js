document.addEventListener('DOMContentLoaded', function() {
    const categorySelect = document.querySelector('#id_category');
    const specsField = document.querySelector('#id_specifications');

    // کانتینر اصلی
    const container = document.createElement('div');
    container.id = 'dynamic-specs-container';
    container.className = 'mt-4 space-y-4';

    specsField.parentNode.insertBefore(container, specsField.nextSibling);
    specsField.style.display = 'none';

    let currentSpecs = {};
    try {
        currentSpecs = JSON.parse(specsField.value || '{}');
    } catch(e) {
        currentSpecs = {};
    }

    // تابع ساخت گروه (آکاردئون)
    function createGroup(groupName, attributes) {
        // 1. باکس کلی گروه
        const groupDiv = document.createElement('div');
        groupDiv.className = 'border border-gray-200 rounded-lg bg-white shadow-sm overflow-hidden mb-4';

        // 2. هدر گروه (قابل کلیک)
        const header = document.createElement('div');
        header.className = 'bg-gray-100 px-4 py-3 cursor-pointer flex justify-between items-center hover:bg-gray-200 transition';
        header.innerHTML = `
            <span class="font-bold text-gray-700 text-sm">${groupName}</span>
            <span class="text-xs text-gray-500">(${attributes.length} ویژگی) ▼</span>
        `;

        // 3. بدنه گروه (محل اینپوت‌ها)
        const body = document.createElement('div');
        body.className = 'p-4 grid grid-cols-1 md:grid-cols-2 gap-4';
        body.style.display = 'grid';

        // عملکرد باز و بسته شدن
        header.addEventListener('click', () => {
            if (body.style.display === 'none') {
                body.style.display = 'grid';
                header.querySelector('span:last-child').innerText = `(${attributes.length} ویژگی) ▼`;
            } else {
                body.style.display = 'none';
                header.querySelector('span:last-child').innerText = `(${attributes.length} ویژگی) ▲`;
            }
        });

        // 4. ساخت اینپوت‌ها
        attributes.forEach(attr => {
            const wrapper = document.createElement('div');

            const labelEl = document.createElement('label');
            labelEl.innerText = attr.label;
            labelEl.className = 'block text-xs font-bold text-gray-500 mb-1';

            const inputEl = document.createElement('input');
            inputEl.type = 'text';
            inputEl.value = currentSpecs[attr.key] || '';
            inputEl.dataset.key = attr.key;
            inputEl.className = 'vTextField w-full border-gray-300 rounded px-2 py-1 text-sm focus:ring focus:ring-red-200';

            inputEl.addEventListener('input', updateJsonField);

            wrapper.appendChild(labelEl);
            wrapper.appendChild(inputEl);
            body.appendChild(wrapper);
        });

        groupDiv.appendChild(header);
        groupDiv.appendChild(body);
        container.appendChild(groupDiv);
    }

    function updateJsonField() {
        const inputs = container.querySelectorAll('input');
        const newData = {};
        inputs.forEach(input => {
            if (input.value.trim()) {
                newData[input.dataset.key] = input.value.trim();
            }
        });
        specsField.value = JSON.stringify(newData, null, 4);
    }

    function fetchAttributes(categoryId) {
        container.innerHTML = '<p class="text-gray-500 text-xs p-2">در حال بارگذاری فرم‌های مشخصات...</p>';

        fetch(`/products/api/category-attributes/${categoryId}/`)
            .then(response => response.json())
            .then(data => {
                container.innerHTML = '';

                if (!data.groups || data.groups.length === 0) {
                    container.innerHTML = '<p class="text-orange-500 text-xs p-2">هیچ گروه ویژگی‌ای تعریف نشده است.</p>';
                    specsField.style.display = 'block';
                    return;
                }

                specsField.style.display = 'none';

                data.groups.forEach(group => {
                    createGroup(group.group_name, group.attributes);
                });
            })
            .catch(err => {
                console.error(err);
                container.innerHTML = '<p class="text-red-500">خطا در دریافت ویژگی‌ها</p>';
            });
    }

    if (categorySelect) {
        categorySelect.addEventListener('change', function() {
            if (this.value) fetchAttributes(this.value);
            else container.innerHTML = '';
        });

        if (categorySelect.value) {
            fetchAttributes(categorySelect.value);
        }
    }
});