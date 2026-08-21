/**
 * AI FOOD PREP SYSTEM - FRONTEND DASHBOARD LOGIC
 * Integrated with Flask + SQLite + Random Forest Regression Backend
 */

// Relative API base URL (works seamlessly when served by Flask or Live Server)
const API_BASE_URL = window.location.protocol === 'file:' ? 'http://127.0.0.1:5000/api' : '/api';

// Google Form Link (Exact published reviewer URL)
const GOOGLE_FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLScVxIq9EXUaPDyEdDQpfR5pVjTLw1XFhqzwmDPebxRvn4ON8g/viewform?usp=publish-editor";

// Centralized Application State
const AppState = {
    selectedDate: "2026-02-02",
    dayOfWeek: "Monday",
    attendance: 642,
    currentMenuItems: [],
    lastPrediction: null,
    hasUnreadNotification: false,
    settings: {
        darkMode: false,
        fontSize: "normal",
        appearance: "paper",
        notificationsEnabled: true,
        animationsEnabled: true
    }
};

// ============================================================
// INITIALIZATION
// ============================================================
document.addEventListener("DOMContentLoaded", () => {
    initApp();
});

function initApp() {
    console.log("Initializing AI Food Prep System Frontend...");
    
    // Set initial date picker value (default: 2026-02-02)
    const dateInput = document.getElementById("datePicker");
    if (dateInput) {
        dateInput.value = AppState.selectedDate;
        updateDay(AppState.selectedDate);
        dateInput.addEventListener("change", (e) => {
            AppState.selectedDate = e.target.value;
            updateDay(e.target.value);
            loadAttendance();
        });
    }

    // Fetch initial biometric attendance from backend
    loadAttendance();

    // Bind Core UI Event Listeners
    setupEventListeners();
}

// ============================================================
// DATE & ATTENDANCE BACKEND INTEGRATION
// ============================================================

function updateDay(dateString) {
    if (!dateString) return;
    const dateObj = new Date(dateString + "T00:00:00");
    const dayNames = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
    const calculatedDay = dayNames[dateObj.getDay()];
    
    AppState.dayOfWeek = calculatedDay;
    const dayDisplayEl = document.getElementById("dayDisplay");
    if (dayDisplayEl) {
        dayDisplayEl.textContent = calculatedDay;
    }
}

async function loadAttendance() {
    const countEl = document.getElementById("attendanceCount");
    if (!countEl) return;

    try {
        const response = await fetch(`${API_BASE_URL}/attendance?date=${AppState.selectedDate}`);
        if (response.ok) {
            const data = await response.json();
            AppState.attendance = data.present;
            countEl.textContent = data.present;
            console.log(`[BACKEND API] Loaded attendance for ${AppState.selectedDate}: ${data.present} present`);
        } else {
            throw new Error(`API error HTTP ${response.status}`);
        }
    } catch (err) {
        console.warn("[BACKEND API] Backend server offline. Using fallback attendance data.", err);
        AppState.attendance = 642;
        countEl.textContent = "642";
    }
}

// ============================================================
// EVENT LISTENERS SETUP
// ============================================================

