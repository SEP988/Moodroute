/**
 * MoodRoute — Main Application Logic
 * Full-map background, two draggable floating boxes:
 *   - Input box  (mood input + pills + location + find button)
 *   - Result box (route result — appears after finding, hides input)
 * All route recommendations use real backend API calls.
 */

const MoodRouteApp = {

    currentLocation: { lat: -34.4054, lng: 150.8784 },
    selectedMood:    null,
    currentWeather:  null,
    currentRoute:    null,

    // ── Init ─────────────────────────────────────────────────────────────
    start() {
        MapManager.init();
        this.setupEventListeners();
        this.makeDraggable('inputBox',   'inputBoxHandle');
        this.makeDraggable('resultBox',  'resultBoxHandle');
        this.makeDraggable('indoorBox',  'indoorBoxHandle');
        this.setupToggle('inputBox',  'inputBoxHandle');
        this.setupToggle('resultBox', 'resultBoxHandle');
        this.setupToggle('indoorBox', 'indoorBoxHandle');
        this.loadWeather(this.currentLocation.lat, this.currentLocation.lng);
        MapManager.addUserMarker(this.currentLocation.lat, this.currentLocation.lng);
    },

    // ── Detect mobile ────────────────────────────────────────────────────
    isMobile() {
        return window.innerWidth <= 768;
    },

    // ── Toggle expand / collapse on handle tap or click ──────────────────
    // Works on both desktop (mouse) and mobile (touch).
    // Skipped if the user was dragging (movedDistance > 5px).
    setupToggle(boxId, handleId) {
        const handle = document.getElementById(handleId);
        if (!handle) return;

        // Mouse click (desktop)
        handle.addEventListener('click', () => {
            if (handle._wasDragging) {
                handle._wasDragging = false;
                return;
            }
            const box = document.getElementById(boxId);
            if (box) box.classList.toggle('minimised');
        });

        // Touch end (mobile) — more reliable than click on touch devices
        handle.addEventListener('touchend', (e) => {
            if (handle._wasDragging) {
                handle._wasDragging = false;
                return;
            }
            e.preventDefault(); // prevent ghost click
            const box = document.getElementById(boxId);
            if (box) box.classList.toggle('minimised');
        }, { passive: false });
    },

    // ── Make any box draggable ───────────────────────────────────────────
    makeDraggable(boxId, handleId) {
        const box    = document.getElementById(boxId);
        const handle = document.getElementById(handleId);
        if (!box || !handle) return;

        let dragging = false;
        let movedDistance = 0;
        let startMouseX = 0, startMouseY = 0;
        let startLeft = 0, startTop = 0;

        const onStart = (e) => {
            dragging = true;
            movedDistance = 0;
            const cx = e.touches ? e.touches[0].clientX : e.clientX;
            const cy = e.touches ? e.touches[0].clientY : e.clientY;
            const rect = box.getBoundingClientRect();

            startMouseX = cx;
            startMouseY = cy;
            startLeft   = rect.left;
            startTop    = rect.top;

            // Fix position so it can move freely
            box.style.left   = `${rect.left}px`;
            box.style.top    = `${rect.top}px`;
            box.style.bottom = 'auto';
            box.style.right  = 'auto';
            e.preventDefault();
        };

        const onMove = (e) => {
            if (!dragging) return;
            const cx = e.touches ? e.touches[0].clientX : e.clientX;
            const cy = e.touches ? e.touches[0].clientY : e.clientY;

            const dx = cx - startMouseX;
            const dy = cy - startMouseY;
            movedDistance = Math.sqrt(dx * dx + dy * dy);

            const newLeft = Math.max(0, Math.min(window.innerWidth  - box.offsetWidth,  startLeft + dx));
            const newTop  = Math.max(87, Math.min(window.innerHeight - box.offsetHeight - 38, startTop  + dy));

            box.style.left = `${newLeft}px`;
            box.style.top  = `${newTop}px`;
        };

        const onEnd = () => {
            if (!dragging) return;
            dragging = false;
            // If the user moved more than 5px, flag it so the click handler
            // knows to skip the toggle (the click fires right after mouseup)
            if (movedDistance > 5) {
                handle._wasDragging = true;
            }
        };

        handle.addEventListener('touchstart',  onStart, { passive: false });
        document.addEventListener('touchmove',  onMove,  { passive: true });
        document.addEventListener('touchend',   onEnd);
        handle.addEventListener('mousedown',    onStart);
        document.addEventListener('mousemove',  onMove);
        document.addEventListener('mouseup',    onEnd);
    },

    // ── Event listeners ──────────────────────────────────────────────────
    setupEventListeners() {
        // Mood pills
        document.getElementById('moodPills').addEventListener('click', (e) => {
            const pill = e.target.closest('.mood-pill');
            if (pill) this.selectMoodPill(pill.dataset.mood, pill);
        });

        // GPS
        document.getElementById('gpsBtn').addEventListener('click', () => this.requestGPSLocation());

        // Find route button
        document.getElementById('findBtn').addEventListener('click', () => this.findRoute());

        // Enter key in textarea
        document.getElementById('moodInput').addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.findRoute();
            }
        });

        // Enter key in location input
        document.getElementById('locationInput').addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                this.geocodeAddress(document.getElementById('locationInput').value);
            }
        });

        // Star rating
        document.getElementById('stars').addEventListener('click', (e) => {
            const star = e.target.closest('.star');
            if (star) this.submitRating(parseInt(star.dataset.star, 10));
        });

        // Back buttons
        document.getElementById('backBtn').addEventListener('click', () => this.resetToInput());
        document.getElementById('indoorBackBtn').addEventListener('click', () => this.resetToInput());
    },

    // ── Mood pill selection ──────────────────────────────────────────────
    selectMoodPill(mood, element) {
        document.querySelectorAll('.mood-pill').forEach(p => p.classList.remove('active'));
        element.classList.add('active');
        this.selectedMood = mood;
    },

    // ── GPS ──────────────────────────────────────────────────────────────
    requestGPSLocation() {
        if (!navigator.geolocation) {
            this.showToast('Geolocation not supported');
            return;
        }
        navigator.geolocation.getCurrentPosition(
            (pos) => {
                const lat = pos.coords.latitude;
                const lng = pos.coords.longitude;
                this.currentLocation = { lat, lng };
                document.getElementById('locationInput').value = `${lat.toFixed(4)}, ${lng.toFixed(4)}`;
                MapManager.setView(lat, lng);
                MapManager.addUserMarker(lat, lng);
                this.loadWeather(lat, lng);
                this.showToast('✅ Location updated');
            },
            () => this.showToast('Could not get location')
        );
    },

    // ── Weather ──────────────────────────────────────────────────────────
    async loadWeather(lat, lng) {
        try {
            const resp = await fetch(`/api/weather?lat=${lat}&lng=${lng}`);
            if (!resp.ok) return;
            const data = await resp.json();
            const w = data.weather || data;
            this.currentWeather = w;
            document.getElementById('weatherIcon').textContent = w.icon || '🌤️';
            document.getElementById('weatherTemp').textContent = `${Math.round(w.temp || 0)}°C`;
        } catch { /* silent */ }
    },

    // ── Find route ───────────────────────────────────────────────────────
    async findRoute() {
        const moodText = this.sanitize(document.getElementById('moodInput').value.trim());
        if (!moodText && !this.selectedMood) {
            this.showToast('💬 Type how you feel or select a mood');
            return;
        }

        this.showLoading('Analysing your mood...');
        document.getElementById('findBtn').disabled = true;

        try {
            await this.animateLoadingSteps();

            const payload = {
                lat: this.currentLocation.lat,
                lng: this.currentLocation.lng
            };
            if (moodText)           payload.text = moodText;
            if (this.selectedMood)  payload.mood = this.selectedMood;

            const resp = await fetch('/api/find-route', {
                method:  'POST',
                headers: { 'Content-Type': 'application/json' },
                body:    JSON.stringify(payload)
            });

            if (!resp.ok) {
                const err = await resp.json().catch(() => ({}));
                throw new Error(err.error || 'Route search failed');
            }

            const data = await resp.json();

            if (data.indoor_alternatives === true && data.alternatives) {
                this.showIndoorAlternatives(data);
            } else if (data.routes && data.routes.length > 0) {
                this.showRouteResult(data);
            } else {
                this.showToast('No routes found near your location');
            }

        } catch (err) {
            this.showToast(err.message || 'Something went wrong');
        } finally {
            this.hideLoading();
            document.getElementById('findBtn').disabled = false;
        }
    },

    // ── Animate loading steps ────────────────────────────────────────────
    async animateLoadingSteps() {
        const steps = [
            '🧠 Detecting your mood...',
            '🌿 Scanning green spaces...',
            '☁️ Checking weather...',
            '⛰️ Analysing terrain...',
            '🏆 Ranking routes...'
        ];
        for (const step of steps) {
            document.getElementById('loadingStep').textContent = step;
            await this.delay(480);
        }
    },

    // ── Show route result — hide input box, show result box ──────────────
    showRouteResult(data) {
        const bestRoute = data.routes[0];
        this.currentRoute = bestRoute;

        // ── Mood badge ──
        const moodData   = data.mood || {};
        const emoji      = moodData.emoji || '🧠';
        const label      = moodData.label || moodData.category || '';
        document.getElementById('resultMood').textContent = `${emoji} ${label}`;
        document.getElementById('resultHandleLabel').textContent = `🗺️ ${bestRoute.name}`;

        // ── Confidence ──
        const pct = moodData.confidence ? Math.round(moodData.confidence * 100) : 0;
        document.getElementById('confidenceText').textContent = `${pct}%`;
        setTimeout(() => {
            document.getElementById('confidenceFill').style.width = `${pct}%`;
        }, 100);

        // ── Route name & meta ──
        document.getElementById('routeName').textContent = bestRoute.name || 'Recommended Route';
        const km  = bestRoute.distance_km || '--';
        const min = Math.round((parseFloat(km) || 0) * 12);
        document.getElementById('routeMeta').innerHTML = `
            <span class="route-tag">🚶 ${km} km</span>
            <span class="route-tag">⏱️ ${min} min</span>
            <span class="route-tag">⭐ ${bestRoute.total_score || '--'}/10</span>`;

        // ── Start / End points ──
        const startName = bestRoute.start_point || 'UOW Campus';
        const endName   = bestRoute.end_point   || 'Destination';
        document.getElementById('routePoints').innerHTML = `
            <div class="route-point">
                <span class="route-point__marker route-point__marker--start">●</span>
                <span>${startName}</span>
            </div>
            <div class="route-point__line"></div>
            <div class="route-point">
                <span class="route-point__marker route-point__marker--end">●</span>
                <span>${endName}</span>
            </div>`;

        // ── Score bars ──
        const scores = bestRoute.scores || {};
        const keyMap = { quietness: 'quiet', flatness: 'flat' };
        const metrics = [
            { label: 'Greenery',  key: 'greenery',  color: '#4a7c59' },
            { label: 'Quietness', key: 'quiet',      color: '#5b8db8' },
            { label: 'Flatness',  key: 'flat',       color: '#8e44ad' },
            { label: 'Seclusion', key: 'uncrowded',  color: '#c17f3e' },
        ];
        document.getElementById('scoreBars').innerHTML = metrics.map(m => {
            const val = scores[m.key] ?? scores[keyMap[m.key]] ?? 0;
            const pct = Math.round((val / 10) * 100);
            return `<div class="score-row">
                <div class="score-label">${m.label}</div>
                <div class="score-track">
                    <div class="score-fill" style="width:0%;background:${m.color}" data-target="${pct}"></div>
                </div>
                <div class="score-val">${val}</div>
            </div>`;
        }).join('');
        setTimeout(() => {
            document.querySelectorAll('.score-fill').forEach(b => {
                b.style.width = b.dataset.target + '%';
            });
        }, 300);

        // ── Explanation ──
        document.getElementById('routeExplanation').textContent =
            bestRoute.explanation || moodData.description || '';

        // ── Reset stars ──
        document.querySelectorAll('.star').forEach(s => s.classList.remove('lit'));

        // ── Draw map route ──
        if (bestRoute.coordinates && bestRoute.coordinates.length > 1) {
            MapManager.clearRoutes();
            MapManager.drawRoute(bestRoute.coordinates, '#1a3c2e', startName, endName);
            MapManager.fitToRoute(bestRoute.coordinates);
        }

        // ── Swap boxes: hide input, show result at same position ──
        const inputBox  = document.getElementById('inputBox');
        const resultBox = document.getElementById('resultBox');
        const rect      = inputBox.getBoundingClientRect();

        resultBox.style.left   = `${rect.left}px`;
        resultBox.style.top    = `${rect.top}px`;
        resultBox.style.bottom = 'auto';
        resultBox.style.right  = 'auto';

        inputBox.classList.add('hidden');
        resultBox.classList.remove('hidden');

        // On mobile: start minimised so the map route is visible immediately.
        // User taps the handle to expand the result details.
        if (this.isMobile()) {
            resultBox.classList.add('minimised');
        } else {
            resultBox.classList.remove('minimised');
        }

        this.showToast(`${emoji} ${label} detected — route found!`);
    },

    // ── Indoor alternatives ──────────────────────────────────────────────
    showIndoorAlternatives(data) {
        const w = data.weather || {};
        document.getElementById('indoorSubtitle').textContent =
            `${w.icon || '⛈️'} ${w.description || 'Dangerous weather'} — stay inside`;

        document.getElementById('indoorOptions').innerHTML = (data.alternatives || []).map(item => `
            <div class="indoor-option">
                <span style="font-size:1.2rem">${item.icon || '🏠'}</span>
                <div>
                    <div style="font-weight:600;font-size:0.82rem">${item.name}</div>
                    <div style="font-size:0.72rem;color:var(--muted)">${item.description || ''}</div>
                </div>
            </div>`).join('');

        const inputBox  = document.getElementById('inputBox');
        const indoorBox = document.getElementById('indoorBox');
        const rect      = inputBox.getBoundingClientRect();

        indoorBox.style.left   = `${rect.left}px`;
        indoorBox.style.top    = `${rect.top}px`;
        indoorBox.style.bottom = 'auto';

        inputBox.classList.add('hidden');
        indoorBox.classList.remove('hidden');

        // On mobile: start minimised so map is visible
        if (this.isMobile()) {
            indoorBox.classList.add('minimised');
        } else {
            indoorBox.classList.remove('minimised');
        }

        this.showToast('⛈️ Dangerous weather — indoor alternatives shown');
    },

    // ── Reset: hide result, show input box ───────────────────────────────
    resetToInput() {
        const inputBox  = document.getElementById('inputBox');
        const resultBox = document.getElementById('resultBox');
        const indoorBox = document.getElementById('indoorBox');
        const resultRect = resultBox.classList.contains('hidden')
            ? indoorBox.getBoundingClientRect()
            : resultBox.getBoundingClientRect();

        inputBox.style.left   = `${resultRect.left}px`;
        inputBox.style.top    = `${resultRect.top}px`;
        inputBox.style.bottom = 'auto';

        resultBox.classList.add('hidden');
        indoorBox.classList.add('hidden');
        inputBox.classList.remove('hidden');
        // Clear any minimised state for next time
        resultBox.classList.remove('minimised');
        indoorBox.classList.remove('minimised');

        MapManager.clearRoutes();
        MapManager.resetToUOW();

        document.getElementById('moodInput').value = '';
        this.selectedMood = null;
        document.querySelectorAll('.mood-pill').forEach(p => p.classList.remove('active'));
    },

    // ── Star rating ──────────────────────────────────────────────────────
    async submitRating(stars) {
        document.querySelectorAll('.star').forEach((s, i) => {
            s.classList.toggle('lit', i < stars);
        });
        if (!this.currentRoute) return;
        try {
            await fetch('/api/rate', {
                method:  'POST',
                headers: { 'Content-Type': 'application/json' },
                body:    JSON.stringify({
                    route_id:          this.currentRoute.id,
                    rating:            stars,
                    mood:              this.selectedMood || 'unknown',
                    weather_condition: this.currentWeather ? this.currentWeather.condition : ''
                })
            });
            this.showToast(`⭐ ${stars}/5 stars saved — thank you!`);
        } catch { this.showToast('Rating could not be saved'); }
    },

    // ── Geocode address ──────────────────────────────────────────────────
    async geocodeAddress(address) {
        if (!address || address.length < 3) return;
        const coords = address.match(/^(-?\d+\.?\d*),\s*(-?\d+\.?\d*)$/);
        if (coords) {
            const lat = parseFloat(coords[1]), lng = parseFloat(coords[2]);
            this.currentLocation = { lat, lng };
            MapManager.setView(lat, lng); MapManager.addUserMarker(lat, lng);
            this.loadWeather(lat, lng); return;
        }
        try {
            const resp = await fetch(
                `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(address)}&limit=1`,
                { headers: { 'Accept': 'application/json' } });
            const results = await resp.json();
            if (!results.length) { this.showToast('Location not found'); return; }
            const lat = parseFloat(results[0].lat), lng = parseFloat(results[0].lon);
            this.currentLocation = { lat, lng };
            document.getElementById('locationInput').value =
                results[0].display_name.split(',').slice(0, 2).join(',');
            MapManager.setView(lat, lng); MapManager.addUserMarker(lat, lng);
            this.loadWeather(lat, lng); this.showToast('Location set ✓');
        } catch { this.showToast('Could not find that location'); }
    },

    // ── Loading ──────────────────────────────────────────────────────────
    showLoading(text) {
        document.getElementById('loadingText').textContent = text || 'Loading...';
        document.getElementById('loadingOverlay').classList.remove('hidden');
    },

    hideLoading() {
        document.getElementById('loadingOverlay').classList.add('hidden');
    },

    // ── Toast ────────────────────────────────────────────────────────────
    showToast(msg) {
        const t = document.getElementById('toast');
        t.textContent = msg;
        t.classList.add('show');
        clearTimeout(this._toastTimer);
        this._toastTimer = setTimeout(() => t.classList.remove('show'), 3000);
    },

    sanitize(input) {
        return input ? input.replace(/<[^>]*>/g, '').substring(0, 300).trim() : '';
    },

    delay(ms) { return new Promise(r => setTimeout(r, ms)); }
};

document.addEventListener('DOMContentLoaded', () => MoodRouteApp.start());
