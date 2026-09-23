/**
 * MoodRoute — Map Management Module
 * Sidebar + map layout. UOW campus boundary + real walking paths.
 */

const MapManager = {
    map: null,
    routeLayer: null,
    markerLayer: null,
    boundaryLayer: null,
    userMarker: null,

    UOW_CENTER: [-34.4054, 150.8784],
    UOW_RADIUS: 5000,

    // ── Initialise ────────────────────────────────────────────────────────
    init() {
        this.map = L.map('map', {
            center: this.UOW_CENTER,
            zoom: 14,
            zoomControl: false
        });

        L.control.zoom({ position: 'topright' }).addTo(this.map);

        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
            maxZoom: 19
        }).addTo(this.map);

        this.boundaryLayer = L.layerGroup().addTo(this.map);
        this.routeLayer    = L.layerGroup().addTo(this.map);
        this.markerLayer   = L.layerGroup().addTo(this.map);

        this.drawUOWBoundary();
        return this;
    },

    // ── UOW boundary ─────────────────────────────────────────────────────
    drawUOWBoundary() {
        // Outer 5km service area circle (dashed)
        L.circle(this.UOW_CENTER, {
            radius: this.UOW_RADIUS,
            color: '#4a7c59',
            weight: 2,
            opacity: 0.5,
            fillColor: '#4a7c59',
            fillOpacity: 0.03,
            dashArray: '10, 8',
            interactive: false
        }).addTo(this.boundaryLayer);

        // Pulsing ring at campus centre
        L.marker(this.UOW_CENTER, {
            icon: L.divIcon({
                className: '',
                html: '<div class="uow-pulse-ring"></div>',
                iconSize: [80, 80],
                iconAnchor: [40, 40]
            }),
            interactive: false
        }).addTo(this.boundaryLayer);

        // UOW campus marker
        L.marker(this.UOW_CENTER, {
            icon: L.divIcon({
                className: 'uow-marker-container',
                html: '<div class="uow-marker"><span class="uow-marker__icon">🎓</span></div>',
                iconSize: [40, 40],
                iconAnchor: [20, 20]
            }),
            zIndexOffset: 500
        }).bindPopup(`
            <div style="font-family:'DM Sans',sans-serif;text-align:center;padding:4px 8px;">
                <strong>University of Wollongong</strong><br>
                <small style="color:#6b7f70;">All routes start from here</small>
            </div>
        `).addTo(this.boundaryLayer);

        // "5 km radius" label
        L.marker([this.UOW_CENTER[0] + 0.044, this.UOW_CENTER[1]], {
            icon: L.divIcon({
                className: 'boundary-label-container',
                html: '<div class="boundary-label">5 km service area</div>',
                iconSize: [110, 22],
                iconAnchor: [55, 11]
            }),
            interactive: false
        }).addTo(this.boundaryLayer);
    },

    // ── User marker ───────────────────────────────────────────────────────
    addUserMarker(lat, lng) {
        if (this.userMarker) this.map.removeLayer(this.userMarker);
        this.userMarker = L.marker([lat, lng], {
            icon: L.divIcon({
                className: 'user-marker-container',
                html: '<div class="user-marker"></div>',
                iconSize: [14, 14],
                iconAnchor: [7, 7]
            })
        }).addTo(this.map).bindPopup('📍 You are here');
    },

    // ── Draw walking route ────────────────────────────────────────────────
    drawRoute(coordinates, color = '#1a3c2e', startName = 'Start', endName = 'End') {
        if (!coordinates || coordinates.length < 2) return;

        // Shadow underline
        L.polyline(coordinates, {
            color: '#ffffff',
            weight: 9,
            opacity: 0.3,
            smoothFactor: 1,
            lineCap: 'round',
            lineJoin: 'round',
            interactive: false
        }).addTo(this.routeLayer).bringToBack();

        // Main route line
        L.polyline(coordinates, {
            color: color,
            weight: 5,
            opacity: 0.9,
            smoothFactor: 1,
            lineCap: 'round',
            lineJoin: 'round'
        }).addTo(this.routeLayer);

        // Direction arrows at 25%, 50%, 75%
        [0.25, 0.5, 0.75].forEach(fraction => {
            const idx = Math.floor(fraction * (coordinates.length - 1));
            if (idx < 1) return;
            const prev = coordinates[idx - 1];
            const curr = coordinates[idx];
            const angle = Math.atan2(curr[1] - prev[1], curr[0] - prev[0]) * (180 / Math.PI);
            L.marker(curr, {
                icon: L.divIcon({
                    className: 'route-arrow-container',
                    html: `<div class="route-arrow" style="transform:rotate(${-angle + 90}deg);color:${color};">›</div>`,
                    iconSize: [14, 14],
                    iconAnchor: [7, 7]
                }),
                interactive: false
            }).addTo(this.routeLayer);
        });

        // START marker
        L.marker(coordinates[0], {
            icon: L.divIcon({
                className: 'route-marker-container',
                html: `<div class="route-marker route-marker--start">▶</div>
                       <div class="route-marker__label route-marker__label--start">${startName}</div>`,
                iconSize: [28, 52],
                iconAnchor: [14, 14]
            })
        }).bindPopup(`<b style="color:#10b981;">🟢 START</b><br>${startName}`)
          .addTo(this.markerLayer);

        // END marker
        L.marker(coordinates[coordinates.length - 1], {
            icon: L.divIcon({
                className: 'route-marker-container',
                html: `<div class="route-marker route-marker--end">⚑</div>
                       <div class="route-marker__label route-marker__label--end">${endName}</div>`,
                iconSize: [28, 52],
                iconAnchor: [14, 14]
            })
        }).bindPopup(`<b style="color:#ef4444;">🔴 END</b><br>${endName}`)
          .addTo(this.markerLayer);
    },

    // ── Helpers ───────────────────────────────────────────────────────────
    clearRoutes() {
        if (this.routeLayer)  this.routeLayer.clearLayers();
        if (this.markerLayer) this.markerLayer.clearLayers();
    },

    setView(lat, lng, zoom = 15) {
        if (this.map) this.map.setView([lat, lng], zoom, { animate: true });
    },

    fitToRoute(coordinates) {
        if (!coordinates || coordinates.length < 2) return;
        this.map.fitBounds(L.latLngBounds(coordinates), {
            padding: [60, 40],
            maxZoom: 16,
            animate: true
        });
    },

    resetToUOW() {
        if (this.map) this.map.setView(this.UOW_CENTER, 14, { animate: true });
    },

    invalidateSize() {
        if (this.map) setTimeout(() => this.map.invalidateSize(), 100);
    }
};
