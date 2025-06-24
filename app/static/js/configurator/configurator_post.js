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

            // Получаем все настройки
            const graphicsSelect = document.getElementById("graphicsSelect");
            const graphicsQuality = graphicsSelect ? graphicsSelect.value : "High";
            
            const fpsSelect = document.getElementById("fpsSelect");
            const targetFps = fpsSelect ? parseInt(fpsSelect.value) : 60;
            
            const resolutionSelect = document.getElementById("resolutionSelect");
            const resolution = resolutionSelect ? parseInt(resolutionSelect.value) : 1080;
            
            const rayTracingSelect = document.getElementById("rayTracingSelect");
            const rayTracingValue = rayTracingSelect ? rayTracingSelect.value : "off";
            const rayTracingEnabled = rayTracingValue !== "off";

  

            const logData = {
                user_selections: {
                    game: {
                        title: selectedGameName.replace(/ /g, "_"),
                        graphics_settings: {
                            quality: graphicsQuality,
                            target_fps: targetFps,
                            resolution: resolution,
                            ray_tracing: rayTracingEnabled,
                        }
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