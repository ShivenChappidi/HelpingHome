// Main Application Logic

const app = document.getElementById('app');

// HTML Structure
if (app) {
    app.innerHTML = `
    <!-- Header -->
    <header>
        <h1>HelpingHome.</h1>
        <div class="header-controls">
            <!-- Notification Center -->
            <div class="notification-wrapper">
                <button class="bell-btn" id="bellBtn" aria-label="Notifications">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path>
                        <path d="M13.73 21a2 2 0 0 1-3.46 0"></path>
                    </svg>
                </button>
                <div class="notification-dropdown" id="notificationDropdown">
                    <div class="notification-header">Recent Notifications</div>
                    <ul class="notification-list">
                        <li class="notification-item">
                            Motion detected in Kitchen
                            <span class="notification-time">2 mins ago</span>
                        </li>
                        <li class="notification-item">
                            Bathroom humidity high
                            <span class="notification-time">15 mins ago</span>
                        </li>
                        <li class="notification-item">
                            Laundry cycle completed
                            <span class="notification-time">1 hour ago</span>
                        </li>
                        <li class="notification-item">
                            System check passed
                            <span class="notification-time">Today, 8:00 AM</span>
                        </li>
                    </ul>
                </div>
            </div>
            
            <!-- Professional Theme Toggle (Sun/Moon + Dropdown) -->
            <div class="theme-wrapper">
                <button class="theme-btn" id="themeBtn" aria-label="Toggle theme">
                    <!-- Sun Icon (Visible in Light) -->
                    <svg class="sun-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <circle cx="12" cy="12" r="5"></circle>
                        <line x1="12" y1="1" x2="12" y2="3"></line>
                        <line x1="12" y1="21" x2="12" y2="23"></line>
                        <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line>
                        <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line>
                        <line x1="1" y1="12" x2="3" y2="12"></line>
                        <line x1="21" y1="12" x2="23" y2="12"></line>
                        <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line>
                        <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>
                    </svg>
                    <!-- Moon Icon (Visible in Dark) -->
                    <svg class="moon-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
                    </svg>
                    <span style="position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px; overflow: hidden; clip: rect(0, 0, 0, 0); white-space: nowrap; border-width: 0;">Toggle theme</span>
                </button>
                <div class="theme-dropdown" id="themeDropdown">
                    <div class="theme-item" data-theme="light">Light</div>
                    <div class="theme-item" data-theme="dark">Dark</div>
                    <div class="theme-item" data-theme="system">System</div>
                </div>
            </div>
        </div>
    </header>

    <!-- Mode Switcher -->
    <div class="mode-switcher">
        <button class="mode-btn active" id="mode-btn-user">User Mode</button>
        <button class="mode-btn" id="mode-btn-caretaker">Caretaker Mode</button>
    </div>

    <!-- 1. User View -->
    <div id="view-user" class="view-section visible">
        <section id="user-section">
            <div class="layout-grid">
                <!-- Sidebar -->
                <div class="sidebar">
                    <h2>Locations</h2>
                    <div class="button-group-vertical">
                        <button class="btn" id="user-btn-kitchen">Kitchen</button>
                        <button class="btn" id="user-btn-laundry">Laundry</button>
                        <button class="btn" id="user-btn-bathroom">Bathroom</button>
                    </div>
                </div>

                <!-- Content Area -->
                <div class="panel-container">
                    <!-- Default Placeholder -->
                    <div id="user-panel-default" class="panel visible">
                        <div style="text-align: center; color: var(--text-muted); margin-top: 100px;">
                            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" stroke-linecap="round" stroke-linejoin="round" style="margin-bottom: 16px; opacity: 0.5;">
                                <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                                <line x1="9" y1="3" x2="9" y2="21"></line>
                            </svg>
                            <p>Select a room to view details.</p>
                        </div>
                    </div>

                    <!-- Activity Monitor Panel (Shared for Kitchen & Bathroom) -->
                    <div id="user-panel-monitor" class="panel">
                        <div class="monitor-header-row">
                            <span class="monitor-title" id="user-monitor-title">Activity Monitor</span>
                            <!-- Status Chip with Pulse -->
                            <div class="status-chip">
                                <span class="status-dot"></span>
                                Active
                            </div>
                        </div>
                        
                        <div class="notifications-area">
                            <strong>Recent Events</strong>
                            <ul class="notification-area-list">
                                <li>Motion detected 5 mins ago</li>
                                <li>Temperature normal (72°F)</li>
                                <li>Routine check passed</li>
                            </ul>
                        </div>
                    </div>

                    <!-- Laundry Panel -->
                    <div id="user-panel-laundry-inner" class="panel">
                        <h3>Laundry Controls</h3>
                        <p style="color: var(--text-muted);">How much clothes do you have?</p>
                        
                        <div class="laundry-inner-group">
                            <!-- Styled to look gray/disabled but functionally clickable for the note -->
                            <button class="btn" id="laundry-lot" style="background-color: var(--btn-disabled-bg); color: var(--btn-disabled-text);">A lot of clothes</button>
                            <button class="btn" id="laundry-little" style="background-color: var(--btn-disabled-bg); color: var(--btn-disabled-text);">A little clothes</button>
                        </div>
                        <div id="laundry-note" class="inline-note" style="display: none;">This feature is coming soon</div>
                    </div>
                </div>
            </div>
        </section>
    </div>

    <!-- 2. Caretaker View -->
    <div id="view-caretaker" class="view-section">
        <section id="caretaker-section">
            <div class="layout-grid">
                <!-- Sidebar -->
                <div class="sidebar">
                    <h2>Management</h2>
                    <div class="button-group-vertical">
                        <button class="btn" id="care-btn-kitchen">Kitchen</button>
                        <button class="btn" id="care-btn-laundry">Laundry</button>
                        <button class="btn" id="care-btn-bathroom">Bathroom</button>
                        
                        <button class="btn btn-separate" id="care-btn-log">Daily Log</button>
                    </div>
                </div>

                <!-- Content Area -->
                <div class="panel-container">
                    <!-- Default Placeholder -->
                    <div id="care-panel-default" class="panel visible">
                        <div style="text-align: center; color: var(--text-muted); margin-top: 100px;">
                             <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" stroke-linecap="round" stroke-linejoin="round" style="margin-bottom: 16px; opacity: 0.5;">
                                <path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"></path>
                            </svg>
                            <p>Select a management area.</p>
                        </div>
                    </div>

                    <!-- Caretaker Kitchen Panel -->
                    <div id="care-panel-kitchen" class="panel">
                        <h3>Kitchen Management</h3>
                        <div class="button-group-vertical" style="margin-top: 20px; max-width: 300px;">
                            <button class="btn disabled" disabled>Add Recipe (Coming Soon)</button>
                            <button class="btn disabled" disabled>Add Device (Coming Soon)</button>
                        </div>
                    </div>

                    <!-- Caretaker Laundry Panel -->
                    <div id="care-panel-laundry" class="panel">
                        <h3>Laundry Management</h3>
                        <div class="button-group-vertical" style="margin-top: 20px; max-width: 300px;">
                            <button class="btn disabled" disabled>Add Cycle Type (Coming Soon)</button>
                        </div>
                    </div>

                    <!-- Caretaker Bathroom Panel -->
                    <div id="care-panel-bathroom" class="panel">
                        <h3>Bathroom Management</h3>
                        <div class="button-group-vertical" style="margin-top: 20px; max-width: 300px;">
                            <button class="btn disabled" disabled>Add Routine (Coming Soon)</button>
                        </div>
                    </div>

                    <!-- Caretaker Daily Log Panel -->
                    <div id="care-panel-log" class="panel">
                        <div class="monitor-header-row">
                            <span class="monitor-title">Daily Log</span>
                        </div>
                        <p>No new entries for today.</p>
                        <ul class="notification-area-list" style="margin-top: 20px;">
                            <li>System check at 08:00 AM: OK</li>
                            <li>System check at 12:00 PM: OK</li>
                        </ul>
                    </div>
                </div>
            </div>
        </section>
    </div>
    `;

    // --- Interaction Logic ---

    // 0. Mode Switcher Logic
    const modeBtnUser = document.getElementById('mode-btn-user');
    const modeBtnCaretaker = document.getElementById('mode-btn-caretaker');
    const viewUser = document.getElementById('view-user');
    const viewCaretaker = document.getElementById('view-caretaker');
    
    // User Section Elements
    const userPanelDefault = document.getElementById('user-panel-default');
    const userPanelMonitor = document.getElementById('user-panel-monitor');
    const userMonitorTitle = document.getElementById('user-monitor-title');
    const userPanelLaundry = document.getElementById('user-panel-laundry-inner');
    
    // Caretaker Section Elements
    const carePanelDefault = document.getElementById('care-panel-default');

    modeBtnUser?.addEventListener('click', () => {
        modeBtnUser.classList.add('active');
        modeBtnCaretaker?.classList.remove('active');
        viewUser?.classList.add('visible');
        viewCaretaker?.classList.remove('visible');
    });

    modeBtnCaretaker?.addEventListener('click', () => {
        modeBtnCaretaker.classList.add('active');
        modeBtnUser?.classList.remove('active');
        viewCaretaker?.classList.add('visible');
        viewUser?.classList.remove('visible');
    });

    // 1. Notification Center Logic
    const bellBtn = document.getElementById('bellBtn');
    const notificationDropdown = document.getElementById('notificationDropdown');

    bellBtn?.addEventListener('click', (e) => {
        e.stopPropagation(); 
        // Close theme dropdown if open
        document.getElementById('themeDropdown')?.classList.remove('visible');
        notificationDropdown?.classList.toggle('visible');
    });

    // 2. Professional Theme Toggle Logic
    const themeBtn = document.getElementById('themeBtn');
    const themeDropdown = document.getElementById('themeDropdown');
    const themeItems = document.querySelectorAll('.theme-item');

    themeBtn?.addEventListener('click', (e) => {
        e.stopPropagation();
        // Close notification dropdown if open
        notificationDropdown?.classList.remove('visible');
        themeDropdown?.classList.toggle('visible');
    });

    function setTheme(theme) {
        // Remove existing theme classes (if we had specific 'light' class, but we use default)
        document.body.classList.remove('dark');

        if (theme === 'dark') {
            document.body.classList.add('dark');
        } else if (theme === 'system') {
            const systemPrefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
            if (systemPrefersDark) {
                document.body.classList.add('dark');
            }
        }
        // 'light' is default, so we just remove 'dark'
        
        // Close dropdown
        themeDropdown?.classList.remove('visible');
    }

    themeItems.forEach(item => {
        item.addEventListener('click', (e) => {
            const selectedTheme = (e.target as HTMLElement).getAttribute('data-theme');
            if (selectedTheme) {
                setTheme(selectedTheme);
            }
        });
    });

    // Close Dropdowns on outside click
    document.addEventListener('click', (e) => {
        const target = e.target as HTMLElement;
        if (!target.closest('.notification-wrapper')) {
            notificationDropdown?.classList.remove('visible');
        }
        if (!target.closest('.theme-wrapper')) {
            themeDropdown?.classList.remove('visible');
        }
    });


    // 3. User Section Panel Logic
    const userKitchenBtn = document.getElementById('user-btn-kitchen');
    const userLaundryBtn = document.getElementById('user-btn-laundry');
    const userBathroomBtn = document.getElementById('user-btn-bathroom');
    
    // Internal Laundry Buttons
    const laundryLotBtn = document.getElementById('laundry-lot');
    const laundryLittleBtn = document.getElementById('laundry-little');
    const laundryNote = document.getElementById('laundry-note');

    function hideAllUserPanels() {
        const panels = document.querySelectorAll('#user-section .panel');
        panels.forEach(p => p.classList.remove('visible'));
        
        const buttons = document.querySelectorAll('#user-section .sidebar .btn');
        buttons.forEach(b => b.classList.remove('active'));
    }

    // Logic: Kitchen -> Activity Monitor
    userKitchenBtn?.addEventListener('click', () => {
        hideAllUserPanels();
        userKitchenBtn.classList.add('active');
        if (userPanelMonitor && userMonitorTitle) {
            userMonitorTitle.textContent = "Activity Monitor — Kitchen";
            userPanelMonitor.classList.add('visible');
        }
    });

    // Logic: Bathroom -> Activity Monitor
    userBathroomBtn?.addEventListener('click', () => {
        hideAllUserPanels();
        userBathroomBtn.classList.add('active');
        if (userPanelMonitor && userMonitorTitle) {
            userMonitorTitle.textContent = "Activity Monitor — Bathroom";
            userPanelMonitor.classList.add('visible');
        }
    });
    
    // Logic: Laundry -> Laundry Panel
    userLaundryBtn?.addEventListener('click', () => {
        hideAllUserPanels();
        userLaundryBtn.classList.add('active');
        userPanelLaundry?.classList.add('visible');
    });

    // Internal Laundry Logic
    function showLaundryNote() {
        if (laundryNote) {
            laundryNote.style.display = 'block';
            laundryNote.textContent = "This feature is coming soon";
        }
    }
    laundryLotBtn?.addEventListener('click', showLaundryNote);
    laundryLittleBtn?.addEventListener('click', showLaundryNote);

    // 4. Caretaker Section Panel Logic
    const careKitchenBtn = document.getElementById('care-btn-kitchen');
    const careLaundryBtn = document.getElementById('care-btn-laundry');
    const careBathroomBtn = document.getElementById('care-btn-bathroom');
    const careLogBtn = document.getElementById('care-btn-log');

    function hideAllCarePanels() {
        const panels = document.querySelectorAll('#caretaker-section .panel');
        panels.forEach(p => p.classList.remove('visible'));

        const buttons = document.querySelectorAll('#caretaker-section .sidebar .btn');
        buttons.forEach(b => b.classList.remove('active'));
    }

    function activateCarePanel(btn: HTMLElement, panelId: string) {
        hideAllCarePanels();
        btn.classList.add('active');
        const panel = document.getElementById(panelId);
        if (panel) panel.classList.add('visible');
    }

    careKitchenBtn?.addEventListener('click', () => activateCarePanel(careKitchenBtn, 'care-panel-kitchen'));
    careLaundryBtn?.addEventListener('click', () => activateCarePanel(careLaundryBtn, 'care-panel-laundry'));
    careBathroomBtn?.addEventListener('click', () => activateCarePanel(careBathroomBtn, 'care-panel-bathroom'));
    careLogBtn?.addEventListener('click', () => activateCarePanel(careLogBtn, 'care-panel-log'));
}