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

        // OpenStreetMap France (Humanitarian) tiles — completely free,
        // no API key, no IP restrictions, works on both local and Render.
        // Uses a different subdomain from the main OSM servers that blocked us.
        L.tileLayer('https://{s}.tile.openstreetmap.fr/osmfr/{z}/{x}/{y}.png', {
            attribution: '&copy; OpenStreetMap France | &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
            subdomains: 'abc',
            maxZoom: 20
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
    },

    // ════════════════════════════════════════════════════════════════════
    // LIVE NAVIGATION
    // ════════════════════════════════════════════════════════════════════

    // Internal navigation state
    _navActive:        false,
    _navCoordinates:   [],   // full route waypoints [[lat,lng], ...]
    _navNextIndex:     0,    // index of the next unwalked waypoint
    _navRemainingLayer: null, // Leaflet layer for the remaining path
    _navUserNavMarker:  null, // large navigation dot

    /**
     * Start navigation mode.
     * @param {Array} coordinates - full route [[lat,lng], ...]
     */
    startNavigation(coordinates) {
        if (!coordinates || coordinates.length < 2) return;

        this._navActive       = true;
        this._navCoordinates  = coordinates;
        this._navNextIndex    = 0;

        // Create a separate layer for the remaining path
        if (this._navRemainingLayer) {
            this.map.removeLayer(this._navRemainingLayer);
        }
        this._navRemainingLayer = L.layerGroup().addTo(this.map);

        // Draw the full remaining path initially
        this._drawRemainingPath(0);

        // Hide the original static route so only the live remaining path shows
        if (this.routeLayer) this.routeLayer.clearLayers();
    },

    /**
     * Called on every GPS update during navigation.
     * Moves the user dot, pans the map, trims the walked portion.
     * @param {number} lat
     * @param {number} lng
     * @returns {object} { remainingMetres, arrived }
     */
    updateNavigation(lat, lng) {
        if (!this._navActive) return { remainingMetres: 0, arrived: false };

        // Move / create the navigation user marker
        this._updateNavMarker(lat, lng);

        // Pan map to keep user centred
        this.map.setView([lat, lng], 17, { animate: true });

        // Find the nearest waypoint ahead and advance _navNextIndex
        this._navNextIndex = this._findNextWaypoint(lat, lng, this._navNextIndex);

        // Redraw only the remaining path from that waypoint onward
        this._drawRemainingPath(this._navNextIndex);

        // Calculate remaining distance
        const remainingMetres = this._calcRemainingDistance(lat, lng, this._navNextIndex);

        // Arrival check: within 30 metres of the final waypoint
        const endPoint = this._navCoordinates[this._navCoordinates.length - 1];
        const distToEnd = this._haversineMetres(lat, lng, endPoint[0], endPoint[1]);
        const arrived = distToEnd < 30;

        return { remainingMetres: Math.round(remainingMetres), arrived };
    },

    /**
     * Stop navigation — clean up all navigation layers and state.
     */
    stopNavigation() {
        this._navActive = false;

        if (this._navRemainingLayer) {
            this.map.removeLayer(this._navRemainingLayer);
            this._navRemainingLayer = null;
        }
        if (this._navUserNavMarker) {
            this.map.removeLayer(this._navUserNavMarker);
            this._navUserNavMarker = null;
        }

        this._navCoordinates = [];
        this._navNextIndex   = 0;
    },

    // ── Private navigation helpers ────────────────────────────────────────

    _updateNavMarker(lat, lng) {
        const navIcon = L.divIcon({
            className: '',
            html: '<div class="nav-user-dot"><div class="nav-user-dot__pulse"></div></div>',
            iconSize: [22, 22],
            iconAnchor: [11, 11]
        });
        if (this._navUserNavMarker) {
            this._navUserNavMarker.setLatLng([lat, lng]);
        } else {
            this._navUserNavMarker = L.marker([lat, lng], { icon: navIcon, zIndexOffset: 1000 })
                .addTo(this.map);
        }
    },

    _drawRemainingPath(fromIndex) {
        if (!this._navRemainingLayer) return;
        this._navRemainingLayer.clearLayers();

        const remaining = this._navCoordinates.slice(fromIndex);
        if (remaining.length < 2) return;

        // Remaining path — bright teal so it's clearly visible
        L.polyline(remaining, {
            color: '#1abc9c',
            weight: 6,
            opacity: 0.95,
            lineCap: 'round',
            lineJoin: 'round'
        }).addTo(this._navRemainingLayer);

        // End marker stays visible
        const endPoint = this._navCoordinates[this._navCoordinates.length - 1];
        L.marker(endPoint, {
            icon: L.divIcon({
                className: 'route-marker-container',
                html: '<div class="route-marker route-marker--end">⚑</div>',
                iconSize: [28, 28],
                iconAnchor: [14, 14]
            })
        }).addTo(this._navRemainingLayer);
    },

    /**
     * Find the index of the nearest waypoint that is ahead of the user.
     * Searches forward from currentIndex to avoid jumping backwards.
     */
    _findNextWaypoint(userLat, userLng, currentIndex) {
        const coords = this._navCoordinates;
        const searchAhead = Math.min(currentIndex + 20, coords.length - 1);
        let bestIndex = currentIndex;
        let bestDist  = Infinity;

        for (let i = currentIndex; i <= searchAhead; i++) {
            const d = this._haversineMetres(userLat, userLng, coords[i][0], coords[i][1]);
            if (d < bestDist) {
                bestDist  = d;
                bestIndex = i;
            }
        }
        // Only advance, never go back
        return Math.max(currentIndex, bestIndex);
    },

    /**
     * Sum of straight-line segments from user position to the end.
     */
    _calcRemainingDistance(userLat, userLng, fromIndex) {
        const coords = this._navCoordinates;
        if (fromIndex >= coords.length - 1) return 0;

        // Distance from user to the next waypoint
        let total = this._haversineMetres(userLat, userLng, coords[fromIndex][0], coords[fromIndex][1]);

        // Sum subsequent waypoint-to-waypoint distances
        for (let i = fromIndex; i < coords.length - 1; i++) {
            total += this._haversineMetres(coords[i][0], coords[i][1], coords[i + 1][0], coords[i + 1][1]);
        }
        return total;
    },

    /**
     * Haversine distance in metres between two lat/lng points.
     */
    _haversineMetres(lat1, lng1, lat2, lng2) {
        const R  = 6371000; // Earth radius in metres
        const φ1 = lat1 * Math.PI / 180;
        const φ2 = lat2 * Math.PI / 180;
        const Δφ = (lat2 - lat1) * Math.PI / 180;
        const Δλ = (lng2 - lng1) * Math.PI / 180;
        const a  = Math.sin(Δφ / 2) ** 2 + Math.cos(φ1) * Math.cos(φ2) * Math.sin(Δλ / 2) ** 2;
        return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    }
};
