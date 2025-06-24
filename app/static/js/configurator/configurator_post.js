document.addEventListener("DOMContentLoaded", () => {
    let selectedGameName = null;

    // Обработчик клика по игре — просто запоминаем название
    const gameCards = document.querySelectorAll(".game-card");
    gameCards.forEach(card => {
        card.addEventListener("click", () => {
            selectedGameName = card.querySelector("h3")?.textContent || "Unknown";
            console.log(`Выбрана игра: ${selectedGameName}`);
            // Можно добавить визуальный эффект выбора, если надо
        });
    });

    // Обработчик клика по кнопке "Далее"
    const btnNext = document.querySelector(".btn-next");
    if (btnNext) {
        btnNext.addEventListener("click", (event) => {
            // Если игра не выбрана — можно отменить переход или предупредить
            if (!selectedGameName) {
                event.preventDefault();
                alert("Пожалуйста, выберите игру перед продолжением.");
                return;
            }

            // Получаем текущие настройки графики
            const graphicsSelect = document.getElementById("graphicsSelect");
            const graphicsQuality = graphicsSelect ? graphicsSelect.value : "High";

            // Формируем JSON
            const logData = {
                user_selections: {
                    game: {
                        title: selectedGameName.replace(/ /g, "_"),
                        graphics_settings: {
                            quality: graphicsQuality
                        }
                    }
                }
            };

            console.log("Отправляем лог:", JSON.stringify(logData, null, 2));

            // Отправляем на сервер (fetch)
            fetch('/configurator/log-click', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    gameName: selectedGameName,
                    graphicsQuality: graphicsQuality,
                    timestamp: new Date().toISOString()
                })
            }).then(response => {
                if (!response.ok) {
                    console.error("Ошибка при отправке данных на сервер.");
                } else {
                    // Если хочешь, чтобы после успешного лога переход состоялся, можно ничего не делать,
                    // так как ссылка будет работать.
                }
            }).catch(error => {
                console.error("Ошибка запроса:", error);
            });

            // Если хочешь — можно позволить ссылке сработать и перейти далее
            // или закомментировать event.preventDefault() если нужно заблокировать переход
        });
    }
});
