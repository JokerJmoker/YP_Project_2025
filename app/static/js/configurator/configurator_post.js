document.addEventListener("DOMContentLoaded", () => {
    let selectedGameName = null;

    // Обработчик клика по игре
    const gameCards = document.querySelectorAll(".game-card");
    gameCards.forEach(card => {
        card.addEventListener("click", () => {
            selectedGameName = card.querySelector("h3")?.textContent || "Unknown";
            console.log(`Выбрана игра: ${selectedGameName}`);
        });
    });

    // Обработчик клика по кнопке "Далее"
    const btnNext = document.querySelector(".btn-next");
    if (btnNext) {
        btnNext.addEventListener("click", (event) => {
            if (!selectedGameName) {
                event.preventDefault();
                alert("Пожалуйста, выберите игру перед продолжением.");
                return;
            }

            // Получаем текущие настройки графики и FPS
            const graphicsSelect = document.getElementById("graphicsSelect");
            const graphicsQuality = graphicsSelect ? graphicsSelect.value : "High";
            
            // Исправлено: используем правильный ID для FPS select
            const fpsSelect = document.getElementById("fpsSelect");
            const targetFps = fpsSelect ? parseInt(fpsSelect.value) : 60;

            console.log(`Выбранный FPS: ${targetFps}`); // Добавьте эту строку для отладки

            // Формируем JSON
            const logData = {
                user_selections: {
                    game: {
                        title: selectedGameName.replace(/ /g, "_"),
                        graphics_settings: {
                            quality: graphicsQuality,
                            target_fps: targetFps
                        }
                    }
                }
            };

            console.log("Отправляем лог:", JSON.stringify(logData, null, 2));

            // Отправляем на сервер
            fetch('/configurator/log-click', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    gameName: selectedGameName,
                    graphicsQuality: graphicsQuality,
                    targetFps: targetFps, // Убедитесь, что это поле совпадает с бэкендом
                    timestamp: new Date().toISOString()
                })
            }).then(response => {
                if (!response.ok) {
                    console.error("Ошибка при отправке данных на сервер.");
                }
            }).catch(error => {
                console.error("Ошибка запроса:", error);
            });
        });
    }
});