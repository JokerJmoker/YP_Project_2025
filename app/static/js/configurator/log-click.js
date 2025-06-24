document.addEventListener("DOMContentLoaded", () => {
    const gameCards = document.querySelectorAll(".game-card");

    gameCards.forEach(card => {
        card.addEventListener("click", () => {
            const gameId = card.dataset.gameId;
            const gameName = card.querySelector("h3")?.textContent || "Unknown";

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
            }).catch(err => console.error('Ошибка отправки на сервер:', err));
        });
    });
});
