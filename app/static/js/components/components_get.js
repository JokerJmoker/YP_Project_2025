document.addEventListener('DOMContentLoaded', function() {
    console.log('[DEBUG] DOM полностью загружен, начинаем инициализацию');

    // Форматирование цены
    function formatPrice(price) {
        console.log('[DEBUG] formatPrice вызван с price:', price);
        if (price === undefined || price === null) {
            console.warn('[WARN] formatPrice: цена не определена');
            return '—';
        }
        
        try {
            const formatted = new Intl.NumberFormat('ru-RU').format(price) + ' ₽';
            console.log('[DEBUG] formatPrice успешно отформатировал цену:', formatted);
            return formatted;
        } catch (error) {
            console.error('[ERROR] formatPrice не смог отформатировать цену:', error);
            return price.toString() + ' ₽';
        }
    }

    // Перевод настроек графики
    function translateGraphicsSettings(setting, value) {
        console.log(`[DEBUG] translateGraphicsSettings вызван с setting=${setting}, value=${value}`);
        
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

        try {
            if (translations[setting]) {
                if (typeof translations[setting] === 'object') {
                    const result = translations[setting][value?.toLowerCase?.()] || value;
                    console.log(`[DEBUG] Переведено значение ${setting}: ${value} -> ${result}`);
                    return result;
                } else if (typeof translations[setting] === 'function') {
                    const result = translations[setting](value);
                    console.log(`[DEBUG] Переведено значение ${setting} через функцию: ${value} -> ${result}`);
                    return result;
                }
            }
            console.log(`[DEBUG] Перевод для ${setting} не найден, возвращаем оригинальное значение: ${value}`);
            return value;
        } catch (error) {
            console.error(`[ERROR] Ошибка при переводе значения ${setting}:`, error);
            return value;
        }
    }

    // Обновление настроек игры
    function updateGameSettings(data) {
        console.log('[DEBUG] updateGameSettings вызван с data:', data);
        
        const game = data.user_selections?.game;
        if (!game) {
            console.warn('[WARN] updateGameSettings: данные игры отсутствуют');
            return;
        }

        try {
            const gameTitle = game.title?.replace(/_/g, ' ') || '—';
            console.log(`[DEBUG] Устанавливаем название игры: ${gameTitle}`);
            document.querySelector('.game-title').textContent = gameTitle;

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
                console.log(`[DEBUG] Обрабатываем настройку ${key} (${label}):`, value);
                
                const translated = value !== undefined ? 
                    translateGraphicsSettings(key, value) : 
                    '-';
                
                console.log(`[DEBUG] Переведенное значение: ${translated}`);

                const row = [...document.querySelectorAll('.settings-row')]
                    .find(r => r.querySelector('.settings-label')?.textContent === label);

                if (row) {
                    row.querySelector('.settings-value').textContent = translated;
                    console.log(`[DEBUG] Успешно обновили настройку ${label}`);
                } else {
                    console.warn(`[WARN] Не найден элемент для настройки ${label}`);
                }
            });
        } catch (error) {
            console.error('[ERROR] Ошибка в updateGameSettings:', error);
        }
    }

    // Обновление информации о бюджете
    function updateBudget(data) {
        console.log('[DEBUG] updateBudget вызван с data:', data);
        
        const budget = data.user_selections?.budget;
        if (!budget) {
            console.warn('[WARN] updateBudget: данные бюджета отсутствуют');
            return;
        }

        try {
            console.log(`[DEBUG] Устанавливаем запрошенный бюджет: ${budget.amount}`);
            document.querySelector('.budget-amount').textContent = formatPrice(budget.amount);

            let total = 0;
            const components = data.components || {};
            console.log('[DEBUG] Компоненты для расчета суммы:', components);

            const keys = ['gpu', 'cpu', 'dimm', 'ssd', 'motherboard', 'psu', 'case_fan', 'pc_case', 'cpu_cooler'];
            
            keys.forEach(key => {
                const comp = components[key];
                const price = comp?.price ?? comp?.data?.price;
                
                if (typeof price === 'number') {
                    console.log(`[DEBUG] Добавляем цену компонента ${key}: ${price}`);
                    total += price;
                } else {
                    console.log(`[DEBUG] Компонент ${key} не имеет цены или отсутствует`);
                }
            });

            console.log(`[DEBUG] Итоговая сумма: ${total}`);
            document.querySelector('.final-price').textContent = formatPrice(total);

            const diff = total - budget.amount;
            console.log(`[DEBUG] Разница с бюджетом: ${diff}`);

            const diffElem = document.querySelector('.budget-difference');
            diffElem.textContent = formatPrice(Math.abs(diff));
            diffElem.classList.toggle('over-budget', diff > 0);
            diffElem.classList.toggle('under-budget', diff <= 0);
            
            console.log('[DEBUG] Бюджет успешно обновлен');
        } catch (error) {
            console.error('[ERROR] Ошибка в updateBudget:', error);
        }
    }

    // Получение спецификаций компонента
    function getComponentSpecs(key, comp) {
        console.log(`[DEBUG] getComponentSpecs вызван для ${key} с данными:`, comp);
        
        const d = comp.data || comp;
        const s = [];

        try {
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
                case 'cpu_cooler':
                    if (d.type) s.push(`Тип: ${d.type === 'air_cpu_cooler' ? 'Воздушный' : 'Жидкостный'}`);
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
            
            console.log(`[DEBUG] Сформированы спецификации для ${key}:`, s);
            return s;
        } catch (error) {
            console.error(`[ERROR] Ошибка при формировании спецификаций для ${key}:`, error);
            return ['Ошибка загрузки характеристик'];
        }
    }

    // Отрисовка таблицы компонентов
    function updateComponentsTable(data) {
        console.log('[DEBUG] updateComponentsTable вызван с data:', data);
        
        const tbody = document.querySelector('.components-table tbody');
        if (!tbody) {
            console.error('[ERROR] Не найден tbody для таблицы компонентов');
            return;
        }

        tbody.innerHTML = '';
        
        try {
            const names = {
                'gpu': 'Видеокарта',
                'cpu': 'Процессор',
                'cpu_cooler': 'Кулер CPU',
                'ssd': 'SSD',
                'dimm': 'ОЗУ',
                'motherboard': 'Материнская плата',
                'psu': 'Блок питания',
                'case_fan': 'Вентиляторы',
                'pc_case': 'Корпус'
            };

            const order = ['gpu', 'cpu', 'dimm', 'ssd', 'motherboard', 'psu', 'case_fan', 'pc_case', 'cpu_cooler'];
            const components = data.components || {};
            
            console.log('[DEBUG] Начинаем обработку компонентов в порядке:', order);

            order.forEach(key => {
                const comp = components[key];
                if (!comp) {
                    console.log(`[DEBUG] Компонент ${key} отсутствует в данных`);
                    return;
                }

                console.log(`[DEBUG] Обрабатываем компонент ${key}:`, comp);
                
                const row = document.createElement('tr');

                // Тип компонента
                const typeCell = document.createElement('td');
                typeCell.textContent = names[key] || key;
                row.appendChild(typeCell);

                // Название компонента
                const nameCell = document.createElement('td');
                nameCell.textContent = comp.name || comp.data?.name || '—';
                row.appendChild(nameCell);

                // Изображение компонента
                const imgCell = document.createElement('td');
                const img = document.createElement('img');
                img.src = comp.image_url || comp.data?.image_url || 'https://via.placeholder.com/80';
                img.alt = names[key] || key;
                img.className = 'component-image';
                imgCell.appendChild(img);
                row.appendChild(imgCell);

                // Цена компонента
                const priceCell = document.createElement('td');
                priceCell.className = 'price-value';
                const price = comp.price ?? comp.data?.price;
                priceCell.textContent = formatPrice(price);
                row.appendChild(priceCell);

                // Характеристики компонента
                const specsCell = document.createElement('td');
                const specsList = document.createElement('div');
                specsList.className = 'specs-list';
                
                const specs = getComponentSpecs(key, comp);
                specs.forEach(spec => {
                    const badge = document.createElement('span');
                    badge.className = 'spec-badge';
                    badge.textContent = spec;
                    specsList.appendChild(badge);
                });
                
                specsCell.appendChild(specsList);
                row.appendChild(specsCell);

                tbody.appendChild(row);
                console.log(`[DEBUG] Добавлена строка для компонента ${key}`);
            });

            console.log('[DEBUG] Таблица компонентов успешно обновлена');
        } catch (error) {
            console.error('[ERROR] Ошибка в updateComponentsTable:', error);
        }
    }

    // Основная обработка ответа от сервера
    function processServerResponse(data) {
        console.log('[DEBUG] processServerResponse вызван с data:', data);
        
        try {
            if (data.status !== 'ok') {
                const errorMsg = data.message || 'Неизвестная ошибка сервера';
                console.error('[ERROR] Сервер вернул ошибку:', errorMsg);
                
                const errorElement = document.querySelector('.error-message');
                errorElement.textContent = errorMsg;
                errorElement.style.display = 'block';
                
                document.querySelector('.loading-indicator').style.display = 'none';
                return;
            }

            console.log('[DEBUG] Начинаем обновление интерфейса');
            updateGameSettings(data);
            updateBudget(data);
            updateComponentsTable(data);

            document.querySelector('.loading-indicator').style.display = 'none';
            document.querySelector('.components-table').style.display = 'table';
            
            console.log('[DEBUG] Интерфейс успешно обновлен');
        } catch (error) {
            console.error('[ERROR] Ошибка в processServerResponse:', error);
            
            const errorElement = document.querySelector('.error-message');
            errorElement.textContent = 'Произошла ошибка при обработке данных';
            errorElement.style.display = 'block';
            
            document.querySelector('.loading-indicator').style.display = 'none';
        }
    }

    // Загрузка конфигурации
    async function loadConfiguration() {
        console.log('[DEBUG] Начало загрузки конфигурации');
        
        try {
            const configId = new URLSearchParams(window.location.search).get('config_id');
            if (!configId) {
                const errorMsg = 'Не найден ID конфигурации в URL';
                console.error('[ERROR]', errorMsg);
                
                document.querySelector('.error-message').textContent = errorMsg;
                document.querySelector('.loading-indicator').style.display = 'none';
                return;
            }

            console.log(`[DEBUG] Загружаем конфигурацию с ID: ${configId}`);
            
            const response = await fetch(`/api/components/result?config_id=${configId}`);
            if (!response.ok) {
                const errorMsg = `Ошибка HTTP: ${response.status}`;
                console.error('[ERROR]', errorMsg);
                
                document.querySelector('.error-message').textContent = errorMsg;
                document.querySelector('.loading-indicator').style.display = 'none';
                return;
            }

            const data = await response.json();
            console.log('[DEBUG] Получены данные от сервера:', data);
            
            processServerResponse(data);
        } catch (error) {
            console.error('[ERROR] Ошибка в loadConfiguration:', error);
            
            document.querySelector('.error-message').textContent = 
                'Ошибка при загрузке конфигурации. Пожалуйста, попробуйте позже.';
            document.querySelector('.loading-indicator').style.display = 'none';
        }
    }

    // Запуск загрузки конфигурации
    console.log('[DEBUG] Запускаем загрузку конфигурации');
    loadConfiguration();
});