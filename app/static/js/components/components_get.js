document.addEventListener('DOMContentLoaded', function() {
    function formatPrice(price) {
        return new Intl.NumberFormat('ru-RU').format(price) + ' ₽';
    }

    function translateGraphicsSettings(setting, value) {
        const translations = {
            'quality': { 'low': 'Низкие', 'medium': 'Средние', 'high': 'Высокие', 'ultra': 'Ультра' },
            'resolution': { '720': '720p (HD)', '1080': '1080p (Full HD)', '1440': '1440p (QHD)', '2160': '2160p (4K UHD)' },
            'dlss': { 'disabled': 'Выключено', 'performance': 'Производительность', 'balanced': 'Сбалансированный', 'quality': 'Качество', 'ultra_performance': 'Ультра производительность' },
            'fsr': { 'disabled': 'Выключено', 'performance': 'Производительность', 'balanced': 'Сбалансированный', 'quality': 'Качество', 'ultra_performance': 'Ультра производительность' },
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

    function updateGameSettings(data) {
        console.log('updateGameSettings called', data);
        if (!data.user_selections || !data.user_selections.game) {
            console.warn('Game settings missing in data', data);
            return;
        }
        const game = data.user_selections.game;
        document.querySelector('.game-title').textContent = game.title.replace(/_/g, ' ');
        
        const settingsMap = {
            'quality': 'Графика',
            'resolution': 'Разрешение',
            'target_fps': 'Частота кадров',
            'ray_tracing': 'Трассировка лучей',
            'dlss': 'NVIDIA DLSS',
            'fsr': 'AMD FSR'
        };
        
        Object.keys(settingsMap).forEach(key => {
            const label = settingsMap[key];
            let value = game.graphics_settings ? game.graphics_settings[key] : undefined;
            if (value === undefined) {
                console.warn(`Graphics setting "${key}" missing`);
                value = '-';
            } else {
                value = translateGraphicsSettings(key, value);
            }
            const rows = document.querySelectorAll('.settings-row');
            let updated = false;
            rows.forEach(row => {
                if (row.querySelector('.settings-label').textContent === label) {
                    row.querySelector('.settings-value').textContent = value;
                    updated = true;
                }
            });
            if (!updated) {
                console.warn(`Row for setting "${label}" not found`);
            }
        });
    }

    function updateBudget(data) {
        console.log('updateBudget called', data);
        if (!data.user_selections || !data.user_selections.budget) {
            console.warn('Budget info missing in data', data);
            return;
        }
        const budget = data.user_selections.budget;
        const budgetAmountEl = document.querySelector('.budget-row:nth-child(1) .budget-value');
        if (budgetAmountEl) {
            budgetAmountEl.textContent = formatPrice(budget.amount);
        } else {
            console.warn('Budget amount element not found');
        }
        
        let totalPrice = 0;
        const comps = data.components || {};
        ['gpu', 'cpu', 'dimm', 'ssd_m2', 'motherboard', 'power_supply', 'case_fan', 'pc_case', 'cpu_cooler'].forEach(key => {
            if (comps[key] && typeof comps[key].price === 'number') {
                totalPrice += comps[key].price;
            }
        });

        const finalPriceEl = document.querySelector('.budget-row:nth-child(2) .budget-value.final');
        if (finalPriceEl) {
            finalPriceEl.textContent = formatPrice(totalPrice);
        } else {
            console.warn('Final budget element not found');
        }
    }

    function updateComponentsTable(data) {
        console.log('updateComponentsTable called', data);
        const tbody = document.querySelector('.components-table tbody');
        if (!tbody) {
            console.warn('Components table tbody element not found');
            return;
        }
        tbody.innerHTML = '';
        
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

        const displayOrder = ['gpu', 'cpu', 'dimm', 'ssd_m2', 'motherboard', 'power_supply', 'case_fan', 'pc_case', 'cpu_cooler'];
        const comps = data.components || {};

        displayOrder.forEach(componentKey => {
            const component = comps[componentKey];
            if (!component) {
                console.log(`Component "${componentKey}" not found or empty`);
                return;
            }
            const row = document.createElement('tr');
            const typeCell = document.createElement('td');
            typeCell.textContent = componentNames[componentKey] || componentKey;
            row.appendChild(typeCell);

            const nameCell = document.createElement('td');
            nameCell.textContent = component.name || 'Не указано';
            row.appendChild(nameCell);

            const imgCell = document.createElement('td');
            const img = document.createElement('img');
            img.src = component.image_url || 'https://via.placeholder.com/80';
            img.alt = componentNames[componentKey] || componentKey;
            img.className = 'component-image';
            imgCell.appendChild(img);
            row.appendChild(imgCell);

            const priceCell = document.createElement('td');
            priceCell.className = 'price-value';
            priceCell.textContent = component.price ? formatPrice(component.price) : '—';
            row.appendChild(priceCell);

            const specsCell = document.createElement('td');
            const specsList = document.createElement('div');
            specsList.className = 'specs-list';

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
                        `Память: ${component.memory_type} до ${component.oc_memory_freq ? component.oc_memory_freq.slice(-1)[0] : '-'} МГц`,
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
                        `Вентиляторы: ${component.fan_support ? component.fan_support.size : '-'} мм`
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

    function processServerResponse(data) {
        console.log('processServerResponse called', data);
        if (data.status !== 'ok') {
            console.error('Server error:', data.message);
            return;
        }
        updateGameSettings(data);
        updateBudget(data);
        updateComponentsTable(data);
    }

    async function loadConfiguration() {
        try {
            const urlParams = new URLSearchParams(window.location.search);
            const configId = urlParams.get('config_id');
            if (!configId) {
                console.error('Configuration ID not found in URL');
                return;
            }
            console.log('Fetching configuration for config_id:', configId);
            const response = await fetch(`/api/components/result?config_id=${configId}`);
            if (!response.ok) {
                console.error('HTTP error', response.status);
                return;
            }
            const data = await response.json();
            console.log('Data received from server:', data);
            processServerResponse(data);
        } catch (error) {
            console.error('Error loading configuration:', error);
        }
    }

    loadConfiguration();
});
