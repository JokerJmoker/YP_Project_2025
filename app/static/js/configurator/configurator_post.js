document.addEventListener("DOMContentLoaded", () => {
    const gameCards = document.querySelectorAll(".game-card");

    gameCards.forEach(card => {
        card.addEventListener("click", () => {
            const gameId = card.dataset.gameId;
            const gameName = card.querySelector("h3")?.textContent || "Unknown";

            console.log(`Clicked on: ${gameName} (ID: ${gameId})`);

            fetch('/configurator/log-click', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    gameId: gameId,
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
