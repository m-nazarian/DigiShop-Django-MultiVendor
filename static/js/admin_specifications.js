document.addEventListener('DOMContentLoaded', function() {
    const categorySelect = document.querySelector('#id_category');
    const specsField = document.querySelector('#id_specifications');

    // کانتینر اصلی
    const container = document.createElement('div');
    container.id = 'dynamic-specs-container';
    container.className = 'mt-4 space-y-4';

    if (specsField) {
        specsField.parentNode.insertBefore(container, specsField.nextSibling);
        specsField.style.display = 'none';
    }

    let currentSpecs = {};
    try {
        currentSpecs = JSON.parse(specsField.value || '{}');
    } catch(e) {
        currentSpecs = {};
    }

    function createGroup(groupName, attributes) {
        // باکس گروه
        const groupDiv = document.createElement('div');
        groupDiv.className = 'border border-gray-200 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-900 shadow-sm overflow-hidden mb-4';

        // هدر گروه
        const header = document.createElement('div');
        header.className = 'bg-gray-50 dark:bg-gray-800 px-4 py-3 cursor-pointer flex justify-between items-center border-b border-gray-100 dark:border-gray-700';
        header.innerHTML = `
            <span class="font-bold text-gray-700 dark:text-gray-200 text-sm flex items-center gap-2">
                <span class="w-1 h-4 bg-red-500 rounded-full block"></span>
                ${groupName}
            </span>
            <span class="text-xs text-gray-500 dark:text-gray-400 group-indicator">(${attributes.length} ویژگی) ▼</span>
        `;

        // بدنه گروه
        const body = document.createElement('div');
        body.className = 'p-4 grid grid-cols-1 md:grid-cols-2 gap-4 bg-white dark:bg-gray-900'; // پس‌زمینه بدنه تیره در دارک مود
        body.style.display = 'grid';

        header.addEventListener('click', () => {
            const indicator = header.querySelector('.group-indicator');
            if (body.style.display === 'none') {
                body.style.display = 'grid';
                indicator.innerText = `(${attributes.length} ویژگی) ▼`;
            } else {
                body.style.display = 'none';
                indicator.innerText = `(${attributes.length} ویژگی) ▲`;
            }
        });

        // ساخت فیلدها
        attributes.forEach(attr => {
            const wrapper = document.createElement('div');
            wrapper.className = 'flex flex-col';

            const labelEl = document.createElement('label');
            labelEl.innerText = attr.label;
            // رنگ لیبل در دارک مود روشن‌تر شد
            labelEl.className = 'block text-xs font-bold text-gray-600 dark:text-gray-300 mb-1.5';

            // تغیییر مهم: استفاده از Textarea به جای Input
            const inputEl = document.createElement('textarea');
            inputEl.value = currentSpecs[attr.key] || '';
            inputEl.dataset.key = attr.key;
            inputEl.rows = 2; // ارتفاع پیش‌فرض

            // کلاس‌های اصلاح شده برای کنتراست بالا
            inputEl.className = `
                w-full 
                bg-gray-50 dark:bg-gray-800 
                text-gray-900 dark:text-gray-100 
                border border-gray-300 dark:border-gray-600 
                rounded-md px-3 py-2 text-sm 
                focus:ring-1 focus:ring-red-500 focus:border-red-500 
                placeholder-gray-400 
                transition-colors
                resize-y
            `;

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
        const inputs = container.querySelectorAll('textarea'); // تغییر سلکتور به textarea
        const newData = {};
        inputs.forEach(input => {
            if (input.value.trim()) {
                newData[input.dataset.key] = input.value.trim();
            }
        });
        specsField.value = JSON.stringify(newData, null, 4);
    }

    function fetchAttributes(categoryId) {
        container.innerHTML = '<div class="p-4 text-center text-gray-500 dark:text-gray-400 text-xs">در حال دریافت ویژگی‌ها...</div>';

        fetch(`/products/api/category-attributes/${categoryId}/`)
            .then(response => response.json())
            .then(data => {
                container.innerHTML = '';

                if (!data.groups || data.groups.length === 0) {
                    container.innerHTML = `
                        <div class="p-4 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg text-center">
                            <p class="text-yellow-700 dark:text-yellow-500 text-sm">هیچ ویژگی خاصی برای این دسته‌بندی تعریف نشده است.</p>
                        </div>
                    `;
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