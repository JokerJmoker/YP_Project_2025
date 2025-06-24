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
                // Удаляем пробелы и знак рубля, затем преобразуем в число
                budgetAmount = parseInt(budgetValueElement.textContent.replace(/\s/g, '').replace('₽', ''));
            }

            const budgetTypeRub = document.getElementById("budgetRub");
            const budgetTypePercent = document.getElementById("budgetPercent");
            let budgetAllocationMethod = "fixed_price_based"; // значение по умолчанию
            
            if (budgetTypeRub && budgetTypePercent) {
                budgetAllocationMethod = budgetTypeRub.checked ? "fixed_price_based" : "percentage_based";
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
                    }
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
                    timestamp: new Date().toISOString()
                })
            }).then(response => {
                if (!response.ok) console.error("Ошибка при отправке данных");
            }).catch(error => {
                console.error("Ошибка запроса:", error);
            });
        });
    }
});