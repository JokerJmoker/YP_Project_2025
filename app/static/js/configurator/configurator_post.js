document.addEventListener("DOMContentLoaded", () => {
    const gameCards = document.querySelectorAll(".game-card");

    gameCards.forEach(card => {
        card.addEventListener("click", () => {
            const gameName = card.querySelector("h3")?.textContent || "Unknown";

            // Формируем объект с нужной структурой
            const logData = {
                user_selections: {
                    game: {
                        title: gameName
                    }
                }
            };

            // Выводим в консоль в виде JSON-строки с отступами
            console.log(JSON.stringify(logData, null, 2));

            // Отправляем на сервер, если нужно
            fetch('/configurator/log-click', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    gameId: card.dataset.gameId,
                    gameName: gameName,
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
    });
});
