document.addEventListener('DOMContentLoaded', function() {
    // Элементы DOM
    const steps = document.querySelectorAll('.config-step');
    const stepIndicators = document.querySelectorAll('.step-indicator span');
    const btnPrev = document.getElementById('btnPrev');
    const btnNext = document.getElementById('btnNext');
    let currentStep = 0;
    
    // Инициализация первого шага
    showStep(currentStep);
    
    // Навигация по шагам
    btnNext.addEventListener('click', function() {
        if (currentStep < steps.length - 1) {
            currentStep++;
            showStep(currentStep);
        } else {
            submitConfig();
        }
    });
    
    btnPrev.addEventListener('click', function() {
        if (currentStep > 0) {
            currentStep--;
            showStep(currentStep);
        }
    });
    
    // Показ текущего шага
    function showStep(stepIndex) {
        steps.forEach((step, index) => {
            step.classList.toggle('active', index === stepIndex);
        });
        
        stepIndicators.forEach((indicator, index) => {
            indicator.classList.toggle('active', index <= stepIndex);
        });
        
        btnPrev.style.visibility = stepIndex === 0 ? 'hidden' : 'visible';
        btnNext.textContent = stepIndex === steps.length - 1 ? 'Завершить' : 'Далее';
    }
    
    // Выбор игры
    const gameCards = document.querySelectorAll('.game-card');
    gameCards.forEach(card => {
        card.addEventListener('click', function() {
            gameCards.forEach(c => c.classList.remove('active'));
            this.classList.add('active');
        });
    });
    
    // Выбор FPS
    const fpsOptions = document.querySelectorAll('.fps-option');
    const fpsRange = document.getElementById('fpsRange');
    
    fpsOptions.forEach(option => {
        option.addEventListener('click', function() {
            fpsOptions.forEach(opt => opt.classList.remove('active'));
            this.classList.add('active');
            fpsRange.value = this.dataset.fps;
        });
    });
    
    fpsRange.addEventListener('input', function() {
        const fpsValue = this.value;
        fpsOptions.forEach(option => {
            option.classList.toggle('active', option.dataset.fps === fpsValue);
        });
    });
    
    // Настройка бюджета
    const budgetRange = document.getElementById('budgetRange');
    const budgetValue = document.getElementById('budgetValue');
    
    budgetRange.addEventListener('input', function() {
        budgetValue.textContent = new Intl.NumberFormat('ru-RU').format(this.value);
    });
    
    // Поиск комплектующих
    const gpuSearch = document.getElementById('gpuSearch');
    const cpuSearch = document.getElementById('cpuSearch');
    const gpuResults = document.getElementById('gpuResults');
    const cpuResults = document.getElementById('cpuResults');
    
    // Пример данных для поиска
    const gpuList = [
        { name: "NVIDIA RTX 4090", desc: "24GB GDDR6X" },
        { name: "AMD RX 7900 XTX", desc: "24GB GDDR6" },
        { name: "NVIDIA RTX 4080", desc: "16GB GDDR6X" }
    ];
    
    const cpuList = [
        { name: "Intel Core i9-13900K", desc: "24 ядра, 5.8 ГГц" },
        { name: "AMD Ryzen 9 7950X", desc: "16 ядер, 5.7 ГГц" },
        { name: "Intel Core i7-13700K", desc: "16 ядер, 5.4 ГГц" }
    ];
    
    // Функция для отображения результатов поиска
    function showSearchResults(input, results, data) {
        const searchTerm = input.value.toLowerCase();
        results.innerHTML = '';
        
        if (searchTerm.length < 2) {
            results.style.display = 'none';
            return;
        }
        
        const filtered = data.filter(item => 
            item.name.toLowerCase().includes(searchTerm) || 
            item.desc.toLowerCase().includes(searchTerm)
        );
        
        if (filtered.length > 0) {
            filtered.forEach(item => {
                const div = document.createElement('div');
                div.innerHTML = `<strong>${item.name}</strong><br><small>${item.desc}</small>`;
                div.addEventListener('click', function() {
                    input.value = item.name;
                    results.style.display = 'none';
                });
                results.appendChild(div);
            });
            results.style.display = 'block';
        } else {
            results.style.display = 'none';
        }
    }
    
    // Обработчики поиска
    gpuSearch.addEventListener('input', () => showSearchResults(gpuSearch, gpuResults, gpuList));
    cpuSearch.addEventListener('input', () => showSearchResults(cpuSearch, cpuResults, cpuList));
    
    // Закрытие результатов при клике вне поля
    document.addEventListener('click', function(e) {
        if (!gpuSearch.contains(e.target)) gpuResults.style.display = 'none';
        if (!cpuSearch.contains(e.target)) cpuResults.style.display = 'none';
    });
    
    // Отправка конфигурации
    function submitConfig() {
        const config = {
            game: document.querySelector('.game-card.active h3')?.textContent || 'Не выбрано',
            fps: fpsRange.value,
            budget: budgetRange.value,
            gpu: gpuSearch.value,
            cpu: cpuSearch.value
        };
        
        console.log('Конфигурация сохранена:', config);
        alert('Ваша конфигурация успешно сохранена!');
        
        // Здесь можно добавить AJAX-запрос для отправки данных на сервер
    }

    document.querySelectorAll('.step-tab').forEach(tab => {
        tab.addEventListener('click', function() {
            const stepIndex = parseInt(this.dataset.step) - 1;
            if (stepIndex >= 0 && stepIndex < steps.length) {
                currentStep = stepIndex;
                showStep(currentStep);
            }
        });
    });

    document.addEventListener('DOMContentLoaded', function() {
        const fpsRange = document.getElementById('fpsRange');
        
        function updateSlider() {
            const value = fpsRange.value;
            const min = fpsRange.min || 60;
            const max = fpsRange.max || 360;
            const percent = ((value - min) / (max - min)) * 100;
            
            // Для WebKit
            fpsRange.style.background = `linear-gradient(to right, #ff6b00 0%, #ff6b00 ${percent}%, #121212 ${percent}%, #121212 100%)`;
        }
        
        fpsRange.addEventListener('input', updateSlider);
        updateSlider(); // Инициализация
    });
});