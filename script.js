/**
 * AI FOOD PREP SYSTEM - FRONTEND DASHBOARD LOGIC
 * Architecture: Vanilla JavaScript (ES6)
 * Directives: Modular structure, clean comments, backend integration ready.
 */

// ============================================================
// CONFIGURATION & GLOBAL STATE
// ============================================================

// Single variable for Google Form Feedback Link (Replace with actual form URL later)
const GOOGLE_FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSc_EXAMPLE_FOOD_PREP_FEEDBACK/viewform";

// Centralized Application State
const AppState = {
    selectedDate: "2026-08-21",
    dayOfWeek: "Friday",
    attendance: 720,
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

// Mock Output History Data for History Modal
const MOCK_HISTORY_DATA = [
    {
        date: "21 AUG 2026",
        items: [
            { name: "Dosa", quantity: 250 },
            { name: "Idli", quantity: 180 },
            { name: "Rice", quantity: 90 }
        ],
        total: 520
    },
    {
        date: "20 AUG 2026",
        items: [
            { name: "Dosa", quantity: 230 },
            { name: "Idli", quantity: 200 },
            { name: "Rice", quantity: 85 }
        ],
        total: 515
    },
    {
        date: "19 AUG 2026",
        items: [
            { name: "Chapati", quantity: 300 },
            { name: "Dal", quantity: 150 },
            { name: "Rice", quantity: 100 }
        ],
        total: 550
    }
];

// ============================================================
// BACKEND API INTEGRATION HOOKS (MOCK DATA PROVIDERS)
// ============================================================

/**
 * Retrieves biometric attendance for the given date.
 * 
 * // MOCK DATA
 * // Replace with backend biometric attendance API call:
 * // return await fetch(`/api/attendance?date=${selectedDate}`).then(res => res.json());
 * 
 * @param {string} dateStr YYYY-MM-DD format
 * @returns {number} Biometric headcount
 */
function getAttendance(dateStr) {
    // Simulated backend lookup based on date
    console.log(`[API MOCK] Fetching biometric attendance for date: ${dateStr}`);
    return 720;
}

/**
 * Sends input payload to AI Model and returns predicted preparation quantities.
 * 
 * // MOCK DATA
 * // Replace with backend AI Prediction API call:
 * // return await fetch('/api/predict', { method: 'POST', body: JSON.stringify(payload) }).then(res => res.json());
 * 
 * @param {Object} payload Input data including attendance, date, menu items, history
 * @returns {Object} AI Prediction result object
 */
function generatePrediction(payload) {
    console.log("[API MOCK] Generating AI Prediction with payload:", payload);

    // Conceptually computes optimized quantities from attendance (720) & input items
    return {
        items: [
            { name: "Dosa", quantity: 250, icon: "🍽" },
            { name: "Idli", quantity: 180, icon: "🍽" },
            { name: "Rice", quantity: 90, icon: "🍚" }
        ],
        total: 520,
        attendance: payload.attendance || 720,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };
}

// ============================================================
// INITIALIZATION
// ============================================================
document.addEventListener("DOMContentLoaded", () => {
    initApp();
});

function initApp() {
    console.log("Initializing AI Food Prep System...");
    
    // Set initial date picker value (default: 2026-08-21 or current system date)
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

    // Load initial attendance headcount
    loadAttendance();

    // Bind Core UI Event Listeners
    setupEventListeners();

    // Render initial history items into History Modal
    renderHistoryModal();
}

// ============================================================
// DATE & ATTENDANCE LOGIC
// ============================================================

/**
 * Automatically calculates and renders the day of the week from the date input.
 * @param {string} dateString YYYY-MM-DD
 */
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

/**
 * Fetches attendance from data hook and updates UI element.
 */
function loadAttendance() {
    const attendanceVal = getAttendance(AppState.selectedDate);
    AppState.attendance = attendanceVal;
    
    const countEl = document.getElementById("attendanceCount");
    if (countEl) {
        countEl.textContent = attendanceVal;
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
        // Reset list and populate with pre-filled sample rows if empty
        itemsList.innerHTML = "";
        
        if (AppState.currentMenuItems.length > 0) {
            AppState.currentMenuItems.forEach(item => addItemRow(item.name, item.quantity));
        } else {
            // Default initial sample menu items
            addItemRow("Rice", 50);
            addItemRow("Dal", 20);
            addItemRow("Vegetables", 15);
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
        <input type="text" class="input-field item-name-input" placeholder="Item Name (e.g., Rice)" value="${name}">
        <input type="number" class="input-field item-qty-input" placeholder="Qty" min="1" value="${qty}">
        <button type="button" class="btn-remove-row" title="Remove Item">&times;</button>
    `;

    // Attach row remove listener
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
        alert("Please enter at least one valid item name and quantity.");
        return;
    }

    // Save menu state
    AppState.currentMenuItems = items;
    closeVesselModal();

    // Trigger AI Analysis Flow
    runAIAnalysis();
}

// ============================================================
// AI ANALYSIS & STOVE EXECUTION FLOW
// ============================================================

function runAIAnalysis() {
    const overlay = document.getElementById("aiOverlay");
    if (overlay) overlay.classList.remove("hidden");

    // Simulate AI computing delay (1.5 seconds)
    setTimeout(() => {
        if (overlay) overlay.classList.add("hidden");

        // Prepare input data payload
        const payload = {
            attendance: AppState.attendance,
            date: AppState.selectedDate,
            day: AppState.dayOfWeek,
            menuItems: AppState.currentMenuItems
        };

        // Call Prediction Function
        const prediction = generatePrediction(payload);
        AppState.lastPrediction = prediction;

        // Activate Stove & Output
        activateStove(prediction);

        // Update Notification Badge & Dropdown Content
        updateNotification(prediction);
    }, 1500);
}

function activateStove(prediction) {
    // Show Flames
    if (AppState.settings.animationsEnabled) {
        document.getElementById("stoveFlames")?.classList.remove("hidden");
    }

    // Highlight Knob and Indicator
    document.getElementById("stoveKnob")?.classList.add("active");
    document.getElementById("stoveIndicator")?.classList.add("active");

    // Render Stove Output Screen
    renderStoveOutput(prediction);
}

function renderStoveOutput(prediction) {
    const idleScreen = document.getElementById("stoveIdle");
    const activeScreen = document.getElementById("stoveActive");

    if (idleScreen && activeScreen) {
        idleScreen.classList.add("hidden");
        activeScreen.classList.remove("hidden");

        let itemsHtml = prediction.items.map(item => `
            <div class="stove-output-line">
                <span>${item.icon || '🍽'} ${item.name}</span>
                <span>........ ${item.quantity}</span>
            </div>
        `).join("");

        activeScreen.innerHTML = `
            <div class="stove-output-header">AI RECOMMENDED PREPARATION</div>
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
        let itemsHtml = prediction.items.map(item => `
            <div class="notif-result-line">
                <span>${item.name}</span>
                <span>&rarr; ${item.quantity}</span>
            </div>
        `).join("");

        content.innerHTML = `
            <div class="notif-result-box">
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
            // Mark as read
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

function openHistoryModal() { document.getElementById("historyModal")?.classList.remove("hidden"); }
function closeHistoryModal() { document.getElementById("historyModal")?.classList.add("hidden"); }

function openCookinCheckModal() { document.getElementById("cookinCheckModal")?.classList.remove("hidden"); }
function closeCookinCheckModal() { document.getElementById("cookinCheckModal")?.classList.add("hidden"); }

function openHelpModal() { document.getElementById("helpModal")?.classList.remove("hidden"); }
function closeHelpModal() { document.getElementById("helpModal")?.classList.add("hidden"); }

function openSettingsModal() { document.getElementById("settingsModal")?.classList.remove("hidden"); }
function closeSettingsModal() { document.getElementById("settingsModal")?.classList.add("hidden"); }

function renderHistoryModal() {
    const listEl = document.getElementById("historyList");
    if (!listEl) return;

    listEl.innerHTML = MOCK_HISTORY_DATA.map(rec => `
        <div class="history-card">
            <div class="history-date">📅 ${rec.date}</div>
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
