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
            // Изменено с .budget-amount на .budget-value:first-child
            document.querySelector('.budget-section .budget-row:first-child .budget-value').textContent = formatPrice(budget.amount);

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
            // Изменено с .final-price на .budget-value.final
            document.querySelector('.budget-section .budget-row:last-child .budget-value').textContent = formatPrice(total);

            const diff = total - budget.amount;
            console.log(`[DEBUG] Разница с бюджетом: ${diff}`);

            const diffElem = document.querySelector('.budget-difference');
            if (diffElem) {
                diffElem.textContent = formatPrice(Math.abs(diff));
                diffElem.classList.toggle('over-budget', diff > 0);
                diffElem.classList.toggle('under-budget', diff <= 0);
            }
            
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
                    if (d.architecture) s.push(`Архитектура: ${d.architecture}`);
                    if (d.vram_size) s.push(`Память: ${d.vram_size} ГБ`);
                    if (d.vram_type) s.push(`Тип памяти: ${d.vram_type}`);
                    if (d.bus_width) s.push(`Ширина шины: ${d.bus_width}-бит`);
                    if (d.base_clock && d.boost_clock) {
                        s.push(`Частота: ${d.base_clock}–${d.boost_clock} МГц`);
                    } else if (d.base_clock) {
                        s.push(`Базовая частота: ${d.base_clock} МГц`);
                    } else if (d.boost_clock) {
                        s.push(`Boost частота: ${d.boost_clock} МГц`);
                    }
                    if (d.cuda_cores) s.push(`CUDA-ядра: ${d.cuda_cores}`);
                    if (d.tensor_cores) s.push(`Tensor-ядра: ${d.tensor_cores}`);
                    if (d.ray_tracing !== undefined) s.push(`Ray Tracing: ${d.ray_tracing ? 'Да' : 'Нет'}`);
                    if (d.interface) s.push(`Интерфейс: ${d.interface}`);
                    if (d.slot_width) s.push(`Тип слота: ${d.slot_width}`);
                    if (d.slots) s.push(`Занимаемых слотов: ${d.slots}`);
                    if (d.low_profile !== undefined) s.push(`Low Profile: ${d.low_profile ? 'Да' : 'Нет'}`);
                    if (d.length) s.push(`Длина: ${d.length} мм`);
                    if (d.width) s.push(`Ширина: ${d.width} мм`);
                    if (d.thickness) s.push(`Толщина: ${d.thickness} мм`);
                    if (d.power_connectors) s.push(`Питание: ${d.power_connectors}`);
                    if (d.recommended_psu) s.push(`Рекомендуемый БП: ${d.recommended_psu} Вт`);
                    if (d.video_outputs) s.push(`Выходы: ${d.video_outputs}`);
                    if (d.max_resolution) s.push(`Макс. разрешение: ${d.max_resolution}`);
                    if (d.benchmark_rate) s.push(`Производительность: ${d.benchmark_rate}`);
                    break;
                case 'cpu':
                    if (d.socket) s.push(`Сокет: ${d.socket}`);
                    if (d.tdp) s.push(`TDP: ${d.tdp} Вт`);
                    if (d.base_tdp) s.push(`Базовый TDP: ${d.base_tdp} Вт`);
                    if (d.cooler_included !== undefined) s.push(`Кулер в комплекте: ${d.cooler_included ? 'Да' : 'Нет'}`);
                    if (d.total_cores) s.push(`Всего ядер: ${d.total_cores}`);
                    if (d.performance_cores) s.push(`Производительные ядра: ${d.performance_cores}`);
                    if (d.efficiency_cores) s.push(`Энергоэффективные ядра: ${d.efficiency_cores}`);
                    if (d.max_threads) s.push(`Потоков: ${d.max_threads}`);
                    if (d.base_frequency && d.turbo_frequency) {
                        s.push(`Частота: ${d.base_frequency}–${d.turbo_frequency} ГГц`);
                    } else if (d.base_frequency) {
                        s.push(`Базовая частота: ${d.base_frequency} ГГц`);
                    } else if (d.turbo_frequency) {
                        s.push(`Turbo частота: ${d.turbo_frequency} ГГц`);
                    }
                    if (d.unlocked_multiplier !== undefined) s.push(`Разблокирован множитель: ${d.unlocked_multiplier ? 'Да' : 'Нет'}`);
                    if (d.memory_type) s.push(`Тип памяти: ${d.memory_type}`);
                    if (d.max_memory) s.push(`Максимум ОЗУ: ${d.max_memory} ГБ`);
                    if (d.memory_channels) s.push(`Каналы памяти: ${d.memory_channels}`);
                    if (d.memory_frequency) s.push(`Частота памяти: до ${d.memory_frequency} МГц`);
                    if (d.integrated_graphics !== undefined) {
                        s.push(`Встроенная графика: ${d.integrated_graphics ? 'Да' : 'Нет'}`);
                    }
                    if (d.pci_express) s.push(`Интерфейс PCIe: ${d.pci_express}`);
                    if (d.pci_lanes) s.push(`PCIe линий: ${d.pci_lanes}`);
                    if (d.benchmark_rate) s.push(`Производительность: ${d.benchmark_rate}`);
                    break;
                case 'cpu_cooler':
                    if (d.type) s.push(`Тип: ${d.type === 'air_cpu_cooler' ? 'Воздушный' : 'Жидкостный'}`);

                    if (d.type === 'air_cpu_cooler') {
                        if (d.socket) s.push(`Сокеты: ${d.socket}`);
                        if (d.tdp) s.push(`TDP: ${d.tdp} Вт`);
                        if (d.fan_size) s.push(`Размер вентилятора: ${d.fan_size.toString().replace(/^(\d{3})(\d{3})$/, '$1×$2')} мм`);
                        if (d.fan_count) s.push(`Кол-во вентиляторов: ${d.fan_count}`);
                        if (d.min_rpm && d.max_rpm) {
                            s.push(`Скорость вращения: ${d.min_rpm}–${d.max_rpm} об/мин`);
                        } else if (d.max_rpm) {
                            s.push(`Макс. скорость: ${d.max_rpm} об/мин`);
                        }
                        if (d.max_noise_level) s.push(`Уровень шума: до ${d.max_noise_level} дБ`);
                        if (d.max_airflow) s.push(`Поток воздуха: до ${d.max_airflow} CFM`);
                        if (d.height) s.push(`Высота: ${d.height} мм`);
                        if (d.width) s.push(`Ширина: ${d.width} мм`);
                        if (d.depth) s.push(`Глубина: ${d.depth} мм`);
                    } else if (d.type === 'water_cpu_cooler') {
                        if (d.compatible_sockets) s.push(`Сокеты: ${d.compatible_sockets}`);
                        if (d.radiator_size) s.push(`Радиатор: ${d.radiator_size}`);
                        if (d.fans_count) s.push(`Кол-во вентиляторов: ${d.fans_count}`);
                        if (d.fan_max_speed) s.push(`Скорость вентиляторов: до ${d.fan_max_speed} об/мин`);
                        if (d.fan_max_noise) s.push(`Шум вентилятора: до ${d.fan_max_noise} дБ`);
                        if (d.fan_airflow) s.push(`Поток воздуха: до ${d.fan_airflow} CFM`);
                        if (d.pump_speed) s.push(`Скорость помпы: до ${d.pump_speed} об/мин`);
                        if (d.tube_length) s.push(`Длина шлангов: ${d.tube_length} мм`);
                    }
                    break;
                case 'ssd':
                    if (d.capacity) s.push(`Объем: ${d.capacity} ГБ`);
                    if (d.form_factor) s.push(`Форм-фактор: ${d.form_factor}`);
                    if (d.interface) s.push(`Интерфейс: ${d.interface}`);
                    if (d.m2_key) s.push(`Ключ M.2: ${d.m2_key}`);
                    if (d.nvme !== undefined) s.push(`Поддержка NVMe: ${d.nvme ? 'Да' : 'Нет'}`);
                    if (d.cell_type) s.push(`Тип ячеек: ${d.cell_type}`);
                    if (d.memory_structure) s.push(`Структура памяти: ${d.memory_structure}`);
                    if (d.has_dram !== undefined) s.push(`DRAM-кэш: ${d.has_dram ? 'Есть' : 'Нет'}`);
                    if (d.dram_size) s.push(`Размер DRAM: ${d.dram_size}`);
                    if (d.max_read_speed && d.max_write_speed) {
                        s.push(`Скорость чтения/записи: ${d.max_read_speed}/${d.max_write_speed} МБ/с`);
                    } else if (d.max_read_speed) {
                        s.push(`Макс. скорость чтения: ${d.max_read_speed} МБ/с`);
                    } else if (d.max_write_speed) {
                        s.push(`Макс. скорость записи: ${d.max_write_speed} МБ/с`);
                    }
                    if (d.random_read_iops) s.push(`Случайное чтение: ${d.random_read_iops.toLocaleString()} IOPS`);
                    if (d.random_write_iops) s.push(`Случайная запись: ${d.random_write_iops.toLocaleString()} IOPS`);
                    if (d.length && d.width) s.push(`Размеры: ${d.length}×${d.width} мм`);
                    if (d.thickness) s.push(`Толщина: ${d.thickness} мм`);
                    if (d.weight) s.push(`Вес: ${d.weight} г`);
                    if (d.heatsink_included !== undefined) s.push(`Радиатор: ${d.heatsink_included ? 'В комплекте' : 'Нет'}`);
                    break;
                case 'dimm':
                    if (d.total_memory) s.push(`Объем: ${d.total_memory} ГБ`);
                    if (d.modules_count) s.push(`Модулей: ${d.modules_count}×${d.total_memory / d.modules_count} ГБ`);
                    if (d.memory_type) s.push(`Тип: ${d.memory_type}`);
                    if (d.module_type) s.push(`Тип модуля: ${d.module_type}`);
                    if (d.frequency) s.push(`Частота: ${d.frequency} МГц`);
                    if (d.cas_latency) s.push(`CAS Latency (CL): ${d.cas_latency}`);
                    if (d.ras_to_cas_delay) s.push(`RAS to CAS Delay (tRCD): ${d.ras_to_cas_delay}`);
                    if (d.row_precharge_delay) s.push(`Row Precharge Delay (tRP): ${d.row_precharge_delay}`);
                    if (d.activate_to_precharge_delay) s.push(`tRAS: ${d.activate_to_precharge_delay}`);
                    if (d.voltage) s.push(`Напряжение: ${d.voltage} В`);
                    if (d.ecc_memory !== undefined) s.push(`ECC: ${d.ecc_memory ? 'Да' : 'Нет'}`);
                    if (d.registered_memory !== undefined) s.push(`Registered: ${d.registered_memory ? 'Да' : 'Нет'}`);
                    if (d.intel_xmp) s.push(`Intel XMP: ${d.intel_xmp}`);
                    if (d.amd_expo) s.push(`AMD EXPO: ${d.amd_expo}`);
                    if (d.height) s.push(`Высота: ${d.height} мм`);
                    if (d.low_profile !== undefined) s.push(`Low Profile: ${d.low_profile ? 'Да' : 'Нет'}`);
                    break;
                case 'motherboard':
                    if (d.socket) s.push(`Сокет: ${d.socket}`);
                    if (d.chipset) s.push(`Чипсет: ${d.chipset}`);
                    if (d.form_factor) s.push(`Форм-фактор: ${d.form_factor}`);
                    if (d.memory_type) s.push(`Тип памяти: ${d.memory_type}`);
                    if (d.memory_slots) s.push(`Слотов под память: ${d.memory_slots}`);
                    if (d.memory_channels) s.push(`Каналов памяти: ${d.memory_channels}`);
                    if (d.max_memory) s.push(`Макс. объём памяти: ${d.max_memory} ГБ`);
                    if (d.base_memory_freq) s.push(`Базовая частота памяти: ${d.base_memory_freq} МГц`);
                    if (d.oc_memory_freq?.length)
                        s.push(`OC частоты памяти: ${d.oc_memory_freq.join(', ')} МГц`);
                    if (d.memory_form_factor) s.push(`Форм-фактор памяти: ${d.memory_form_factor}`);
                    if (d.pcie_version) s.push(`Версия PCIe: ${d.pcie_version}`);
                    if (d.pcie_x16_slots) s.push(`PCIe x16 слотов: ${d.pcie_x16_slots}`);
                    if (d.sli_crossfire !== undefined)
                        s.push(`SLI/CrossFire: ${d.sli_crossfire ? `Да (${d.sli_crossfire_count})` : 'Нет'}`);
                    if (d.nvme_support !== undefined) s.push(`Поддержка NVMe: ${d.nvme_support ? 'Да' : 'Нет'}`);
                    if (d.m2_slots) s.push(`Слотов M.2: ${d.m2_slots}`);
                    if (d.sata_ports) s.push(`Портов SATA: ${d.sata_ports}`);
                    if (d.sata_raid !== undefined) s.push(`SATA RAID: ${d.sata_raid ? 'Да' : 'Нет'}`);
                    if (d.nvme_raid !== undefined) s.push(`NVMe RAID: ${d.nvme_raid ? 'Да' : 'Нет'}`);
                    if (d.cpu_fan_headers) s.push(`Разъёмов CPU FAN: ${d.cpu_fan_headers}`);
                    if (d.aio_pump_headers !== null && d.aio_pump_headers !== undefined)
                        s.push(`Разъёмов AIO PUMP: ${d.aio_pump_headers}`);
                    if (d.case_fan_4pin) s.push(`Разъёмов корпусных вентиляторов (4-pin): ${d.case_fan_4pin}`);
                    if (d.case_fan_3pin) s.push(`Разъёмов корпусных вентиляторов (3-pin): ${d.case_fan_3pin}`);
                    if (d.main_power) s.push(`Питание материнской платы: ${d.main_power}`);
                    if (d.cpu_power) s.push(`Питание процессора: ${d.cpu_power}`);
                    if (d.width && d.height) s.push(`Размеры: ${d.width}×${d.height} мм`);
                    break;
                case 'psu':
                    if (d.wattage) s.push(`Мощность: ${d.wattage} Вт`);
                    if (d.certification_80plus) s.push(`Сертификат: 80+ ${d.certification_80plus}`);
                    if (d.form_factor) s.push(`Форм-фактор: ${d.form_factor}`);
                    if (d.cable_management) s.push(`Кабель-менеджмент: ${d.cable_management}`);
                    if (d.main_connector) s.push(`Основной разъём питания: ${d.main_connector}`);
                    if (d.cpu_connectors) s.push(`Разъёмы CPU: ${d.cpu_connectors}`);
                    if (d.pcie_connectors) s.push(`PCIe разъёмы: ${d.pcie_connectors}`);
                    if (d.sata_connectors !== undefined) s.push(`SATA разъёмы: ${d.sata_connectors}`);
                    if (d.molex_connectors !== undefined) s.push(`Molex разъёмы: ${d.molex_connectors}`);
                    if (d.floppy_connector !== undefined)
                        s.push(`Разъём Floppy: ${d.floppy_connector ? 'Да' : 'Нет'}`);
                    if (d.cooling_type) s.push(`Тип охлаждения: ${d.cooling_type}`);
                    if (d.fan_size) {
                        const fanW = Math.floor(d.fan_size / 1000);
                        const fanH = d.fan_size % 1000;
                        s.push(`Размер вентилятора: ${fanW}×${fanH} мм`);
                    }
                    if (d.hybrid_mode !== undefined)
                        s.push(`Гибридный режим: ${d.hybrid_mode ? 'Да' : 'Нет'}`);
                    if (d.pfc_type) s.push(`Тип PFC: ${d.pfc_type}`);
                    if (d.length && d.width && d.height)
                        s.push(`Размеры: ${d.width}×${d.height}×${d.length} мм`);
                    if (d.weight) s.push(`Вес: ${d.weight} кг`);
                    break;
                case 'case_fan':
                    if (d.fan_size && d.fan_thickness)
                        s.push(`Размер: ${d.fan_size}×${d.fan_thickness} мм`);
                    else if (d.fan_size)
                        s.push(`Размер: ${d.fan_size} мм`);
                    if (d.max_rotation_speed && d.min_rotation_speed)
                        s.push(`Обороты: ${d.min_rotation_speed}–${d.max_rotation_speed} об/мин`);
                    else if (d.max_rotation_speed)
                        s.push(`Макс. обороты: ${d.max_rotation_speed} об/мин`);
                    if (d.max_airflow) s.push(`Поток воздуха: ${d.max_airflow} CFM`);
                    if (d.max_static_pressure)
                        s.push(`Статическое давление: ${d.max_static_pressure} мм H₂O`);
                    if (d.max_noise_level && d.min_noise_level)
                        s.push(`Шум: ${d.min_noise_level}–${d.max_noise_level} дБ`);
                    else if (d.max_noise_level)
                        s.push(`Макс. шум: ${d.max_noise_level} дБ`);
                    if (d.power_connector_type)
                        s.push(`Разъём питания: ${d.power_connector_type}`);
                    break;
                case 'pc_case':
                    if (d.motherboard_form_factors) s.push(`Форм-форматы материнских плат: ${d.motherboard_form_factors}`);
                    if (d.max_gpu_length) s.push(`Максимальная длина видеокарты: до ${d.max_gpu_length}`);
                    if (d.psu_form_factor) s.push(`Форм-фактор блока питания: ${d.psu_form_factor}`);
                    if (d.max_psu_length) s.push(`Максимальная длина блока питания: ${d.max_psu_length}`);
                    if (d.fan_support) {
                        const size = d.fan_support.size ? `${d.fan_support.size} мм` : '';
                        const positions = d.fan_support.positions ? d.fan_support.positions.join(', ') : '';
                        s.push(`Поддержка вентиляторов: ${size} в позициях ${positions}`);
                    }
                    if (d.max_cpu_cooler_height) s.push(`Максимальная высота кулера ЦП: ${d.max_cpu_cooler_height}`);
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
                'cooler': 'Кулер CPU',
                'ssd': 'SSD',
                'dimm': 'ОЗУ',
                'motherboard': 'Материнская плата',
                'psu': 'Блок питания',
                'case_fan': 'Вентиляторы',
                'pc_case': 'Корпус'
            };

            const order = ['gpu', 'cpu', 'dimm', 'ssd', 'motherboard', 'psu', 'case_fan', 'pc_case', 'cooler'];
            const components = data.components || {};
            
            console.log('[DEBUG] Начинаем обработку компонентов в порядке:', order);

            order.forEach(key => {
                const comp = components[key];
                if (!comp) {
                    console.log(`[DEBUG] Компонент ${key} отсутствует в данных`);
                    return;
                }

                console.log(`[DEBUG] Обрабатываем компонент ${key}:`, comp);
                
                // Основная строка с компонентом
                const mainRow = document.createElement('tr');
                mainRow.className = 'component-main-row';

                // Тип компонента
                const typeCell = document.createElement('td');
                typeCell.textContent = names[key] || key;
                mainRow.appendChild(typeCell);

                // Название компонента
                const nameCell = document.createElement('td');
                nameCell.textContent = comp.name || comp.data?.name || '—';
                mainRow.appendChild(nameCell);

                // Изображение компонента
                const imgCell = document.createElement('td');
                const img = document.createElement('img');
                img.src = comp.image_url || comp.data?.image_url || 'https://via.placeholder.com/80';
                img.alt = names[key] || key;
                img.className = 'component-image';
                imgCell.appendChild(img);
                mainRow.appendChild(imgCell);

                // Цена компонента
                const priceCell = document.createElement('td');
                priceCell.className = 'price-value';
                const price = comp.price ?? comp.data?.price;
                priceCell.textContent = formatPrice(price);
                mainRow.appendChild(priceCell);

                tbody.appendChild(mainRow);
                
                // Строка с характеристиками
                const specsRow = document.createElement('tr');
                specsRow.className = 'component-specs-row';
                
                const specsCell = document.createElement('td');
                specsCell.colSpan = 4;
                
                const specsContainer = document.createElement('div');
                specsContainer.className = 'specs-container';
                
                const specs = getComponentSpecs(key, comp);
                specs.forEach(spec => {
                    const badge = document.createElement('span');
                    badge.className = 'spec-badge';
                    badge.textContent = spec;
                    specsContainer.appendChild(badge);
                });
                
                specsCell.appendChild(specsContainer);
                specsRow.appendChild(specsCell);
                
                tbody.appendChild(specsRow);
                
                console.log(`[DEBUG] Добавлены строки для компонента ${key}`);
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