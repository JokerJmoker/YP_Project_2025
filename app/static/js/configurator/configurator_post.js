document.addEventListener("DOMContentLoaded", () => {
    let selectedGameName = null;

    // Обработка выбора игры
    const gameCards = document.querySelectorAll(".game-card");
    gameCards.forEach(card => {
        card.addEventListener("click", () => {
            selectedGameName = card.querySelector("h3")?.textContent || "Unknown";
            console.log(`Выбрана игра: ${selectedGameName}`);
        });
    });

    // Стандартные значения для распределения бюджета
    const defaultValues = {
        percentage: {
            cpu: 25,
            gpu: 35,
            ram: 8,
            storage: 7,
            motherboard: 8,
            psu: 7,
            cooling: 3,
            case: 5,
            cpuCooler: 2
        },
        fixed: {
            cpu: 30000,
            gpu: 60000,
            ram: 10000,
            storage: 8000,
            motherboard: 12000,
            psu: 8000,
            cooling: 3000,
            case: 7000,
            cpuCooler: 5000
        }
    };

    // Получаем значение компонента (для allocation)
    function getComponentBudgetValue(inputId, componentType, isPercentage) {
        const input = document.getElementById(inputId);
        if (!input || !input.value.trim()) {
            return isPercentage 
                ? defaultValues.percentage[componentType]
                : defaultValues.fixed[componentType];
        }
        return isPercentage ? input.value : input.value.replace(/[^\d]/g, '');
    }

    // Получаем выбор компонента (для названий)
    function getComponentSelection(selectId, valueId) {
        const select = document.getElementById(selectId);
        const valueInput = document.getElementById(valueId);
        
        if (!select || !valueInput) return "any";
        if (select.value === "custom" && valueInput.value.trim()) {
            return valueInput.value;
        }
        return select.value;
    }

    // Получаем тип кулера процессора
    function getCpuCoolerType() {
        const select = document.getElementById("cpuCoolerType");
        if (!select) return "air_cooler"; // безопасное значение по умолчанию
        
        const selectedValue = select.value;
        
        // Для явных выборов возвращаем как есть
        if (selectedValue === "included_with_cpu" || 
            selectedValue === "water_cooling" || 
            selectedValue === "air_cooler") {
            return selectedValue;
        }
        
        // Для "Любое" - случайный выбор из трех вариантов
        if (selectedValue === "any") {
            const options = ["included_with_cpu", "air_cooler", "water_cooling"];
            const randomIndex = Math.floor(Math.random() * options.length);
            return options[randomIndex];
        }
        
        return "air_cooler"; // fallback
    }

    // Обработка кнопки "Далее"
    const btnNext = document.querySelector(".btn-next");
    if (btnNext) {
        btnNext.addEventListener("click", (event) => {
            if (!selectedGameName) {
                event.preventDefault();
                alert("Пожалуйста, выберите игру перед продолжением.");
                return;
            }

            const isPercentageBased = document.getElementById("budgetPercent").checked;

            // Формируем данные для отправки
            const formData = {
                gameName: selectedGameName,
                graphicsQuality: document.getElementById("graphicsSelect")?.value || "High",
                targetFps: parseInt(document.getElementById("fpsSelect")?.value) || 60,
                resolution: parseInt(document.getElementById("resolutionSelect")?.value) || 1080,
                rayTracingEnabled: document.getElementById("rayTracingSelect")?.value !== "off",
                dlss: document.getElementById("dlssSelect")?.value || "off",
                fsr: document.getElementById("fsrSelect")?.value || "off",
                budgetAmount: parseInt(document.getElementById("budgetValue").textContent.replace(/\D/g, '')),
                budgetAllocationMethod: isPercentageBased ? "percentage_based" : "fixed_price_based",
                components: {
                    mandatory: {
                        cpu: getComponentSelection("cpuSelect", "cpuValue"),
                        gpu: getComponentSelection("gpuSelect", "gpuValue"),
                        dimm: getComponentSelection("ramSelect", "ramValue"),
                        ssd_m2: getComponentSelection("storageSelect", "storageValue"),
                        motherboard: getComponentSelection("motherboardSelect", "motherboardValue"),
                        power_supply: getComponentSelection("psuSelect", "psuValue")
                    },
                    mandatory_allocation: {
                        method: isPercentageBased ? "percentage_based" : "fixed_price_based"
                    },
                    optional: {
                        case_fan: "any", // Всегда "any" для дополнительных компонентов
                        pc_case: "any",    // если не выбран конкретный вариант
                        cpu_cooler: getCpuCoolerType()
                    },
                    optional_allocation: {
                        method: isPercentageBased ? "percentage_based" : "fixed_price_based"
                    }
                },
                timestamp: new Date().toISOString()
            };

            // Добавляем значения распределения бюджета
            if (isPercentageBased) {
                formData.components.mandatory_allocation.percentage_based = {
                    cpu_percentage: parseInt(getComponentBudgetValue("cpuValue", "cpu", true)),
                    gpu_percentage: parseInt(getComponentBudgetValue("gpuValue", "gpu", true)),
                    dimm_percentage: parseInt(getComponentBudgetValue("ramValue", "ram", true)),
                    ssd_m2_percentage: parseInt(getComponentBudgetValue("storageValue", "storage", true)),
                    motherboard_percentage: parseInt(getComponentBudgetValue("motherboardValue", "motherboard", true)),
                    power_supply_percentage: parseInt(getComponentBudgetValue("psuValue", "psu", true))
                };
                
                formData.components.optional_allocation.percentage_based = {
                    case_fan_percentage: parseInt(getComponentBudgetValue("coolingValue", "cooling", true)),
                    pc_case_percentage: parseInt(getComponentBudgetValue("caseValue", "case", true)),
                    cpu_cooler_percentage: parseInt(getComponentBudgetValue("cpuCoolerValue", "cpuCooler", true))
                };
            } else {
                formData.components.mandatory_allocation.fixed_price_based = {
                    cpu_max_price: parseInt(getComponentBudgetValue("cpuValue", "cpu", false)),
                    gpu_max_price: parseInt(getComponentBudgetValue("gpuValue", "gpu", false)),
                    dimm_max_price: parseInt(getComponentBudgetValue("ramValue", "ram", false)),
                    ssd_m2_max_price: parseInt(getComponentBudgetValue("storageValue", "storage", false)),
                    motherboard_max_price: parseInt(getComponentBudgetValue("motherboardValue", "motherboard", false)),
                    power_supply_max_price: parseInt(getComponentBudgetValue("psuValue", "psu", false))
                };
                
                formData.components.optional_allocation.fixed_price_based = {
                    case_fan_max_price: parseInt(getComponentBudgetValue("coolingValue", "cooling", false)),
                    pc_case_max_price: parseInt(getComponentBudgetValue("caseValue", "case", false)),
                    cpu_cooler_max_price: parseInt(getComponentBudgetValue("cpuCoolerValue", "cpuCooler", false))
                };
            }

            console.log("Отправка данных:", JSON.stringify(formData, null, 2));

            // Отправка на сервер
            fetch('/configurator/log-click', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            }).then(response => {
                if (!response.ok) console.error("Ошибка при отправке данных");
            }).catch(error => {
                console.error("Ошибка запроса:", error);
            });
        });
    }

    // Обработка переключения между "Любое" и "Выбрать свой компонент"
    document.querySelectorAll('.component-select').forEach(select => {
        select.addEventListener('change', function() {
            const componentType = this.id.replace('Select', '');
            const customRow = document.getElementById(`${componentType}CustomRow`);
            if (customRow) {
                customRow.style.display = this.value === 'custom' ? 'flex' : 'none';
            }
        });
    });

    // Обновление placeholder'ов при смене метода расчета
    const updatePlaceholders = () => {
        const isPercentage = document.getElementById("budgetPercent").checked;
        document.querySelectorAll('.value-input').forEach(input => {
            const parts = input.placeholder.split(' (или ');
            if (parts.length === 2) {
                input.placeholder = isPercentage ? parts[0] : parts[1].replace(')', '');
            }
        });
    };

    document.getElementById("budgetRub")?.addEventListener('change', updatePlaceholders);
    document.getElementById("budgetPercent")?.addEventListener('change', updatePlaceholders);
    updatePlaceholders(); // Инициализация при загрузке
});