function setupEventListeners() {
    // Vessel Click (Open Menu Entry Modal)
    const vesselBtn = document.getElementById("vesselContainer");
    if (vesselBtn) {
        vesselBtn.addEventListener("click", openVesselModal);
        vesselBtn.addEventListener("keydown", (e) => {
            if (e.key === "Enter" || e.key === " ") openVesselModal();
        });
    }

    // Vessel Modal Actions
    document.getElementById("closeVesselModal")?.addEventListener("click", closeVesselModal);
    document.getElementById("btnAddRow")?.addEventListener("click", () => addItemRow());
    document.getElementById("btnSubmitMenu")?.addEventListener("click", handleMenuSubmit);

    // Sidebar Navigation Buttons
    document.getElementById("btnFeedback")?.addEventListener("click", openFeedbackModal);
    document.getElementById("btnHistory")?.addEventListener("click", openHistoryModal);
    document.getElementById("btnCookinCheck")?.addEventListener("click", openCookinCheckModal);
    document.getElementById("btnHelp")?.addEventListener("click", openHelpModal);
    document.getElementById("btnSettings")?.addEventListener("click", openSettingsModal);

    // Modal Close Buttons
    document.getElementById("closeFeedbackModal")?.addEventListener("click", closeFeedbackModal);
    document.getElementById("closeHistoryModal")?.addEventListener("click", closeHistoryModal);
    document.getElementById("closeCookinCheckModal")?.addEventListener("click", closeCookinCheckModal);
    document.getElementById("closeHelpModal")?.addEventListener("click", closeHelpModal);
    document.getElementById("closeSettingsModal")?.addEventListener("click", closeSettingsModal);

    // Google Form Link Button
    document.getElementById("btnOpenGForm")?.addEventListener("click", () => {
        window.open(GOOGLE_FORM_URL, "_blank");
    });

    // Notification Dropdown Toggle & Close
    const notifBtn = document.getElementById("notifBtn");
    const notifDropdown = document.getElementById("notifDropdown");
    const notifCloseBtn = document.getElementById("notifCloseBtn");

    if (notifBtn) {
        notifBtn.addEventListener("click", (e) => {
            e.stopPropagation();
            toggleNotificationDropdown();
        });
    }

    if (notifCloseBtn) {
        notifCloseBtn.addEventListener("click", () => {
            notifDropdown?.classList.add("hidden");
        });
    }

    document.addEventListener("click", (e) => {
        if (!notifDropdown?.contains(e.target) && !notifBtn?.contains(e.target)) {
            notifDropdown?.classList.add("hidden");
        }
    });

    // Settings Functional Controls
    document.getElementById("toggleDarkMode")?.addEventListener("change", (e) => {
        toggleDarkMode(e.target.checked);
    });

    document.getElementById("fontSizeSelect")?.addEventListener("change", (e) => {
        updateFontSize(e.target.value);
    });

    document.getElementById("appearanceSelect")?.addEventListener("change", (e) => {
        updateAppearance(e.target.value);
    });

    document.getElementById("toggleAnimations")?.addEventListener("change", (e) => {
        toggleAnimations(e.target.checked);
    });
}

// ============================================================
// COOKING VESSEL & MENU MODAL FLOW
// ============================================================

function openVesselModal() {
    const modal = document.getElementById("vesselModal");
    const itemsList = document.getElementById("menuItemsList");
    
    if (modal && itemsList) {
        itemsList.innerHTML = "";
        
        if (AppState.currentMenuItems.length > 0) {
            AppState.currentMenuItems.forEach(item => addItemRow(item.name, item.quantity));
        } else {
            addItemRow("Dosa", 200);
            addItemRow("Idli", 400);
            addItemRow("Rice", 150);
        }

        modal.classList.remove("hidden");
    }
}

function closeVesselModal() {
    document.getElementById("vesselModal")?.classList.add("hidden");
}

function addItemRow(name = "", qty = "") {
    const listContainer = document.getElementById("menuItemsList");
    if (!listContainer) return;

    const rowDiv = document.createElement("div");
    rowDiv.className = "menu-item-row";

    rowDiv.innerHTML = `
        <input type="text" class="input-field item-name-input" placeholder="Item Name (e.g., Dosa)" value="${name}">
        <input type="number" class="input-field item-qty-input" placeholder="Qty" min="1" value="${qty}">
        <button type="button" class="btn-remove-row" title="Remove Item">&times;</button>
    `;

    rowDiv.querySelector(".btn-remove-row")?.addEventListener("click", () => {
        rowDiv.remove();
    });

    listContainer.appendChild(rowDiv);
}

function validateItems() {
    const rows = document.querySelectorAll(".menu-item-row");
    const items = [];

    rows.forEach(row => {
        const nameInput = row.querySelector(".item-name-input");
        const qtyInput = row.querySelector(".item-qty-input");

        const name = nameInput ? nameInput.value.trim() : "";
        const qty = qtyInput ? parseInt(qtyInput.value.trim(), 10) : 0;

        if (name !== "" && !isNaN(qty) && qty > 0) {
            items.push({ name, quantity: qty });
        }
    });

    return items;
}

