document.addEventListener('DOMContentLoaded', function () {
    // Форматирование цены
    function formatPrice(price) {
        if (price === undefined || price === null) return '—';
        return new Intl.NumberFormat('ru-RU').format(price) + ' ₽';
    }

    // Перевод настроек графики
    function translateGraphicsSettings(setting, value) {
        const translations = {
            'quality': {
                'low': 'Низкие',
                'medium': 'Средние',
                'high': 'Высокие',
                'ultra': 'Ультра'
            },
            'resolution': {
                '720': '720p (HD)',
                '1080': '1080p (Full HD)',
                '1440': '1440p (QHD)',
                '2160': '2160p (4K UHD)'
            },
            'dlss': {
                'disabled': 'Выключено',
                'performance': 'Производительность',
                'balanced': 'Сбалансированный',
                'quality': 'Качество',
                'ultra_performance': 'Ультра производительность'
            },
            'fsr': {
                'disabled': 'Выключено',
                'performance': 'Производительность',
                'balanced': 'Сбалансированный',
                'quality': 'Качество',
                'ultra_performance': 'Ультра производительность'
            },
            'ray_tracing': value => value ? 'Включено' : 'Выключено',
            'target_fps': value => `${value} FPS`
        };

        if (translations[setting]) {
            if (typeof translations[setting] === 'object') {
                return translations[setting][value?.toLowerCase?.()] || value;
            } else if (typeof translations[setting] === 'function') {
                return translations[setting](value);
            }
        }
        return value;
    }

    // Обновление настроек игры
    function updateGameSettings(data) {
        const game = data.user_selections?.game;
        if (!game) return;

        document.querySelector('.game-title').textContent = game.title?.replace(/_/g, ' ') || '—';

        const settingsMap = {
            'quality': 'Графика',
            'resolution': 'Разрешение',
            'target_fps': 'Частота кадров',
            'ray_tracing': 'Трассировка лучей',
            'dlss': 'NVIDIA DLSS',
            'fsr': 'AMD FSR'
        };

        Object.entries(settingsMap).forEach(([key, label]) => {
            const value = game.graphics_settings?.[key];
            const translated = value !== undefined ? translateGraphicsSettings(key, value) : '-';

            const row = [...document.querySelectorAll('.settings-row')]
                .find(r => r.querySelector('.settings-label')?.textContent === label);

            if (row) {
                row.querySelector('.settings-value').textContent = translated;
            }
        });
    }

    // Обновление информации о бюджете
    function updateBudget(data) {
        const budget = data.user_selections?.budget;
        if (!budget) return;

        document.querySelector('.budget-amount').textContent = formatPrice(budget.amount);

        let total = 0;
        const components = data.components || {};

        const keys = ['gpu', 'cpu', 'dimm', 'ssd', 'motherboard', 'psu', 'case_fan', 'pc_case', 'cooler'];

        for (const key of keys) {
            const comp = components[key];
            const price = comp?.price ?? comp?.data?.price;
            if (typeof price === 'number') total += price;
        }

        document.querySelector('.final-price').textContent = formatPrice(total);
        const diff = total - budget.amount;

        const diffElem = document.querySelector('.budget-difference');
        diffElem.textContent = formatPrice(Math.abs(diff));
        diffElem.classList.toggle('over-budget', diff > 0);
        diffElem.classList.toggle('under-budget', diff <= 0);
    }

    // Получение спецификаций компонента
    function getComponentSpecs(key, comp) {
        const d = comp.data || comp;
        const s = [];

        switch (key) {
            case 'gpu':
                if (d.gpu_model) s.push(`Модель: ${d.gpu_model}`);
                if (d.vram_size) s.push(`Память: ${d.vram_size} ГБ`);
                if (d.base_clock && d.boost_clock) s.push(`Частота: ${d.base_clock}-${d.boost_clock} МГц`);
                if (d.tdp) s.push(`TDP: ${d.tdp} Вт`);
                break;
            case 'cpu':
                if (d.socket) s.push(`Сокет: ${d.socket}`);
                if (d.performance_cores) s.push(`Ядра: ${d.performance_cores}`);
                if (d.base_frequency && d.turbo_frequency) s.push(`Частота: ${d.base_frequency}-${d.turbo_frequency} ГГц`);
                if (d.tdp) s.push(`TDP: ${d.tdp} Вт`);
                break;
            case 'cooler':
                if (d.type) s.push(`Тип: ${d.type === 'air_cooler' ? 'Воздушный' : 'Жидкостный'}`);
                if (d.socket) s.push(`Сокет: ${d.socket}`);
                if (d.tdp) s.push(`TDP: ${d.tdp} Вт`);
                break;
            case 'ssd':
                if (d.capacity) s.push(`Объем: ${d.capacity} ГБ`);
                if (d.max_read_speed && d.max_write_speed)
                    s.push(`Скорость: ${d.max_read_speed}/${d.max_write_speed} МБ/с`);
                break;
            case 'dimm':
                if (d.total_memory) s.push(`Объем: ${d.total_memory} ГБ`);
                if (d.memory_type) s.push(`Тип: ${d.memory_type}`);
                if (d.frequency) s.push(`Частота: ${d.frequency} МГц`);
                break;
            case 'motherboard':
                if (d.socket) s.push(`Сокет: ${d.socket}`);
                if (d.chipset) s.push(`Чипсет: ${d.chipset}`);
                if (d.memory_type) s.push(`Память: ${d.memory_type}`);
                break;
            case 'psu':
                if (d.wattage) s.push(`Мощность: ${d.wattage} Вт`);
                if (d.certification_80plus) s.push(`Сертификат: 80+ ${d.certification_80plus}`);
                break;
            case 'case_fan':
                if (d.fan_size) s.push(`Размер: ${d.fan_size} мм`);
                if (d.max_airflow) s.push(`Поток: ${d.max_airflow} CFM`);
                if (d.max_noise_level) s.push(`Шум: ${d.max_noise_level} дБ`);
                break;
            case 'pc_case':
                if (d.motherboard_form_factors) s.push(`Форм-фактор: ${d.motherboard_form_factors}`);
                if (d.max_gpu_length) s.push(`Длина GPU: до ${d.max_gpu_length}`);
                break;
        }

        return s;
    }

    // Отрисовка таблицы компонентов
    function updateComponentsTable(data) {
        const tbody = document.querySelector('.components-table tbody');
        if (!tbody) return;

        tbody.innerHTML = '';

        const names = {
            'gpu': 'Видеокарта',
            'cpu': 'Процессор',
            'cooler': 'Кулер CPU',
            'ssd': 'SSD',
            'dimm': 'ОЗУ',
            'motherboard': 'Материнская плата',
            'psu': 'Блок питания',
            'case_fan': 'Вентиляторы',
            'pc_case': 'Корпус'
        };

        const order = ['gpu', 'cpu', 'dimm', 'ssd', 'motherboard', 'psu', 'case_fan', 'pc_case', 'cooler'];

        for (const key of order) {
            const comp = data.components?.[key];
            if (!comp) continue;

            const row = document.createElement('tr');

            const typeCell = document.createElement('td');
            typeCell.textContent = names[key] || key;
            row.appendChild(typeCell);

            const nameCell = document.createElement('td');
            nameCell.textContent = comp.name || comp.data?.name || '—';
            row.appendChild(nameCell);

            const imgCell = document.createElement('td');
            const img = document.createElement('img');
            img.src = comp.image_url || comp.data?.image_url || 'https://via.placeholder.com/80';
            img.alt = names[key] || key;
            img.className = 'component-image';
            imgCell.appendChild(img);
            row.appendChild(imgCell);

            const priceCell = document.createElement('td');
            priceCell.className = 'price-value';
            const price = comp.price ?? comp.data?.price;
            priceCell.textContent = formatPrice(price);
            row.appendChild(priceCell);

            const specsCell = document.createElement('td');
            const specsList = document.createElement('div');
            specsList.className = 'specs-list';
            getComponentSpecs(key, comp).forEach(spec => {
                const badge = document.createElement('span');
                badge.className = 'spec-badge';
                badge.textContent = spec;
                specsList.appendChild(badge);
            });
            specsCell.appendChild(specsList);
            row.appendChild(specsCell);

            tbody.appendChild(row);
        }
    }

    // Основная обработка ответа от сервера
    function processServerResponse(data) {
        if (data.status !== 'ok') {
            console.error('Ошибка от сервера:', data.message);
            document.querySelector('.error-message').textContent = data.message || 'Произошла ошибка.';
            return;
        }

        updateGameSettings(data);
        updateBudget(data);
        updateComponentsTable(data);

        document.querySelector('.loading-indicator').style.display = 'none';
    }

    // Загрузка конфигурации
    async function loadConfiguration() {
        const configId = new URLSearchParams(window.location.search).get('config_id');
        if (!configId) {
            console.error('config_id не найден в URL');
            return;
        }

        try {
            const res = await fetch(`/api/components/result?config_id=${configId}`);
            const data = await res.json();
            processServerResponse(data);
        } catch (err) {
            console.error('Ошибка при загрузке конфигурации:', err);
            document.querySelector('.error-message').textContent =
                'Ошибка при загрузке конфигурации. Попробуйте позже.';
            document.querySelector('.loading-indicator').style.display = 'none';
        }
    }

    // Запуск
    loadConfiguration();
});
