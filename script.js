document.addEventListener("DOMContentLoaded", function () {
    console.log("SmartStop VIT Loaded");

    let favorites = JSON.parse(localStorage.getItem('favorites') || '[]');

    fetchBusData(); // Immediate bus data load on page load
    updateFavoritesList();
    setupEventListeners();

    // --- DARK MODE TOGGLE ---
    const darkBtn = document.getElementById('darkModeSwitch');
    if (darkBtn) {
        darkBtn.addEventListener('click', function () {
            document.body.classList.toggle('dark-mode');
            darkBtn.innerHTML = document.body.classList.contains('dark-mode')
                ? '<i class="fas fa-sun"></i> Light Mode'
                : '<i class="fas fa-moon"></i> Dark Mode';
        });
    }

    // --- AUTO LISTING (DEMO + BACKEND fallback) ---
    function loadAutos() {
        // Try backend API, if not available, fallback to demo
        fetch('/api/autos')
            .then(response => response.json())
            .then(data => {
                showAutoList(data.autos);
            })
            .catch(() => {
                // Fallback DEMO: 5 autos
                showAutoList([
                    { id: "A101", location: "Near Main Gate", phone: "9876543210" },
                    { id: "A102", location: "Near SJT", phone: "9876543222" },
                    { id: "A103", location: "Near PRP", phone: "9876543223" },
                    { id: "A104", location: "Near Q Block", phone: "9876543224" },
                    { id: "A105", location: "Near K Block", phone: "9876543225" }
                ]);
            });
    }
    function showAutoList(autos) {
        const autoList = document.getElementById('autoList');
        if (!autoList) return;
        if (!autos || autos.length === 0) {
            autoList.innerHTML = "<p>No autos available right now.</p>";
            return;
        }
        let html = "";
        autos.forEach(auto => {
            html += `<div class="auto-card">
                <div>
                <b>Auto #${auto.id}</b><br>
                ${auto.location}<br>
                Phone: ${auto.phone}
                </div>
                <button class="auto-book-btn" data-auto-id="${auto.id}">Book</button>
            </div>`;
        });
        autoList.innerHTML = html;
        document.querySelectorAll('.auto-book-btn').forEach(btn => {
            btn.onclick = function () {
                document.getElementById("autoModal").style.display = "flex";
                document.getElementById("autoModalDetails").innerHTML =
                    "Booking Auto <b>" + this.dataset.autoId + "</b>.<br>Fill details below.";
                document.getElementById("autoIdField").value = this.dataset.autoId;
                document.getElementById("autoBookingForm").style.display = "";
            };
        });
    }
    loadAutos();

    // --- EVENT LISTENERS ---
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

        delegateBusRowClick();

        const mapOptions = document.querySelectorAll(".map-options input");
        mapOptions.forEach(option => {
            option.addEventListener("change", updateMapDisplay);
        });

        // --- Auto Booking Modal ---
        const closeAutoModalBtn = document.getElementById("closeAutoModalBtn");
        if (closeAutoModalBtn) {
            closeAutoModalBtn.onclick = function () {
                document.getElementById("autoModal").style.display = "none";
                document.getElementById("autoBookingForm").style.display = "";
            };
        }

        const autoBookingForm = document.getElementById("autoBookingForm");
        if (autoBookingForm) {
            autoBookingForm.onsubmit = function (e) {
                e.preventDefault();
                const formData = new FormData(this);
                fetch('/api/book_auto', { method: 'POST', body: formData })
                    .then(res => res.json())
                    .then(data => {
                        document.getElementById("autoModalDetails").innerHTML =
                            data.status === "success"
                                ? "<b>" + data.message + "</b><br><button onclick='document.getElementById(\"autoModal\").style.display=\"none\";'>Close</button>"
                                : "<span style='color:red'>" + data.message + "</span>";
                        this.style.display = "none";
                    }).catch(() => {
                        // DEMO fallback on error
                        document.getElementById("autoModalDetails").innerHTML =
                            "<b>Auto booked (demo mode).</b><br><button onclick='document.getElementById(\"autoModal\").style.display=\"none\";'>Close</button>";
                        this.style.display = "none";
                    });
            };
        }
    }

    function delegateBusRowClick() {
        const busRows = document.querySelectorAll(".bus-row");
        busRows.forEach(row => {
            row.addEventListener("click", function (e) {
                if (e.target.classList.contains("qr-code")) return;
                showBusDetails(this.getAttribute("data-bus-id"));
            });
        });
    }

    // --- BUS & TABLE LOGIC ---
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
            .then(routesData => {
                buildBusTable(buses, routesData);
                delegateBusRowClick();
            })
            .catch(() => {
                buildBusTable(buses, {});
                delegateBusRowClick();
            });
    }

    function buildBusTable(buses, routes) {
        // Hostels/route improvements can be added here as before, if relevant for your board.
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
            const occColor = occPercent < 50 ? 'green' : occPercent < 80 ? 'orange' : 'red';
            tableHTML += `
                <tr class="bus-row" data-bus-id="${busId}" data-route="${info.route_id}" data-occupancy="${occPercent}">
                    <td>${busId}</td>
                    <td>${routeInfo.start} → ${routeInfo.end}</td>
                    <td>${info.eta}</td>
                    <td>
                        <div class="occupancy-bar">
                            <div class="occupancy-fill" style="width: ${occPercent}%; background-color: ${occColor};"></div>
                        </div>
                        <span class="occupancy-text">${info.occupancy}/${info.capacity}</span>
                    </td>
                    <td class="${info.on_time ? 'status-ok' : 'status-delay'}">${info.status}</td>
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
        tableHTML += "</tbody></table>";
        busTableContainer.innerHTML = tableHTML;
    }

    function updateLastUpdatedTime(timestamp) {
        const lastUpdateTimeElement = document.getElementById("lastUpdateTime");
        if (lastUpdateTimeElement && timestamp) {
            const date = new Date(timestamp.replace(" ", "T"));
            lastUpdateTimeElement.textContent = date.toLocaleTimeString();
        }
    }

    // --- SEARCH & FILTER ---
    function performSearch() {
        const query = document.getElementById("searchInput").value.trim().toLowerCase();
        const busRows = document.querySelectorAll(".bus-row");
        busRows.forEach(row => {
            const text = row.textContent.toLowerCase();
            row.style.display = text.includes(query) ? "" : "none";
        });
    }

    function applyFilter(filter) {
        const busRows = document.querySelectorAll(".bus-row");
        busRows.forEach(row => {
            const occ = parseFloat(row.getAttribute("data-occupancy"));
            const statusOk = row.querySelector("td:nth-child(5)").classList.contains("status-ok");
            switch (filter) {
                case "all": row.style.display = ""; break;
                case "available": row.style.display = occ < 90 ? "" : "none"; break;
                case "ontime": row.style.display = statusOk ? "" : "none"; break;
                case "crowded": row.style.display = occ >= 70 ? "" : "none"; break;
            }
        });
    }

    // FAVORITES and the rest remain unchanged...
    function toggleFavorite(routeId) {
        const index = favorites.indexOf(routeId);
        if (index === -1) favorites.push(routeId);
        else favorites.splice(index, 1);
        localStorage.setItem("favorites", JSON.stringify(favorites));
    }

    function updateFavoritesList() {
        const favoritesList = document.getElementById("favorites-list");
        if (!favoritesList) return;
        if (favorites.length === 0) {
            favoritesList.innerHTML = "<p class='no-favorites'>No favorites added yet.</p>";
            return;
        }
        let html = "";
        favorites.forEach(routeId => {
            const card = document.querySelector(`.route-card[data-route-id="${routeId}"]`);
            if (!card) return;
            const routeTitle = card.querySelector(".route-header h3").textContent;
            html += `<div class="favorite-item"><h3>${routeTitle}</h3></div>`;
        });
        favoritesList.innerHTML = html;
    }

    // ----- FEEDBACK MODAL -----
    function submitFeedback() {
        const form = document.getElementById("feedbackForm");
        if (!form) return;
        const formData = new FormData(form);
        fetch("/feedback", { method: "POST", body: formData })
            .then(res => res.json())
            .then(data => {
                alert(data.status === "success" ? "Thanks for your feedback!" : data.message);
                if (data.status === "success") form.reset();
            })
            .catch(() => alert("Error submitting feedback."));
    }

    // -------------------- MAP DISPLAY --------------------
    function updateMapDisplay() {
        const mapFrame = document.getElementById("mapFrame");
        if (!mapFrame || !mapFrame.contentWindow) return;
        mapFrame.contentWindow.postMessage({
            action: "updateLayers",
            layers: {
                buildings: document.getElementById("showBuildings").checked,
                hostels: document.getElementById("showHostels").checked,
                routes: document.getElementById("showRoutes").checked
            }
        }, "*");
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

    window.closeBusDetailModal = function () {
        const modal = document.getElementById("busDetailModal");
        if (modal) modal.style.display = "none";
    };

    window.showBusDetails = function (busId) {
        fetch(`/api/bus/${busId}`)
            .then(res => res.json())
            .then(data => {
                const modal = document.getElementById("busDetailModal");
                const content = document.getElementById("busDetailsContent");
                if (modal && content && data.status === "success") {
                    const info = data.data;
                    content.innerHTML = `
                        <h2>Bus: ${info.bus_id}</h2>
                        <p><strong>Route:</strong> ${info.route_id} → ${info.destination}</p>
                        <p><strong>ETA:</strong> ${info.eta}</p>
                        <p><strong>Occupancy:</strong> ${info.occupancy}/${info.capacity}</p>
                        <p><strong>Status:</strong> ${info.status}</p>
                        <button onclick="closeBusDetailModal()">Close</button>
                    `;
                    modal.style.display = "flex";
                }
            });
    };

    window.onclick = function (event) {
        const qrModal = document.getElementById("qrModal");
        const busDetailModal = document.getElementById("busDetailModal");
        const autoModal = document.getElementById("autoModal");
        if (event.target === qrModal) qrModal.style.display = "none";
        if (event.target === busDetailModal) busDetailModal.style.display = "none";
        if (event.target === autoModal) {
            autoModal.style.display = "none";
            document.getElementById("autoBookingForm").style.display = "";
        }
    };
});
