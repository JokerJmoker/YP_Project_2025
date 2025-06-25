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
        btnNext.addEventListener("click", async (event) => {
            event.preventDefault(); // Предотвращаем стандартную отправку формы
            
            if (!selectedGameName) {
                alert("Пожалуйста, выберите игру перед продолжением.");
                return;
            }

            // Показываем индикатор загрузки
            btnNext.disabled = true;
            btnNext.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Обработка...';

            try {
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
                            case_fan: "any",
                            pc_case: "any",
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
                const response = await fetch('/configurator/log-click', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(formData)
                });

                if (!response.ok) {
                    const errorData = await response.json().catch(() => ({}));
                    throw new Error(errorData.message || `Ошибка сервера: ${response.status}`);
                }

                const result = await response.json();
                
                if (result.status === "ok" && result.redirect_url) {
                    // Перенаправляем пользователя на указанный URL
                    window.location.href = result.redirect_url;
                } else {
                    throw new Error(result.message || "Неизвестная ошибка сервера");
                }
            } catch (error) {
                console.error("Ошибка при отправке данных:", error);
                
                // Создаем красивое сообщение об ошибке
                const errorMessage = `
                    <div class="alert alert-danger mt-3">
                        <strong>Ошибка!</strong> ${error.message || "Произошла неизвестная ошибка"}
                        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                    </div>
                `;
                
                // Вставляем сообщение об ошибке перед кнопкой
                const alertContainer = document.createElement('div');
                alertContainer.innerHTML = errorMessage;
                btnNext.parentNode.insertBefore(alertContainer, btnNext);
                
                // Автоматически закрываем сообщение через 5 секунд
                setTimeout(() => {
                    const alert = bootstrap.Alert.getOrCreateInstance(alertContainer.querySelector('.alert'));
                    alert.close();
                }, 5000);
            } finally {
                // Восстанавливаем кнопку в любом случае
                btnNext.disabled = false;
                btnNext.textContent = "Далее";
            }
        });
    }
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