function handleMenuSubmit() {
    const items = validateItems();

    if (items.length === 0) {
        alert("Please add at least one food item.");
        return;
    }

    AppState.currentMenuItems = items;
    closeVesselModal();

    // Trigger AI Analysis Flow
    runAIAnalysis();
}

// ============================================================
// AI ANALYSIS & PREDICTION FLOW
// ============================================================

async function runAIAnalysis() {
    const overlay = document.getElementById("aiOverlay");
    const submitBtn = document.getElementById("btnSubmitMenu");

    if (overlay) overlay.classList.remove("hidden");
    if (submitBtn) submitBtn.disabled = true;

    const payload = {
        date: AppState.selectedDate,
        day: AppState.dayOfWeek,
        attendance: AppState.attendance,
        items: AppState.currentMenuItems
    };

    try {
        console.log("[BACKEND API] Sending prediction request:", payload);
        const response = await fetch(`${API_BASE_URL}/predict`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            throw new Error(`Server returned HTTP ${response.status}`);
        }

        const prediction = await response.json();
        console.log("[BACKEND API] Received prediction response:", prediction);

        AppState.lastPrediction = prediction;
        activateStove(prediction);
        updateNotification(prediction);

    } catch (err) {
        console.warn("[BACKEND API] Server offline. Running fallback estimation.", err);
        
        const fallbackResults = AppState.currentMenuItems.map(i => ({
            item: i.name,
            predicted_quantity: Math.round(i.quantity * (AppState.attendance / 600.0))
        }));
        const total = fallbackResults.reduce((sum, r) => sum + r.predicted_quantity, 0);

        const fallbackPrediction = {
            date: AppState.selectedDate,
            day: AppState.dayOfWeek,
            attendance: AppState.attendance,
            results: fallbackResults,
            total: total
        };

        AppState.lastPrediction = fallbackPrediction;
        activateStove(fallbackPrediction);
        updateNotification(fallbackPrediction);
    } finally {
        if (overlay) overlay.classList.add("hidden");
        if (submitBtn) submitBtn.disabled = false;
    }
}

function activateStove(prediction) {
    if (AppState.settings.animationsEnabled) {
        document.getElementById("stoveFlames")?.classList.remove("hidden");
    }

    document.getElementById("stoveKnob")?.classList.add("active");
    document.getElementById("stoveIndicator")?.classList.add("active");

    renderStoveOutput(prediction);
}

function renderStoveOutput(prediction) {
    const idleScreen = document.getElementById("stoveIdle");
    const activeScreen = document.getElementById("stoveActive");

    if (idleScreen && activeScreen) {
        idleScreen.classList.add("hidden");
        activeScreen.classList.remove("hidden");

        const itemsList = prediction.results || prediction.items || [];
        let itemsHtml = itemsList.map(item => `
            <div class="stove-output-line">
                <span>🍽 ${item.item || item.name}</span>
                <span>........ ${item.predicted_quantity || item.quantity}</span>
            </div>
        `).join("");

        activeScreen.innerHTML = `
            <div class="stove-output-header">🔥 AI RECOMMENDED PREPARATION</div>
            ${itemsHtml}
            <div class="stove-output-total">
                <span>TOTAL</span>
                <span>${prediction.total} PORTIONS</span>
            </div>
        `;
    }
}

// ============================================================
// NOTIFICATION SYSTEM CONNECTION
// ============================================================

function updateNotification(prediction) {
    const badge = document.getElementById("notifBadge");
    const content = document.getElementById("notifContent");

    if (badge) {
        badge.classList.remove("hidden");
        badge.textContent = "1";
        AppState.hasUnreadNotification = true;
    }

    if (content) {
        const itemsList = prediction.results || prediction.items || [];
        let itemsHtml = itemsList.map(item => `
            <div class="notif-result-line">
                <span>${item.item || item.name}</span>
                <span>&rarr; ${item.predicted_quantity || item.quantity}</span>
            </div>
        `).join("");

        content.innerHTML = `
            <div class="notif-result-box">
                <div style="font-weight: bold; margin-bottom: 4px;">AI FOOD PREPARATION READY</div>
                <div style="font-size: 0.75rem; color: var(--color-dark-sand); margin-bottom: 8px;">Date: ${prediction.date} (${prediction.day}) | Present: ${prediction.attendance}</div>
                ${itemsHtml}
                <div class="notif-result-line notif-result-total">
                    <span>Total</span>
                    <span>${prediction.total} portions</span>
                </div>
            </div>
        `;
    }
}

