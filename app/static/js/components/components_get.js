document.addEventListener('DOMContentLoaded', function() {
    // Функция для форматирования цены с пробелами
    function formatPrice(price) {
        return new Intl.NumberFormat('ru-RU').format(price) + ' ₽';
    }

    // Функция для перевода настроек графики на русский
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
                return translations[setting][value.toLowerCase()] || value;
            } else if (typeof translations[setting] === 'function') {
                return translations[setting](value);
            }
        }
        return value;
    }

    // Функция для обновления блока с игрой и настройками
    function updateGameSettings(data) {
        const game = data.user_request.game;
        
        // Обновляем название игры
        document.querySelector('.game-title').textContent = game.title.replace(/_/g, ' ');
        
        // Обновляем настройки графики
        const settingsMap = {
            'quality': 'Графика',
            'resolution': 'Разрешение',
            'target_fps': 'Частота кадров',
            'ray_tracing': 'Трассировка лучей',
            'dlss': 'NVIDIA DLSS',
            'fsr': 'AMD FSR'
        };
        
        // Обновляем каждую настройку
        Object.keys(settingsMap).forEach(key => {
            const label = settingsMap[key];
            let value = game.graphics[key];
            value = translateGraphicsSettings(key, value);
            
            // Находим соответствующую строку в таблице и обновляем значение
            const rows = document.querySelectorAll('.settings-row');
            rows.forEach(row => {
                if (row.querySelector('.settings-label').textContent === label) {
                    row.querySelector('.settings-value').textContent = value;
                }
            });
        });
    }

    // Функция для обновления блока с бюджетом
    function updateBudget(data) {
        const budget = data.user_request.budget;
        
        document.querySelector('.budget-row:nth-child(1) .budget-value').textContent = 
            formatPrice(budget.amount);
        
        // Рассчитываем итоговую сумму из всех компонентов
        let totalPrice = 0;
        if (data.gpu) totalPrice += data.gpu.price;
        if (data.cpu) totalPrice += data.cpu.price;
        if (data.dimm) totalPrice += data.dimm.price;
        if (data.ssd_m2) totalPrice += data.ssd_m2.price;
        if (data.motherboard) totalPrice += data.motherboard.price;
        if (data.power_supply) totalPrice += data.power_supply.price;
        if (data.case_fan) totalPrice += data.case_fan.price;
        if (data.pc_case) totalPrice += data.pc_case.price;
        if (data.cpu_cooler) totalPrice += data.cpu_cooler.price;
        
        document.querySelector('.budget-row:nth-child(2) .budget-value.final').textContent = 
            formatPrice(totalPrice);
    }

    // Функция для обновления таблицы комплектующих
    function updateComponentsTable(data) {
        const tbody = document.querySelector('.components-table tbody');
        tbody.innerHTML = ''; // Очищаем таблицу
        
        // Маппинг компонентов на русский язык
        const componentNames = {
            'gpu': 'Видеокарта',
            'cpu': 'Процессор',
            'dimm': 'ОЗУ',
            'ssd_m2': 'SSD',
            'motherboard': 'Материнская плата',
            'power_supply': 'БП',
            'case_fan': 'Вентиляторы',
            'pc_case': 'Корпус',
            'cpu_cooler': 'Кулер CPU'
        };
        
        // Порядок отображения компонентов
        const displayOrder = [
            'gpu', 'cpu', 'dimm', 'ssd_m2', 'motherboard', 
            'power_supply', 'case_fan', 'pc_case', 'cpu_cooler'
        ];
        
        // Добавляем строки для каждого компонента
        displayOrder.forEach(componentKey => {
            const component = data[componentKey];
            if (!component) return;
            
            const row = document.createElement('tr');
            
            // Название компонента
            const typeCell = document.createElement('td');
            typeCell.textContent = componentNames[componentKey] || componentKey;
            row.appendChild(typeCell);
            
            // Название модели
            const nameCell = document.createElement('td');
            nameCell.textContent = component.name || 'Не указано';
            row.appendChild(nameCell);
            
            // Изображение
            const imgCell = document.createElement('td');
            const img = document.createElement('img');
            img.src = component.image_url || 'https://via.placeholder.com/80';
            img.alt = componentNames[componentKey] || componentKey;
            img.className = 'component-image';
            imgCell.appendChild(img);
            row.appendChild(imgCell);
            
            // Цена
            const priceCell = document.createElement('td');
            priceCell.className = 'price-value';
            priceCell.textContent = component.price ? formatPrice(component.price) : '—';
            row.appendChild(priceCell);
            
            // Характеристики
            const specsCell = document.createElement('td');
            const specsList = document.createElement('div');
            specsList.className = 'specs-list';
            
            // Специфичные характеристики для каждого типа компонента
            let specs = [];
            switch(componentKey) {
                case 'gpu':
                    specs = [
                        `PCIe: ${component.interface}`,
                        `Память: ${component.vram_size} ГБ ${component.vram_type}`,
                        `Шина: ${component.bus_width} бит`,
                        `Частота: ${component.base_clock}/${component.boost_clock} МГц`,
                        `Ядра: ${component.cuda_cores}`,
                        `TDP: ${component.tdp} Вт`
                    ];
                    break;
                case 'cpu':
                    specs = [
                        `Сокет: ${component.socket}`,
                        `Ядра: ${component.performance_cores}P + ${component.efficiency_cores}E`,
                        `Частота: ${component.base_frequency}-${component.turbo_frequency} ГГц`,
                        `Потоки: ${component.max_threads}`,
                        `TDP: ${component.tdp} Вт`,
                        `Память: ${component.memory_type}`
                    ];
                    break;
                case 'dimm':
                    specs = [
                        `Тип: ${component.memory_type}`,
                        `Объем: ${component.total_memory} ГБ`,
                        `Частота: ${component.frequency} МГц`,
                        `Тайминги: CL${component.cas_latency}`,
                        `Модули: ${component.modules_count}`
                    ];
                    break;
                case 'ssd_m2':
                    specs = [
                        `Объем: ${component.capacity} ГБ`,
                        `Интерфейс: ${component.interface}`,
                        `Скорость: ${component.max_read_speed}/${component.max_write_speed} МБ/с`,
                        `IOPS: ${component.random_read_iops}/${component.random_write_iops}`
                    ];
                    break;
                case 'motherboard':
                    specs = [
                        `Сокет: ${component.socket}`,
                        `Чипсет: ${component.chipset}`,
                        `Память: ${component.memory_type} до ${component.oc_memory_freq.slice(-1)[0]} МГц`,
                        `Слоты: ${component.memory_slots}`,
                        `M.2: ${component.m2_slots}`,
                        `PCIe: ${component.pcie_x16_slots} x16`
                    ];
                    break;
                case 'power_supply':
                    specs = [
                        `Мощность: ${component.wattage} Вт`,
                        `Сертификат: 80+ ${component.certification_80plus}`,
                        `PCIe: ${component.pcie_connectors}`,
                        `Форм-фактор: ${component.form_factor}`
                    ];
                    break;
                case 'case_fan':
                    specs = [
                        `Размер: ${component.fan_size} мм`,
                        `Воздушный поток: ${component.max_airflow} CFM`,
                        `Шум: ${component.max_noise_level} дБ`,
                        `Скорость: ${component.max_rotation_speed} RPM`
                    ];
                    break;
                case 'pc_case':
                    specs = [
                        `Форм-фактор: ${component.motherboard_form_factors}`,
                        `Длина GPU: до ${component.max_gpu_length}`,
                        `Высота кулера: до ${component.max_cpu_cooler_height}`,
                        `Вентиляторы: ${component.fan_support.size} мм`
                    ];
                    break;
                case 'cpu_cooler':
                    specs = [
                        `Тип: ${component.type === 'air_cooler' ? 'Воздушный' : 'Жидкостный'}`,
                        `Сокет: ${component.socket}`,
                        `TDP: ${component.tdp} Вт`,
                        `Шум: ${component.noise_level}`
                    ];
                    break;
            }
            
            // Добавляем характеристики в виде бейджей
            specs.forEach(spec => {
                const badge = document.createElement('span');
                badge.className = 'spec-badge';
                badge.textContent = spec;
                specsList.appendChild(badge);
            });
            
            specsCell.appendChild(specsList);
            row.appendChild(specsCell);
            
            tbody.appendChild(row);
        });
    }

    // Функция для обработки ответа сервера
    function processServerResponse(data) {
        // Собираем все компоненты в один объект для удобства
        const components = {
            gpu: data.gpu,
            cpu: data.cpu,
            dimm: data.dimm,
            ssd_m2: data.ssd_m2,
            motherboard: data.motherboard,
            power_supply: data.power_supply,
            case_fan: data.case_fan,
            pc_case: data.pc_case,
            cpu_cooler: data.cpu_cooler
        };
        
        // Добавляем компоненты к основным данным
        const fullData = {
            ...data,
            ...components
        };
        
        updateGameSettings(fullData);
        updateBudget(fullData);
        updateComponentsTable(fullData);
    }

    // Функция для отправки данных и обработки ответа
    function fetchAndDisplayConfig() {
        // Здесь должен быть код для получения данных конфигурации
        // Например, если данные передаются через переменную в шаблоне:
        if (typeof serverResponse !== 'undefined') {
            processServerResponse(serverResponse);
        } 
        // Или если нужно сделать AJAX-запрос:
        else {
            fetch('/configurator/log-click', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify({
                    // Здесь должны быть данные из формы
                })
            })
            .then(response => response.json())
            .then(data => {
                processServerResponse(data);
            })
            .catch(error => {
                console.error('Error:', error);
            });
        }
    }

    // Вызываем функцию при загрузке страницы
    fetchAndDisplayConfig();
});