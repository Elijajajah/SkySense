document.addEventListener('DOMContentLoaded', function () {
    // Mobile menu toggle
    const mobileMenuButton = document.querySelector('.mobile-menu-button');
    const mobileMenu = document.querySelector('.mobile-menu');

    if (mobileMenuButton && mobileMenu) {
        mobileMenuButton.addEventListener('click', function () {
            mobileMenu.classList.toggle('hidden');
            const icon = mobileMenuButton.querySelector('svg');
            if (mobileMenu.classList.contains('hidden')) {
                icon.setAttribute('data-feather', 'menu');
            } else {
                icon.setAttribute('data-feather', 'x');
            }
            feather.replace();
        });
    }

    // Smooth scrolling
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                targetElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
                if (!mobileMenu.classList.contains('hidden')) {
                    mobileMenu.classList.add('hidden');
                    mobileMenuButton.querySelector('svg').setAttribute('data-feather', 'menu');
                    feather.replace();
                }
            }
        });
    });

    const weatherForm = document.getElementById('weatherForm');
    if (!weatherForm) return;

    // Friendly names and gradients
    const weatherNames = {
        drizzle: 'Drizzly',
        rain: 'Rainy',
        sun: 'Sunny',
        snow: 'Snowy',
        fog: 'Foggy'
    };

    const weatherGradients = {
        drizzle: 'from-blue-300 to-blue-500',
        rain: 'from-indigo-400 to-blue-700',
        sun: 'from-yellow-400 to-orange-500',
        snow: 'from-white to-gray-300',
        fog: 'from-gray-400 to-gray-600'
    };

    // Submit event
    weatherForm.addEventListener('submit', async function (e) {
        e.preventDefault();

        const inputs = ['precipitation', 'temp_max', 'temp_min', 'wind'];

        // Clear errors
        inputs.forEach(id => {
            const errEl = document.getElementById(id + 'Error');
            errEl.textContent = '';
            errEl.classList.add('hidden');
            document.getElementById(id).classList.remove('border-red-500');
        });

        // Values
        const precipitation = parseFloat(document.getElementById('precipitation').value);
        const tempMax = parseFloat(document.getElementById('temp_max').value);
        const tempMin = parseFloat(document.getElementById('temp_min').value);
        const wind = parseFloat(document.getElementById('wind').value);

        let hasError = false;

        // -------- FIXED VALIDATION --------
        if (isNaN(precipitation) || precipitation < 0 || precipitation > 35) {
            const errEl = document.getElementById('precipitationError');
            errEl.textContent = 'Precipitation must be between 0 and 35 mm';
            errEl.classList.remove('hidden');
            document.getElementById('precipitation').classList.add('border-red-500');
            hasError = true;
        }

        if (isNaN(tempMax) || tempMax < -2 || tempMax > 36) {
            const errEl = document.getElementById('temp_maxError');
            errEl.textContent = 'Max Temp must be between -2°C and 36°C';
            errEl.classList.remove('hidden');
            document.getElementById('temp_max').classList.add('border-red-500');
            hasError = true;
        }

        if (isNaN(tempMin) || tempMin < -8 || tempMin > tempMax) {
            const errEl = document.getElementById('temp_minError');
            errEl.textContent = 'Min Temp must be ≤ Max Temp';
            errEl.classList.remove('hidden');
            document.getElementById('temp_min').classList.add('border-red-500');
            hasError = true;
        }

        if (isNaN(wind) || wind < 0 || wind > 8) {
            const errEl = document.getElementById('windError');
            errEl.textContent = 'Wind must be between 0 and 8 km/h';
            errEl.classList.remove('hidden');
            document.getElementById('wind').classList.add('border-red-500');
            hasError = true;
        }

        if (hasError) return;

        // Prediction UI elements
        const resultPlaceholder = document.getElementById('resultPlaceholder');
        const resultDisplay = document.getElementById('resultDisplay');

        resultPlaceholder.classList.add('hidden');
        resultDisplay.classList.remove('hidden');

        try {
            const response = await fetch('http://127.0.0.1:8000/predict', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    precipitation,
                    temp_max: tempMax,
                    temp_min: tempMin,
                    wind
                })
            });

            if (!response.ok) throw new Error('Network response was not ok');

            const data = await response.json();
            console.log(data);

            // API fields
            const confidence = data.confidence_percent;
            const weatherType = data.prediction.toLowerCase();

            const friendlyName = weatherNames[weatherType] || 'Unknown';
            const gradientClass = weatherGradients[weatherType] || weatherGradients['sun'];

            // Update UI
            document.getElementById('weatherType').textContent = friendlyName;
            document.getElementById('weatherType').className =
                'text-2xl md:text-3xl font-extrabold bg-clip-text text-transparent bg-gradient-to-r ' + gradientClass;

            document.getElementById('weatherDescription').textContent =
                `Predicted weather with a confidence of ${confidence}%`;

            const confidenceValueEl = document.getElementById('confidenceValue');
            const confidencePath = document.getElementById('confidencePath');
            animateCircle(confidence);

            resultDisplay.style.animation = 'fadeIn 0.5s ease-in forwards';

        } catch (error) {
            console.error(error);
            document.getElementById('weatherType').textContent = 'Error';
            document.getElementById('weatherDescription').textContent =
                'Unable to fetch prediction. Please try again.';
            document.getElementById('confidenceValue').textContent = '--';
        }
    });

    // Animate circle graph
    function animateCircle(confidence) {
        const confidencePath = document.getElementById('confidencePath');
        const confidenceValueEl = document.getElementById('confidenceValue');
        const circumference = 2 * Math.PI * 15.9155;

        let start = null;
        const initialOffset = circumference; // start at 0% filled
        const targetOffset = circumference * (1 - confidence / 100);

        function step(timestamp) {
            if (!start) start = timestamp;
            const progress = Math.min((timestamp - start) / 1000, 1); // 1 second animation
            const currentOffset = initialOffset + (targetOffset - initialOffset) * progress;
            confidencePath.style.strokeDasharray = `${circumference}`;
            confidencePath.style.strokeDashoffset = currentOffset;
            confidenceValueEl.textContent = `${Math.round(progress * confidence)}%`;

            if (progress < 1) {
                requestAnimationFrame(step);
            } else {
                confidenceValueEl.textContent = `${confidence}%`;
            }
        }

        requestAnimationFrame(step);
    }
});

