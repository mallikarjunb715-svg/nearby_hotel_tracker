// Interactive Map Initializer for OpenStreetMap
function initFoodMap(userLat, userLng) {
    const map = L.map('map').setView([userLat, userLng], 13);

    // Load OpenStreetMap tiles
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);

    // Customer Location Marker
    L.marker([userLat, userLng]).addTo(map)
        .bindPopup('<b>Your Current Location</b>').openPopup();

    // Fetch Nearby Hotels via REST API
    fetch(`/api/nearby-hotels?lat=${userLat}&lng=${userLng}&radius=10`)
        .then(response => response.json())
        .then(data => {
            data.forEach(hotel => {
                const marker = L.marker([hotel.latitude, hotel.longitude]).addTo(map);
                marker.bindPopup(`
                    <div class="p-1">
                        <h6 class="fw-bold mb-1">${hotel.name}</h6>
                        <p class="small mb-1">${hotel.address}</p>
                        <span class="badge bg-danger">${hotel.distance} km away</span>
                        <a href="/hotel/${hotel.id}" class="btn btn-sm btn-primary mt-2 text-white d-block">View Hotel</a>
                    </div>
                `);
            });
        })
        .catch(err => console.error('Error fetching map markers:', err));
}