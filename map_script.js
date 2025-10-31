document.addEventListener("DOMContentLoaded", function () {
    console.log("SmartStop VIT Loaded");

    const isAnalyticsPage = window.location.pathname.includes("analytics");
    if (isAnalyticsPage) {
        initAnalyticsPage();
    } else {
        initMainTracker();
    }

    // =====================================================================
    // 🔹 MAIN DASHBOARD (index.html)
    // =====================================================================
    function initMainTracker() {
        let favorites = JSON.parse(localStorage.getItem("favorites") || "[]");
        let refreshInterval = null;

        startAutoRefresh();
        updateFavoritesList();
        setupEventListeners();

        // -------------------- EVENT LISTENERS --------------------
        function setupEventListeners() {
            const refreshButton = document.getElementById("refreshButton");
            if (refreshButton) refreshButton.addEventListener("click", fetchBusData);

            const searchButton = document.getElementById("searchButton");
            const searchInput = document.getElementById("searchInput");
            if (searchButton && searchInput) {
                searchButton.addEventListener("click", performSearch);
                searchInput.addEventListener("keypress", (e) => {
                    if (e.key === "Enter") performSearch();
                });
            }

            const filterButtons = document.querySelectorAll(".filter-btn");
            filterButtons.forEach(button => {
                button.addEventListener("click", function () {
                    filterButtons.forEach(btn => btn.classList.remove("active"));
                    this.classList.add("active");
                    applyFilter(this.dataset.filter);
                });
            });

            const feedbackForm = document.getElementById("feedbackForm");
            if (feedbackForm) {
                feedbackForm.addEventListener("submit", function (e) {
                    e.preventDefault();
                    submitFeedback();
                });
            }

            const mapOptions = document.querySelectorAll(".map-options input");
            mapOptions.forEach(option => {
                option.addEventListener("change", updateMapDisplay);
            });
        }

        // -------------------- AUTO REFRESH --------------------
        function startAutoRefresh() {
            if (refreshInterval) clearInterval(refreshInterval);
            refreshInterval = setInterval(fetchBusData, 30000);
        }

        // -------------------- FETCH BUS DATA --------------------
        function fetchBusData() {
            const refreshButton = document.getElementById("refreshButton");
            if (refreshButton) refreshButton.classList.add("rotating");

            fetch("/api/buses")
                .then(response => response.json())
                .then(data => {
                    updateBusTable(data);
                    updateLastUpdatedTime(data.last_updated);
                    if (refreshButton) refreshButton.classList.remove("rotating");
                })
                .catch(error => {
                    console.error("Error fetching bus data:", error);
                    if (refreshButton) refreshButton.classList.remove("rotating");
                });
        }

        // -------------------- UPDATE BUS TABLE --------------------
        function updateBusTable(data) {
            const busTableContainer = document.getElementById("busTableContainer");
            if (!busTableContainer) return;

            const buses = data.buses || {};
            if (Object.keys(buses).length === 0) {
                busTableContainer.innerHTML = '<p class="no-data">No bus data available yet. Scan a QR code to start tracking!</p>';
                return;
            }

            fetch("/api/routes")
                .then(response => response.json())
                .then(routesData => buildBusTable(buses, routesData))
                .catch(() => buildBusTable(buses, {}));
        }

        // -------------------- BUILD TABLE --------------------
        function buildBusTable(buses, routes) {
            const busTableContainer = document.getElementById("busTableContainer");
            let tableHTML = `
                <table id="busTable">
                    <thead>
                        <tr>
                            <th>Bus ID</th>
                            <th>Route</th>
                            <th>ETA</th>
                            <th>Occupancy</th>
                            <th>Status</th>
                            <th>QR Code</th>
                        </tr>
                    </thead>
                    <tbody>
            `;

            for (const [busId, info] of Object.entries(buses)) {
                const routeInfo = routes[info.route_id] || { start: "Unknown", end: "Unknown" };
                const occPercent = info.capacity ? (info.occupancy / info.capacity) * 100 : 0;
                const occColor = occPercent < 50 ? "green" : occPercent < 80 ? "orange" : "red";

                tableHTML += `
                    <tr class="bus-row" data-bus-id="${busId}">
                        <td>${busId}</td>
                        <td>${routeInfo.start} → ${routeInfo.end}</td>
                        <td>${info.eta}</td>
                        <td>
                            <div class="occupancy-bar">
                                <div class="occupancy-fill" style="width:${occPercent}%; background:${occColor};"></div>
                            </div>
                            <span class="occupancy-text">${info.occupancy}/${info.capacity}</span>
                        </td>
                        <td class="${info.on_time ? "status-ok" : "status-delay"}">${info.status}</td>
                        <td>
                            <img src="/static/qr_codes/${busId}.png" 
                                 alt="QR ${busId}" 
                                 class="qr-code" 
                                 width="40" height="40" 
                                 onclick="enlargeQR('${busId}')"
                                 onerror="this.style.display='none'">
                        </td>
                    </tr>
                `;
            }

            busTableContainer.innerHTML = tableHTML + "</tbody></table>";
        }

        // -------------------- SEARCH & FILTER --------------------
        function performSearch() {
            const query = document.getElementById("searchInput").value.trim().toLowerCase();
            document.querySelectorAll(".bus-row").forEach(row => {
                row.style.display = row.textContent.toLowerCase().includes(query) ? "" : "none";
            });
        }

        function applyFilter(filter) {
            const busRows = document.querySelectorAll(".bus-row");
            busRows.forEach(row => {
                const occ = parseFloat(row.querySelector(".occupancy-fill").style.width);
                const isOnTime = row.querySelector(".status-ok");
                switch (filter) {
                    case "all": row.style.display = ""; break;
                    case "available": row.style.display = occ < 90 ? "" : "none"; break;
                    case "ontime": row.style.display = isOnTime ? "" : "none"; break;
                    case "crowded": row.style.display = occ >= 70 ? "" : "none"; break;
                }
            });
        }

        // -------------------- MAP DISPLAY --------------------
        function updateMapDisplay() {
            const mapFrame = document.getElementById("mapFrame");
            if (mapFrame && mapFrame.contentWindow) {
                mapFrame.contentWindow.postMessage({
                    action: "updateLayers",
                    layers: {
                        buildings: document.getElementById("showBuildings").checked,
                        hostels: document.getElementById("showHostels").checked,
                        routes: document.getElementById("showRoutes").checked,
                    },
                }, "*");
            }
        }

        // -------------------- MODALS --------------------
        window.enlargeQR = function (busId) {
            const modal = document.getElementById("qrModal");
            const enlargedQR = document.getElementById("enlargedQR");
            if (modal && enlargedQR) {
                enlargedQR.src = `/static/qr_codes/${busId}.png`;
                modal.style.display = "flex";
            }
        };

        window.closeModal = function () {
            const modal = document.getElementById("qrModal");
            if (modal) modal.style.display = "none";
        };

        window.onclick = function (event) {
            const qrModal = document.getElementById("qrModal");
            if (event.target === qrModal) qrModal.style.display = "none";
        };
    }

    // =====================================================================
    // 📊 ANALYTICS DASHBOARD (analytics.html)
    // =====================================================================
    function initAnalyticsPage() {
        console.log("Analytics Dashboard Active");
        fetchAnalyticsData();
        setInterval(fetchAnalyticsData, 60000);

        function fetchAnalyticsData() {
            Promise.all([
                fetch("/api/analytics/utilization").then(res => res.json()),
                fetch("/api/analytics/routes").then(res => res.json()),
                fetch("/api/analytics/feedback").then(res => res.json())
            ])
                .then(([util, routes, feedback]) => {
                    renderUtilization(util);
                    renderRoutePerformance(routes);
                    renderFeedback(feedback);
                })
                .catch(err => console.error("Analytics load error:", err));
        }

        function renderUtilization(data) {
            const ctx = document.getElementById("utilizationChart");
            if (!ctx) return;

            new Chart(ctx, {
                type: "bar",
                data: {
                    labels: ["Average Occupancy (%)"],
                    datasets: [{
                        label: "Occupancy Rate",
                        data: [data.average_occupancy || 0],
                        backgroundColor: "#0066FF"
                    }]
                },
                options: { responsive: true, scales: { y: { beginAtZero: true, max: 100 } } }
            });

            document.getElementById("busiestBus").textContent = data.busiest_bus || "N/A";
            document.getElementById("peakTime").textContent = data.peak_time || "N/A";
        }

        function renderRoutePerformance(data) {
            const ctx = document.getElementById("routePerformanceChart");
            if (!ctx) return;

            const labels = Object.keys(data.routes || {});
            const durations = Object.values(data.routes || {});
            new Chart(ctx, {
                type: "line",
                data: {
                    labels,
                    datasets: [{
                        label: "Average Duration (min)",
                        data: durations,
                        borderColor: "#FF69B4",
                        fill: false,
                        tension: 0.4
                    }]
                },
                options: { responsive: true }
            });

            document.getElementById("fastestRoute").textContent = data.fastest_route || "N/A";
            document.getElementById("slowestRoute").textContent = data.slowest_route || "N/A";
        }

        function renderFeedback(data) {
            const ctx = document.getElementById("feedbackChart");
            if (!ctx) return;

            const labels = Object.keys(data.bus_ratings || {});
            const ratings = Object.values(data.bus_ratings || {});
            new Chart(ctx, {
                type: "doughnut",
                data: {
                    labels,
                    datasets: [{
                        data: ratings,
                        backgroundColor: ["#0066FF", "#FF69B4", "#2ecc71", "#f39c12", "#e74c3c"]
                    }]
                },
                options: { responsive: true }
            });

            document.getElementById("totalFeedback").textContent = data.total_feedback || 0;
            document.getElementById("avgRating").textContent = data.average_rating || "N/A";
        }
    }
});