function toggleNotificationDropdown() {
    const dropdown = document.getElementById("notifDropdown");
    const badge = document.getElementById("notifBadge");

    if (dropdown) {
        dropdown.classList.toggle("hidden");
        if (!dropdown.classList.contains("hidden")) {
            if (badge) badge.classList.add("hidden");
            AppState.hasUnreadNotification = false;
        }
    }
}

// ============================================================
// MODAL DISPLAY HANDLERS
// ============================================================

function openFeedbackModal() { document.getElementById("feedbackModal")?.classList.remove("hidden"); }
function closeFeedbackModal() { document.getElementById("feedbackModal")?.classList.add("hidden"); }

async function openHistoryModal() {
    const modal = document.getElementById("historyModal");
    const listEl = document.getElementById("historyList");
    if (modal) modal.classList.remove("hidden");

    if (listEl) {
        try {
            const res = await fetch(`${API_BASE_URL}/history`);
            if (res.ok) {
                const data = await res.json();
                renderHistoryModal(data.history);
            }
        } catch (err) {
            console.warn("[BACKEND API] Failed to fetch prediction history.", err);
        }
    }
}
function closeHistoryModal() { document.getElementById("historyModal")?.classList.add("hidden"); }

async function openCookinCheckModal() {
    const modal = document.getElementById("cookinCheckModal");
    if (modal) modal.classList.remove("hidden");

    try {
        const res = await fetch(`${API_BASE_URL}/cooking-items`);
        if (res.ok) {
            const data = await res.json();
        }
    } catch (err) {
        console.warn("[BACKEND API] Failed to fetch cooking items history.", err);
    }
}
function closeCookinCheckModal() { document.getElementById("cookinCheckModal")?.classList.add("hidden"); }

function openHelpModal() { document.getElementById("helpModal")?.classList.remove("hidden"); }
function closeHelpModal() { document.getElementById("closeHelpModal")?.classList.add("hidden"); }

function openSettingsModal() { document.getElementById("settingsModal")?.classList.remove("hidden"); }
function closeSettingsModal() { document.getElementById("settingsModal")?.classList.add("hidden"); }

function renderHistoryModal(historyData) {
    const listEl = document.getElementById("historyList");
    if (!listEl || !historyData) return;

    listEl.innerHTML = historyData.map(rec => `
        <div class="history-card">
            <div class="history-date">📅 ${rec.date} (${rec.day}) - Present: ${rec.attendance}</div>
            <div class="history-breakdown">
                ${rec.items.map(i => `${i.name} &rarr; ${i.quantity}`).join(' | ')}
            </div>
        </div>
    `).join("");
}

// ============================================================
// SETTINGS HANDLERS
// ============================================================

function toggleDarkMode(enabled) {
    AppState.settings.darkMode = enabled;
    if (enabled) {
        document.body.classList.add("dark-mode");
    } else {
        document.body.classList.remove("dark-mode");
    }
}

function updateFontSize(size) {
    AppState.settings.fontSize = size;
    document.body.classList.remove("font-large", "font-xlarge");
    if (size === "large") document.body.classList.add("font-large");
    if (size === "xlarge") document.body.classList.add("font-xlarge");
}

function updateAppearance(mode) {
    AppState.settings.appearance = mode;
    if (mode === "smooth") {
        document.body.classList.add("smooth-appearance");
    } else {
        document.body.classList.remove("smooth-appearance");
    }
}

function toggleAnimations(enabled) {
    AppState.settings.animationsEnabled = enabled;
    const flames = document.getElementById("stoveFlames");
    if (flames) {
        if (!enabled) flames.classList.add("hidden");
        else if (AppState.lastPrediction) flames.classList.remove("hidden");
    }
}