document.addEventListener('DOMContentLoaded', () => {
    const weatherForm = document.getElementById('weatherForm');
    const randomizeButton = document.getElementById('randomizeButton');

    randomizeButton.addEventListener('click', () => {

        // Random number helper
        const rand = (min, max, decimals = 1) => +(Math.random() * (max - min) + min).toFixed(decimals);

        // 5 weather profiles with min/max ranges from your table
        const profiles = [
            // drizzle
            () => {
                const tempMax = rand(1.1, 31.7);
                const tempMin = rand(-3.9, tempMax); // cannot exceed tempMax
                return {
                    precipitation: rand(0.0, 0.0),
                    tempMax,
                    tempMin,
                    wind: rand(0.6, 4.7)
                };
            },
            // fog
            () => {
                const tempMax = rand(1.7, 30.6);
                const tempMin = rand(-3.2, tempMax);
                return {
                    precipitation: rand(0.0, 0.0),
                    tempMax,
                    tempMin,
                    wind: rand(0.8, 6.6)
                };
            },
            // rain
            () => {
                const tempMax = rand(3.9, 35.6);
                const tempMin = rand(-3.8, tempMax);
                return {
                    precipitation: rand(0.0, 32.38),
                    tempMax,
                    tempMin,
                    wind: rand(0.5, 7.54)
                };
            },
            // snow
            () => {
                const tempMax = rand(-1.1, 11.1);
                const tempMin = rand(-4.3, tempMax);
                return {
                    precipitation: rand(0.3, 23.9),
                    tempMax,
                    tempMin,
                    wind: rand(1.6, 7.0)
                };
            },
            // sun
            () => {
                const tempMax = rand(-1.6, 35.0);
                const tempMin = rand(-7.1, tempMax);
                return {
                    precipitation: rand(0.0, 0.0),
                    tempMax,
                    tempMin,
                    wind: rand(0.4, 7.54)
                };
            }
        ];

        // Randomly pick a weather profile
        const profile = profiles[Math.floor(Math.random() * profiles.length)]();

        // Fill the form
        document.getElementById('precipitation').value = profile.precipitation;
        document.getElementById('temp_max').value = profile.tempMax;
        document.getElementById('temp_min').value = profile.tempMin;
        document.getElementById('wind').value = profile.wind;

        weatherForm.requestSubmit();
    });
});
