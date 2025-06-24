document.addEventListener("DOMContentLoaded", () => {
    let selectedGameName = null;

    const gameCards = document.querySelectorAll(".game-card");
    gameCards.forEach(card => {
        card.addEventListener("click", () => {
            selectedGameName = card.querySelector("h3")?.textContent || "Unknown";
            console.log(`Выбрана игра: ${selectedGameName}`);
        });
    });

    const btnNext = document.querySelector(".btn-next");
    if (btnNext) {
        btnNext.addEventListener("click", (event) => {
            if (!selectedGameName) {
                event.preventDefault();
                alert("Пожалуйста, выберите игру перед продолжением.");
                return;
            }

            // Получаем все настройки графики
            const graphicsSelect = document.getElementById("graphicsSelect");
            const graphicsQuality = graphicsSelect ? graphicsSelect.value : "High";
            
            const fpsSelect = document.getElementById("fpsSelect");
            const targetFps = fpsSelect ? parseInt(fpsSelect.value) : 60;
            
            const resolutionSelect = document.getElementById("resolutionSelect");
            const resolution = resolutionSelect ? parseInt(resolutionSelect.value) : 1080;
            
            const rayTracingSelect = document.getElementById("rayTracingSelect");
            const rayTracingValue = rayTracingSelect ? rayTracingSelect.value : "off";
            const rayTracingEnabled = rayTracingValue !== "off";

            // Получаем настройки масштабирования
            const dlssSelect = document.getElementById("dlssSelect");
            const dlssValue = dlssSelect ? dlssSelect.value : "off";
            const dlssMapping = {
                "off": "Disabled",
                "dlss-quality": "Quality",
                "dlss-balanced": "Balanced",
                "dlss-performance": "Performance",
                "dlss-ultra-performance": "Ultra Performance"
            };
            const dlssSetting = dlssMapping[dlssValue] || "Disabled";

            const fsrSelect = document.getElementById("fsrSelect");
            const fsrValue = fsrSelect ? fsrSelect.value : "off";
            const fsrMapping = {
                "off": "Disabled",
                "fsr-quality": "Quality",
                "fsr-balanced": "Balanced",
                "fsr-performance": "Performance",
                "fsr-ultra-performance": "Ultra Performance"
            };
            const fsrSetting = fsrMapping[fsrValue] || "Disabled";

            // Получаем данные о бюджете
            const budgetRange = document.getElementById("budgetRange");
            const budgetValueElement = document.getElementById("budgetValue");
            let budgetAmount = 150000; // значение по умолчанию
            
            if (budgetRange && budgetValueElement) {
                budgetAmount = parseInt(budgetValueElement.textContent.replace(/\s/g, '').replace('₽', ''));
            }

            const budgetTypeRub = document.getElementById("budgetRub");
            const budgetTypePercent = document.getElementById("budgetPercent");
            let budgetAllocationMethod = "fixed_price_based"; // значение по умолчанию
            
            if (budgetTypeRub && budgetTypePercent) {
                budgetAllocationMethod = budgetTypeRub.checked ? "fixed_price_based" : "percentage_based";
            }

            // Получаем данные о комплектующих
            const components = {
                mandatory: {
                    cpu: getComponentSelection("cpuSelect", "cpuValue"),
                    gpu: getComponentSelection("gpuSelect", "gpuValue"),
                    dimm: getComponentSelection("ramSelect", "ramValue"),
                    ssd_m2: getComponentSelection("storageSelect", "storageValue"),
                    motherboard: getComponentSelection("motherboardSelect", "motherboardValue"),
                    power_supply: getComponentSelection("psuSelect", "psuValue")
                },
                mandatory_allocation: {
                    method: budgetAllocationMethod
                },
                optional: {
                    case_fan: getComponentValue("coolingValue"),
                    pc_case: getComponentValue("caseValue"),
                    cpu_cooler: getCpuCoolerType()
                },
                optional_allocation: {
                    method: budgetAllocationMethod
                }
            };

            // Добавляем данные о распределении бюджета для обязательных компонентов
            if (budgetAllocationMethod === "percentage_based") {
                components.mandatory_allocation.percentage_based = {
                    cpu_percentage: getPercentageValue("cpuValue"),
                    gpu_percentage: getPercentageValue("gpuValue"),
                    dimm_percentage: getPercentageValue("ramValue"),
                    ssd_m2_percentage: getPercentageValue("storageValue"),
                    motherboard_percentage: getPercentageValue("motherboardValue"),
                    power_supply_percentage: getPercentageValue("psuValue")
                };
                
                components.optional_allocation.percentage_based = {
                    case_fan_percentage: getPercentageValue("coolingValue", 0, 10),
                    pc_case_percentage: getPercentageValue("caseValue", 0, 10),
                    cpu_cooler_percentage: getPercentageValue("cpuCoolerValue", 0, 8)
                };
            } else {
                components.mandatory_allocation.fixed_price_based = {
                    cpu_max_price: getPriceValue("cpuValue"),
                    gpu_max_price: getPriceValue("gpuValue"),
                    dimm_max_price: getPriceValue("ramValue"),
                    ssd_m2_max_price: getPriceValue("storageValue"),
                    motherboard_max_price: getPriceValue("motherboardValue"),
                    power_supply_max_price: getPriceValue("psuValue")
                };
                
                components.optional_allocation.fixed_price_based = {
                    case_fan_max_price: getPriceValue("coolingValue", 2000, 15000),
                    pc_case_max_price: getPriceValue("caseValue", 3000, 20000),
                    cpu_cooler_max_price: getPriceValue("cpuCoolerValue", 2000, 10000)
                };
            }

            const logData = {
                user_selections: {
                    game: {
                        title: selectedGameName.replace(/ /g, "_"),
                        graphics_settings: {
                            quality: graphicsQuality,
                            target_fps: targetFps,
                            resolution: resolution,
                            ray_tracing: rayTracingEnabled,
                            dlss: dlssSetting,
                            fsr: fsrSetting
                        }
                    },
                    budget: {
                        amount: budgetAmount,
                        budget_allocation_method: budgetAllocationMethod
                    },
                    components: components
                }
            };

            console.log("Отправляем лог:", JSON.stringify(logData, null, 2));

            fetch('/configurator/log-click', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    gameName: selectedGameName,
                    graphicsQuality: graphicsQuality,
                    targetFps: targetFps,
                    resolution: resolution,
                    rayTracingEnabled: rayTracingEnabled,
                    rayTracingPreset: rayTracingValue,
                    dlss: dlssValue,
                    fsr: fsrValue,
                    budgetAmount: budgetAmount,
                    budgetAllocationMethod: budgetAllocationMethod,
                    components: components,
                    timestamp: new Date().toISOString()
                })
            }).then(response => {
                if (!response.ok) console.error("Ошибка при отправке данных");
            }).catch(error => {
                console.error("Ошибка запроса:", error);
            });
        });
    }

    // Вспомогательные функции
    function getComponentSelection(selectId, valueId) {
        const select = document.getElementById(selectId);
        const valueInput = document.getElementById(valueId);
        
        if (!select || !valueInput) return "any";
        
        if (select.value === "custom" && valueInput.value) {
            return valueInput.value;
        }
        return select.value;
    }

    function getComponentValue(inputId) {
        const input = document.getElementById(inputId);
        return input && input.value ? input.value : "any";
    }

    function getCpuCoolerType() {
        const select = document.getElementById("cpuCoolerType");
        if (!select) return "any";
        
        const mapping = {
            "liquid": "water_cooling",
            "air": "air_cooler",
            "any": "any",
            "included": "included_with_cpu"
        };
        return mapping[select.value] || "any";
    }

    function getPercentageValue(inputId, min = 0, max = 100) {
        const input = document.getElementById(inputId);
        if (!input || !input.value) return min;
        
        const value = input.value.replace(/[^\d%]/g, '');
        const percentage = parseInt(value) || min;
        return Math.min(Math.max(percentage, min), max);
    }

    function getPriceValue(inputId, min = 0, max = 300000) {
        const input = document.getElementById(inputId);
        if (!input || !input.value) return min;
        
        const value = input.value.replace(/\D/g, '');
        const price = parseInt(value) || min;
        return Math.min(Math.max(price, min), max);
    }
});