// Main Application Logic

const app = document.getElementById('app');

// HTML Structure
if (app) {
    app.innerHTML = `
    <!-- Laundry Cycle Complete Popup Notification -->
    <div id="laundry-popup-notification" class="laundry-popup" style="display: none;">
        <div class="laundry-popup-content">
            <div class="laundry-popup-text">
                <div class="laundry-popup-title">Laundry Cycle Complete</div>
                <div class="laundry-popup-message" id="laundry-popup-message">Your laundry cycle has finished!</div>
            </div>
        </div>
    </div>

    <!-- Header -->
    <header>
        <h1>HelpingHome</h1>
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
            
            <!-- Voice Selector -->
            <div class="theme-wrapper">
                <button class="theme-btn" id="voiceBtn" aria-label="Select voice">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path>
                        <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
                        <line x1="12" y1="19" x2="12" y2="23"></line>
                        <line x1="8" y1="23" x2="16" y2="23"></line>
                    </svg>
                    <span style="position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px; overflow: hidden; clip: rect(0, 0, 0, 0); white-space: nowrap; border-width: 0;">Select voice</span>
                </button>
                <div class="theme-dropdown" id="voiceDropdown">
                    <div class="theme-item" data-voice="australian-woman">Shivani</div>
                    <div class="theme-item" data-voice="american-man">Caleb</div>
                    <div class="theme-item" data-voice="british-woman">Sukhleen</div>
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
                        
                        <!-- Recipe Selection (Kitchen Only) -->
                        <div id="recipe-selection-container" style="display: none; margin-bottom: 30px; padding-bottom: 20px; border-bottom: 1px solid var(--border-color);">
                            <h4 style="margin-bottom: 12px;">Start a Recipe</h4>
                            <div style="display: flex; gap: 12px; align-items: center; flex-wrap: wrap;">
                                <select id="recipe-select" style="flex: 1; min-width: 200px; padding: 10px 12px; border: 1px solid var(--border-color); border-radius: 8px; background-color: var(--bg-panel); color: var(--text-main); font-family: inherit; font-size: 0.95rem;">
                                    <option value="">Select a recipe...</option>
                                </select>
                                <button class="btn" id="start-recipe-btn" style="background-color: var(--accent-color); color: var(--accent-text);" disabled>Start Recipe</button>
                                <button class="btn" id="stop-recipe-btn" style="display: none; background-color: #dc3545; color: white;">Stop Recipe</button>
                            </div>
                            <div id="recipe-status" style="margin-top: 12px; padding: 10px; border-radius: 4px; display: none;"></div>
                        </div>
                        
                        <!-- Routine Selection (Bathroom Only) -->
                        <div id="routine-selection-container" style="display: none; margin-bottom: 30px; padding-bottom: 20px; border-bottom: 1px solid var(--border-color);">
                            <h4 style="margin-bottom: 12px;">Start a Routine</h4>
                            <div style="display: flex; gap: 12px; align-items: center; flex-wrap: wrap;">
                                <select id="routine-select" style="flex: 1; min-width: 200px; padding: 10px 12px; border: 1px solid var(--border-color); border-radius: 8px; background-color: var(--bg-panel); color: var(--text-main); font-family: inherit; font-size: 0.95rem;">
                                    <option value="">Select a routine...</option>
                                </select>
                                <button class="btn" id="start-routine-btn" style="background-color: var(--accent-color); color: var(--accent-text);" disabled>Start Routine</button>
                                <button class="btn" id="stop-routine-btn" style="display: none; background-color: #dc3545; color: white;">Stop Routine</button>
                            </div>
                            <div id="routine-status" style="margin-top: 12px; padding: 10px; border-radius: 4px; display: none;"></div>
                        </div>
                        
                        <div class="notifications-area">
                            <strong>Recent Events</strong>
                            <ul class="notification-area-list" id="activity-event-list">
                                <li>Loading events...</li>
                            </ul>
                        </div>
                    </div>

                    <!-- Laundry Panel -->
                    <div id="user-panel-laundry-inner" class="panel">
                        <div class="monitor-header-row">
                            <span class="monitor-title">Laundry Routine</span>
                        </div>
                        
                        <!-- Laundry Routine Selection -->
                        <div id="laundry-routine-selection-container" style="margin-bottom: 30px; padding-bottom: 20px; border-bottom: 1px solid var(--border-color);">
                            <h4 style="margin-bottom: 12px;">Start a Wash Cycle</h4>
                            <div style="display: flex; gap: 12px; align-items: center; flex-wrap: wrap;">
                                <select id="laundry-routine-select" style="flex: 1; min-width: 200px; padding: 10px 12px; border: 1px solid var(--border-color); border-radius: 8px; background-color: var(--bg-panel); color: var(--text-main); font-family: inherit; font-size: 0.95rem;">
                                    <option value="">Select a wash cycle...</option>
                                </select>
                                <button class="btn" id="start-laundry-routine-btn" style="background-color: var(--accent-color); color: var(--accent-text);" disabled>Start Cycle</button>
                                <button class="btn" id="stop-laundry-routine-btn" style="display: none; background-color: #dc3545; color: white;">Stop Cycle</button>
                            </div>
                            <div id="laundry-routine-status" style="margin-top: 12px; padding: 10px; border-radius: 4px; display: none;"></div>
                        </div>
                        
                        <div class="notifications-area">
                            <strong>Recent Events</strong>
                            <ul class="notification-area-list" id="laundry-event-list">
                                <li>Loading events...</li>
                            </ul>
                        </div>
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
                        <div class="button-group-vertical" style="margin-top: 20px; max-width: 400px;">
                            <button class="btn" id="add-recipe-btn">Add Recipe</button>
                            <button class="btn disabled" disabled style="white-space: nowrap;">Add Device (Coming Soon)</button>
                        </div>
                        
                        <div style="margin-top: 40px; padding-top: 30px; border-top: 1px solid var(--border-color);">
                            <h4 style="margin-bottom: 15px;">Stored Recipes</h4>
                            <div id="recipes-list-container">
                                <p style="color: var(--text-muted);">Loading recipes...</p>
                            </div>
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
                        <div class="button-group-vertical" style="margin-top: 20px; max-width: 400px;">
                            <button class="btn" id="add-routine-btn">Add Routine</button>
                            <button class="btn disabled" disabled style="white-space: nowrap;">Add Device (Coming Soon)</button>
                        </div>
                        
                        <div style="margin-top: 40px; padding-top: 30px; border-top: 1px solid var(--border-color);">
                            <h4 style="margin-bottom: 15px;">Stored Routines</h4>
                            <div id="routines-list-container">
                                <p style="color: var(--text-muted);">Loading routines...</p>
                            </div>
                        </div>
                    </div>

                    <!-- Recipe Modal -->
                    <div id="recipe-modal" class="modal" style="display: none;">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h3>Add New Recipe</h3>
                                <button class="modal-close" id="recipe-modal-close">&times;</button>
                            </div>
                            <div class="modal-body">
                                <form id="recipe-form">
                                    <div class="form-group">
                                        <label for="recipe-name">Recipe Name *</label>
                                        <input type="text" id="recipe-name" name="name" required placeholder="e.g., Chocolate Chip Cookies">
                                    </div>
                                    <div class="form-group">
                                        <label for="recipe-description">Description</label>
                                        <input type="text" id="recipe-description" name="description" placeholder="Optional description">
                                    </div>
                                    <div class="form-group">
                                        <label for="recipe-steps">Steps * (one per line)</label>
                                        <textarea id="recipe-steps" name="steps" rows="8" required placeholder="Gather ingredients&#10;Crack eggs into bowl&#10;Whisk eggs&#10;Heat pan&#10;Cook until done"></textarea>
                                    </div>
                                    <div id="recipe-form-status" style="display: none; margin-top: 15px; padding: 10px; border-radius: 4px;"></div>
                                    <div class="modal-actions">
                                        <button type="button" class="btn" id="recipe-form-cancel" style="background-color: var(--bg-secondary);">Cancel</button>
                                        <button type="submit" class="btn" style="background-color: var(--accent-color); color: var(--accent-text);">Add Recipe</button>
                                    </div>
                                </form>
                            </div>
                        </div>
                    </div>

                    <!-- Caretaker Daily Log Panel -->
                    <div id="care-panel-log" class="panel">
                        <div class="monitor-header-row">
                            <span class="monitor-title">Daily Log</span>
                        </div>
                        
                        <div style="margin-top: 20px;">
                            <p style="margin-bottom: 20px;">Generate a daily summary of activities from the last 24 hours.</p>
                            
                            <button class="btn" id="generate-daily-log-btn" style="margin-bottom: 20px;">
                                Generate Daily Log
                            </button>
                            
                            <div id="daily-log-status" style="margin-top: 15px; padding: 10px; border-radius: 4px; display: none;"></div>
                            
                            <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid var(--border);">
                                <h4 style="margin-bottom: 10px;">Access Your Journals</h4>
                                <p style="color: var(--text-muted); margin-bottom: 15px;">
                                    View and manage your daily logs and journals on OpenNote.
                                </p>
                                <a href="https://opennote.com" target="_blank" rel="noopener noreferrer" 
                                   class="btn" style="display: inline-block; text-decoration: none;">
                                    Open OpenNote →
                                </a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </section>
    </div>
    `;

    // --- Interaction Logic ---

    // API Configuration
    const API_BASE_URL = 'http://localhost:5001/api';  // Changed from 5000 to 5001 (5000 often used by AirPlay on macOS)

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
        // Close other dropdowns if open
        document.getElementById('themeDropdown')?.classList.remove('visible');
        document.getElementById('voiceDropdown')?.classList.remove('visible');
        notificationDropdown?.classList.toggle('visible');
    });

    // 2. Voice Selector Logic
    const voiceBtn = document.getElementById('voiceBtn');
    const voiceDropdown = document.getElementById('voiceDropdown');
    const voiceItems = document.querySelectorAll('[data-voice]');

    // Load saved voice preference
    let currentVoice = localStorage.getItem('voicePreference') || 'australian-woman';
    
    // Update voice selection visual state
    function updateVoiceSelection(voice: string) {
        voiceItems.forEach(item => {
            if (item.getAttribute('data-voice') === voice) {
                item.classList.add('active');
            } else {
                item.classList.remove('active');
            }
        });
    }
    
    voiceBtn?.addEventListener('click', (e) => {
        e.stopPropagation();
        // Close other dropdowns if open
        notificationDropdown?.classList.remove('visible');
        document.getElementById('themeDropdown')?.classList.remove('visible');
        voiceDropdown?.classList.toggle('visible');
    });

    async function setVoice(voice: string) {
        currentVoice = voice;
        localStorage.setItem('voicePreference', voice);
        updateVoiceSelection(voice);
        
        // Send voice preference to backend
        try {
            const response = await fetch(`${API_BASE_URL}/voice-preference`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ voice: voice })
            });
            
            if (!response.ok) {
                console.error('Failed to update voice preference on server');
            }
        } catch (error) {
            console.error('Error updating voice preference:', error);
        }
        
        // Close dropdown
        voiceDropdown?.classList.remove('visible');
    }

    voiceItems.forEach(item => {
        item.addEventListener('click', () => {
            const voice = item.getAttribute('data-voice');
            if (voice) {
                setVoice(voice);
            }
        });
    });
    
    // Initialize voice selection on load
    updateVoiceSelection(currentVoice);
    
    // Load voice preference from backend on startup
    (async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/voice-preference`);
            if (response.ok) {
                const data = await response.json();
                if (data.voice) {
                    currentVoice = data.voice;
                    localStorage.setItem('voicePreference', data.voice);
                    updateVoiceSelection(data.voice);
                }
            }
        } catch (error) {
            console.error('Error loading voice preference:', error);
        }
    })();

    // 3. Professional Theme Toggle Logic
    const themeBtn = document.getElementById('themeBtn');
    const themeDropdown = document.getElementById('themeDropdown');
    const themeItems = document.querySelectorAll('.theme-item');

    themeBtn?.addEventListener('click', (e) => {
        e.stopPropagation();
        // Close other dropdowns if open
        notificationDropdown?.classList.remove('visible');
        document.getElementById('voiceDropdown')?.classList.remove('visible');
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
            voiceDropdown?.classList.remove('visible');
        }
    });


    // 3. User Section Panel Logic
    const userKitchenBtn = document.getElementById('user-btn-kitchen');
    const userLaundryBtn = document.getElementById('user-btn-laundry');
    const userBathroomBtn = document.getElementById('user-btn-bathroom');
    
    // Laundry Routine Elements
    const laundryRoutineSelect = document.getElementById('laundry-routine-select') as HTMLSelectElement;
    const startLaundryRoutineBtn = document.getElementById('start-laundry-routine-btn') as HTMLButtonElement;
    const stopLaundryRoutineBtn = document.getElementById('stop-laundry-routine-btn') as HTMLButtonElement;
    const laundryRoutineStatus = document.getElementById('laundry-routine-status');
    const laundryEventList = document.getElementById('laundry-event-list');

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
            // Show recipe selection container for kitchen, hide routine selection
            const recipeContainer = document.getElementById('recipe-selection-container');
            const routineContainer = document.getElementById('routine-selection-container');
            if (recipeContainer) recipeContainer.style.display = 'block';
            if (routineContainer) routineContainer.style.display = 'none';
            // Load recipes and fetch events for kitchen
            setTimeout(() => {
                loadRecipesForUser();
                fetchActivityEventsForPanel('kitchen');
            }, 100);
        }
    });

    // Logic: Bathroom -> Activity Monitor
    userBathroomBtn?.addEventListener('click', () => {
        hideAllUserPanels();
        userBathroomBtn.classList.add('active');
        if (userPanelMonitor && userMonitorTitle) {
            userMonitorTitle.textContent = "Activity Monitor — Bathroom";
            userPanelMonitor.classList.add('visible');
            // Hide recipe selection container for bathroom, show routine selection
            const recipeContainer = document.getElementById('recipe-selection-container');
            const routineContainer = document.getElementById('routine-selection-container');
            if (recipeContainer) recipeContainer.style.display = 'none';
            if (routineContainer) {
                routineContainer.style.display = 'block';
                // Load routines for bathroom
                setTimeout(() => loadRoutinesForUser(), 100);
            }
            // Fetch events for bathroom
            setTimeout(() => fetchActivityEventsForPanel('bathroom'), 100);
        }
    });
    
    // Logic: Laundry -> Laundry Panel
    userLaundryBtn?.addEventListener('click', () => {
        hideAllUserPanels();
        userLaundryBtn.classList.add('active');
        userPanelLaundry?.classList.add('visible');
        // Load laundry routines and fetch events for laundry
        setTimeout(() => {
            loadLaundryRoutinesForUser();
            fetchActivityEventsForPanel('laundry');
        }, 100);
    });

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

    careKitchenBtn?.addEventListener('click', () => {
        activateCarePanel(careKitchenBtn, 'care-panel-kitchen');
        // Load recipes when opening kitchen panel
        setTimeout(() => loadRecipesList(), 100);
    });
    careLaundryBtn?.addEventListener('click', () => activateCarePanel(careLaundryBtn, 'care-panel-laundry'));
    careBathroomBtn?.addEventListener('click', () => {
        activateCarePanel(careBathroomBtn, 'care-panel-bathroom');
        // Load routines when opening bathroom panel
        setTimeout(() => loadRoutinesList(), 100);
    });
    careLogBtn?.addEventListener('click', () => activateCarePanel(careLogBtn, 'care-panel-log'));

    // 5. Recipe Management
    const addRecipeBtn = document.getElementById('add-recipe-btn');
    const recipeModal = document.getElementById('recipe-modal');
    const recipeModalClose = document.getElementById('recipe-modal-close');
    const recipeFormCancel = document.getElementById('recipe-form-cancel');
    const recipeForm = document.getElementById('recipe-form') as HTMLFormElement;
    const recipeFormStatus = document.getElementById('recipe-form-status');
    const recipesListContainer = document.getElementById('recipes-list-container');

    // Load and display recipes list
    async function loadRecipesList() {
        if (!recipesListContainer) return;
        
        recipesListContainer.innerHTML = '<p style="color: var(--text-muted);">Loading recipes...</p>';
        
        try {
            const response = await fetch(`${API_BASE_URL}/recipes`);
            const data = await response.json();
            
            if (data.status === 'success' && data.recipes) {
                const recipes = data.recipes;
                const recipeIds = Object.keys(recipes);
                
                if (recipeIds.length === 0) {
                    recipesListContainer.innerHTML = '<p style="color: var(--text-muted);">No recipes yet. Add one above!</p>';
                    return;
                }
                
                let html = '<div style="display: flex; flex-direction: column; gap: 12px;">';
                
                recipeIds.forEach(recipeId => {
                    const recipe = recipes[recipeId];
                    html += `
                        <div style="border: 1px solid var(--border-color); border-radius: 10px; padding: 16px; background-color: var(--bg-secondary);">
                            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 8px;">
                                <div>
                                    <strong style="font-size: 1.05rem; color: var(--text-main);">${recipe.name || recipeId}</strong>
                                    ${recipe.description ? `<p style="margin: 4px 0 0 0; color: var(--text-muted); font-size: 0.9rem;">${recipe.description}</p>` : ''}
                                </div>
                                <span style="color: var(--text-muted); font-size: 0.85rem; white-space: nowrap; margin-left: 12px;">${recipe.steps?.length || 0} steps</span>
                            </div>
                            ${recipe.steps && recipe.steps.length > 0 ? `
                                <details style="margin-top: 8px;">
                                    <summary style="cursor: pointer; color: var(--accent-color); font-size: 0.9rem; user-select: none;">View steps</summary>
                                    <ol style="margin: 12px 0 0 0; padding-left: 20px; color: var(--text-muted); font-size: 0.9rem;">
                                        ${recipe.steps.map((step: string) => `<li style="margin-bottom: 6px;">${step}</li>`).join('')}
                                    </ol>
                                </details>
                            ` : ''}
                        </div>
                    `;
                });
                
                html += '</div>';
                recipesListContainer.innerHTML = html;
            } else {
                recipesListContainer.innerHTML = '<p style="color: var(--text-muted);">No recipes found.</p>';
            }
        } catch (error: any) {
            const errorMsg = error.message || 'Failed to load recipes';
            if (errorMsg.includes('fetch') || errorMsg.includes('network')) {
                recipesListContainer.innerHTML = `<p style="color: #f8d7da;">Cannot load recipes. Make sure the API server is running on ${API_BASE_URL}</p>`;
            } else {
                recipesListContainer.innerHTML = `<p style="color: #f8d7da;">Error loading recipes: ${errorMsg}</p>`;
            }
        }
    }

    function openRecipeModal() {
        if (recipeModal) {
            recipeModal.style.display = 'flex';
            // Reset form
            if (recipeForm) recipeForm.reset();
            if (recipeFormStatus) {
                recipeFormStatus.style.display = 'none';
                recipeFormStatus.textContent = '';
            }
        }
    }

    function closeRecipeModal() {
        if (recipeModal) {
            recipeModal.style.display = 'none';
        }
    }

    addRecipeBtn?.addEventListener('click', openRecipeModal);
    recipeModalClose?.addEventListener('click', closeRecipeModal);
    recipeFormCancel?.addEventListener('click', closeRecipeModal);

    // Close modal when clicking outside
    recipeModal?.addEventListener('click', (e) => {
        if (e.target === recipeModal) {
            closeRecipeModal();
        }
    });

    // Handle form submission
    recipeForm?.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        if (!recipeFormStatus) return;
        
        const formData = new FormData(recipeForm);
        const name = (formData.get('name') as string)?.trim();
        const description = (formData.get('description') as string)?.trim();
        const stepsText = (formData.get('steps') as string)?.trim();
        
        if (!name || !stepsText) {
            recipeFormStatus.style.display = 'block';
            recipeFormStatus.style.backgroundColor = '#f8d7da';
            recipeFormStatus.style.color = '#721c24';
            recipeFormStatus.textContent = 'Please fill in all required fields.';
            return;
        }
        
        // Parse steps (one per line)
        const steps = stepsText.split('\n')
            .map(step => step.trim())
            .filter(step => step.length > 0);
        
        if (steps.length === 0) {
            recipeFormStatus.style.display = 'block';
            recipeFormStatus.style.backgroundColor = '#f8d7da';
            recipeFormStatus.style.color = '#721c24';
            recipeFormStatus.textContent = 'Please provide at least one step.';
            return;
        }
        
        // Generate recipe_id from name
        const recipe_id = name.toLowerCase().replace(/[^a-z0-9]+/g, '_').replace(/^_|_$/g, '');
        
        // Show loading state
        recipeFormStatus.style.display = 'block';
        recipeFormStatus.style.backgroundColor = 'var(--bg-secondary)';
        recipeFormStatus.style.color = 'var(--text)';
        recipeFormStatus.textContent = 'Adding recipe...';
        
        try {
            const response = await fetch(`${API_BASE_URL}/recipes`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    recipe_id: recipe_id,
                    name: name,
                    steps: steps,
                    description: description || ''
                })
            });
            
            const data = await response.json();
            
            if (data.status === 'success') {
                recipeFormStatus.style.backgroundColor = '#d4edda';
                recipeFormStatus.style.color = '#155724';
                recipeFormStatus.textContent = `Recipe "${name}" added successfully!`;
                
                // Refresh recipes list
                loadRecipesList();
                
                // Clear form and close modal after 1.5 seconds
                setTimeout(() => {
                    recipeForm.reset();
                    closeRecipeModal();
                }, 1500);
            } else {
                recipeFormStatus.style.backgroundColor = '#f8d7da';
                recipeFormStatus.style.color = '#721c24';
                recipeFormStatus.textContent = `Error: ${data.message || 'Failed to add recipe'}`;
            }
        } catch (error: any) {
            recipeFormStatus.style.backgroundColor = '#f8d7da';
            recipeFormStatus.style.color = '#721c24';
            const errorMsg = error.message || 'Failed to add recipe';
            if (errorMsg.includes('fetch') || errorMsg.includes('network')) {
                recipeFormStatus.textContent = `Error: Cannot connect to API server. Please make sure the API server is running on ${API_BASE_URL}`;
            } else {
                recipeFormStatus.textContent = `Error: ${errorMsg}`;
            }
        }
    });

    // 6. Recipe Selection and Guidance (User Kitchen Section)
    const recipeSelect = document.getElementById('recipe-select') as HTMLSelectElement;
    const startRecipeBtn = document.getElementById('start-recipe-btn') as HTMLButtonElement;
    const stopRecipeBtn = document.getElementById('stop-recipe-btn') as HTMLButtonElement;
    const recipeStatus = document.getElementById('recipe-status');

    // Load recipes into dropdown
    async function loadRecipesForUser() {
        if (!recipeSelect) return;
        
        try {
            const response = await fetch(`${API_BASE_URL}/recipes`);
            const data = await response.json();
            
            if (data.status === 'success' && data.recipes) {
                // Clear existing options except the first one
                recipeSelect.innerHTML = '<option value="">Select a recipe...</option>';
                
                // Add recipes to dropdown
                Object.keys(data.recipes).forEach(recipeId => {
                    const recipe = data.recipes[recipeId];
                    const option = document.createElement('option');
                    option.value = recipeId;
                    option.textContent = recipe.name || recipeId;
                    recipeSelect.appendChild(option);
                });
            }
        } catch (error: any) {
            console.error('Error loading recipes:', error);
        }
    }

    // Enable/disable start button based on selection
    recipeSelect?.addEventListener('change', (e) => {
        if (startRecipeBtn) {
            startRecipeBtn.disabled = !(e.target as HTMLSelectElement).value;
        }
    });

    // Start recipe guidance
    startRecipeBtn?.addEventListener('click', async () => {
        const selectedRecipeId = recipeSelect?.value;
        if (!selectedRecipeId || !recipeStatus) return;
        
        startRecipeBtn.disabled = true;
        recipeStatus.style.display = 'block';
        recipeStatus.style.backgroundColor = 'var(--bg-secondary)';
        recipeStatus.style.color = 'var(--text)';
        recipeStatus.textContent = 'Starting recipe guidance...';
        
        try {
            const response = await fetch(`${API_BASE_URL}/recipe-guidance/start`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    recipe_id: selectedRecipeId
                })
            });
            
            const data = await response.json();
            
            if (data.status === 'success') {
                recipeStatus.style.backgroundColor = '#d4edda';
                recipeStatus.style.color = '#155724';
                recipeStatus.textContent = `Recipe "${data.recipe_name}" started! Follow the audio instructions and press the pressure sensor for next step.`;
                
                // Update UI - show stop button, hide start button
                if (startRecipeBtn) startRecipeBtn.style.display = 'none';
                if (stopRecipeBtn) stopRecipeBtn.style.display = 'block';
                if (recipeSelect) recipeSelect.disabled = true;
            } else {
                recipeStatus.style.backgroundColor = '#f8d7da';
                recipeStatus.style.color = '#721c24';
                recipeStatus.textContent = `Error: ${data.message || 'Failed to start recipe'}`;
                startRecipeBtn.disabled = false;
            }
        } catch (error: any) {
            recipeStatus.style.backgroundColor = '#f8d7da';
            recipeStatus.style.color = '#721c24';
            const errorMsg = error.message || 'Failed to start recipe';
            if (errorMsg.includes('fetch') || errorMsg.includes('network')) {
                recipeStatus.textContent = `Error: Cannot connect to API server. Make sure the API server is running on ${API_BASE_URL}`;
            } else {
                recipeStatus.textContent = `Error: ${errorMsg}`;
            }
            startRecipeBtn.disabled = false;
        }
    });

    // Stop recipe guidance
    stopRecipeBtn?.addEventListener('click', async () => {
        if (!recipeStatus) return;
        
        stopRecipeBtn.disabled = true;
        recipeStatus.style.display = 'block';
        recipeStatus.style.backgroundColor = 'var(--bg-secondary)';
        recipeStatus.style.color = 'var(--text)';
        recipeStatus.textContent = 'Stopping recipe guidance...';
        
        try {
            const response = await fetch(`${API_BASE_URL}/recipe-guidance/stop`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            const data = await response.json();
            
            if (data.status === 'success') {
                recipeStatus.style.backgroundColor = '#d4edda';
                recipeStatus.style.color = '#155724';
                recipeStatus.textContent = `Recipe guidance stopped.`;
                
                // Update UI - show start button, hide stop button
                if (startRecipeBtn) {
                    startRecipeBtn.style.display = 'block';
                    startRecipeBtn.disabled = false;
                }
                if (stopRecipeBtn) {
                    stopRecipeBtn.style.display = 'none';
                    stopRecipeBtn.disabled = false;
                }
                if (recipeSelect) recipeSelect.disabled = false;
            } else {
                recipeStatus.style.backgroundColor = '#f8d7da';
                recipeStatus.style.color = '#721c24';
                recipeStatus.textContent = `Error: ${data.message || 'Failed to stop recipe'}`;
                stopRecipeBtn.disabled = false;
            }
        } catch (error: any) {
            recipeStatus.style.backgroundColor = '#f8d7da';
            recipeStatus.style.color = '#721c24';
            recipeStatus.textContent = `Error: ${error.message || 'Failed to stop recipe'}`;
            stopRecipeBtn.disabled = false;
        }
    });

    // 7. Routine Management (Bathroom)
    const addRoutineBtn = document.getElementById('add-routine-btn');
    const routinesListContainer = document.getElementById('routines-list-container');

    // Load and display routines list (similar to recipes)
    async function loadRoutinesList() {
        if (!routinesListContainer) return;
        
        routinesListContainer.innerHTML = '<p style="color: var(--text-muted);">Loading routines...</p>';
        
        try {
            const response = await fetch(`${API_BASE_URL}/routines`);
            const data = await response.json();
            
            if (data.status === 'success' && data.routines) {
                const routines = data.routines;
                const routineIds = Object.keys(routines);
                
                if (routineIds.length === 0) {
                    routinesListContainer.innerHTML = '<p style="color: var(--text-muted);">No routines yet. Add one above!</p>';
                    return;
                }
                
                let html = '<div style="display: flex; flex-direction: column; gap: 12px;">';
                
                routineIds.forEach(routineId => {
                    const routine = routines[routineId];
                    html += `
                        <div style="border: 1px solid var(--border-color); border-radius: 10px; padding: 16px; background-color: var(--bg-secondary);">
                            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 8px;">
                                <div>
                                    <strong style="font-size: 1.05rem; color: var(--text-main);">${routine.name || routineId}</strong>
                                    ${routine.description ? `<p style="margin: 4px 0 0 0; color: var(--text-muted); font-size: 0.9rem;">${routine.description}</p>` : ''}
                                </div>
                                <span style="color: var(--text-muted); font-size: 0.85rem; white-space: nowrap; margin-left: 12px;">${routine.steps?.length || 0} steps</span>
                            </div>
                            ${routine.steps && routine.steps.length > 0 ? `
                                <details style="margin-top: 8px;">
                                    <summary style="cursor: pointer; color: var(--accent-color); font-size: 0.9rem; user-select: none;">View steps</summary>
                                    <ol style="margin: 12px 0 0 0; padding-left: 20px; color: var(--text-muted); font-size: 0.9rem;">
                                        ${routine.steps.map((step: string) => `<li style="margin-bottom: 6px;">${step}</li>`).join('')}
                                    </ol>
                                </details>
                            ` : ''}
                        </div>
                    `;
                });
                
                html += '</div>';
                routinesListContainer.innerHTML = html;
            } else {
                routinesListContainer.innerHTML = '<p style="color: var(--text-muted);">No routines found.</p>';
            }
        } catch (error: any) {
            const errorMsg = error.message || 'Failed to load routines';
            if (errorMsg.includes('fetch') || errorMsg.includes('network')) {
                routinesListContainer.innerHTML = `<p style="color: #f8d7da;">Cannot load routines. Make sure the API server is running on ${API_BASE_URL}</p>`;
            } else {
                routinesListContainer.innerHTML = `<p style="color: #f8d7da;">Error loading routines: ${errorMsg}</p>`;
            }
        }
    }

    // Add routine button - reuse recipe modal for now (or can create separate routine modal later)
    addRoutineBtn?.addEventListener('click', () => {
        // For now, just show a message - can add routine modal later or reuse recipe modal
        alert('Routine management coming soon! Routines can be added via API or data/routines.json file.');
    });

    // 8. Routine Selection and Guidance (User Bathroom Section)
    const routineSelect = document.getElementById('routine-select') as HTMLSelectElement;
    const startRoutineBtn = document.getElementById('start-routine-btn') as HTMLButtonElement;
    const stopRoutineBtn = document.getElementById('stop-routine-btn') as HTMLButtonElement;
    const routineStatus = document.getElementById('routine-status');

    // Load routines into dropdown (similar to recipes)
    async function loadRoutinesForUser() {
        if (!routineSelect) return;
        
        try {
            const response = await fetch(`${API_BASE_URL}/routines`);
            const data = await response.json();
            
            if (data.status === 'success' && data.routines) {
                // Clear existing options except the first one
                routineSelect.innerHTML = '<option value="">Select a routine...</option>';
                
                // Add routines to dropdown
                Object.keys(data.routines).forEach(routineId => {
                    const routine = data.routines[routineId];
                    const option = document.createElement('option');
                    option.value = routineId;
                    option.textContent = routine.name || routineId;
                    routineSelect.appendChild(option);
                });
            }
        } catch (error: any) {
            console.error('Error loading routines:', error);
        }
    }

    // Enable/disable start button based on selection
    routineSelect?.addEventListener('change', (e) => {
        if (startRoutineBtn) {
            startRoutineBtn.disabled = !(e.target as HTMLSelectElement).value;
        }
    });

    // Start routine guidance
    startRoutineBtn?.addEventListener('click', async () => {
        const selectedRoutineId = routineSelect?.value;
        if (!selectedRoutineId || !routineStatus) return;
        
        startRoutineBtn.disabled = true;
        routineStatus.style.display = 'block';
        routineStatus.style.backgroundColor = 'var(--bg-secondary)';
        routineStatus.style.color = 'var(--text)';
        routineStatus.textContent = 'Starting routine guidance...';
        
        try {
            const response = await fetch(`${API_BASE_URL}/routine-guidance/start`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    routine_id: selectedRoutineId
                })
            });
            
            const data = await response.json();
            
            if (data.status === 'success') {
                routineStatus.style.backgroundColor = '#d4edda';
                routineStatus.style.color = '#155724';
                routineStatus.textContent = `Routine "${data.routine_name}" started! Follow the audio instructions and bring your hand within 100mm of the proximity sensor for next step.`;
                
                // Update UI - show stop button, hide start button
                if (startRoutineBtn) startRoutineBtn.style.display = 'none';
                if (stopRoutineBtn) stopRoutineBtn.style.display = 'block';
                if (routineSelect) routineSelect.disabled = true;
            } else {
                routineStatus.style.backgroundColor = '#f8d7da';
                routineStatus.style.color = '#721c24';
                routineStatus.textContent = `Error: ${data.message || 'Failed to start routine'}`;
                startRoutineBtn.disabled = false;
            }
        } catch (error: any) {
            routineStatus.style.backgroundColor = '#f8d7da';
            routineStatus.style.color = '#721c24';
            const errorMsg = error.message || 'Failed to start routine';
            if (errorMsg.includes('fetch') || errorMsg.includes('network')) {
                routineStatus.textContent = `Error: Cannot connect to API server. Make sure the API server is running on ${API_BASE_URL}`;
            } else {
                routineStatus.textContent = `Error: ${errorMsg}`;
            }
            startRoutineBtn.disabled = false;
        }
    });

    // Stop routine guidance
    stopRoutineBtn?.addEventListener('click', async () => {
        if (!routineStatus) return;
        
        stopRoutineBtn.disabled = true;
        routineStatus.style.display = 'block';
        routineStatus.style.backgroundColor = 'var(--bg-secondary)';
        routineStatus.style.color = 'var(--text)';
        routineStatus.textContent = 'Stopping routine guidance...';
        
        try {
            const response = await fetch(`${API_BASE_URL}/routine-guidance/stop`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            const data = await response.json();
            
            if (data.status === 'success') {
                routineStatus.style.backgroundColor = '#d4edda';
                routineStatus.style.color = '#155724';
                routineStatus.textContent = `Routine guidance stopped.`;
                
                // Update UI - show start button, hide stop button
                if (startRoutineBtn) {
                    startRoutineBtn.style.display = 'block';
                    startRoutineBtn.disabled = false;
                }
                if (stopRoutineBtn) {
                    stopRoutineBtn.style.display = 'none';
                    stopRoutineBtn.disabled = false;
                }
                if (routineSelect) routineSelect.disabled = false;
            } else {
                routineStatus.style.backgroundColor = '#f8d7da';
                routineStatus.style.color = '#721c24';
                routineStatus.textContent = `Error: ${data.message || 'Failed to stop routine'}`;
                stopRoutineBtn.disabled = false;
            }
        } catch (error: any) {
            routineStatus.style.backgroundColor = '#f8d7da';
            routineStatus.style.color = '#721c24';
            routineStatus.textContent = `Error: ${error.message || 'Failed to stop routine'}`;
            stopRoutineBtn.disabled = false;
        }
    });

    // 9. Laundry Routine Selection and Guidance
    // Load laundry routines into dropdown (filter for laundry routines)
    async function loadLaundryRoutinesForUser() {
        if (!laundryRoutineSelect) return;
        
        try {
            const response = await fetch(`${API_BASE_URL}/routines`);
            const data = await response.json();
            
            if (data.status === 'success' && data.routines) {
                // Clear existing options except the first one
                laundryRoutineSelect.innerHTML = '<option value="">Select a wash cycle...</option>';
                
                // Add laundry routines to dropdown (filter by routine_id starting with "laundry_")
                Object.keys(data.routines).forEach(routineId => {
                    if (routineId.startsWith('laundry_')) {
                        const routine = data.routines[routineId];
                        const option = document.createElement('option');
                        option.value = routineId;
                        option.textContent = routine.name || routineId;
                        laundryRoutineSelect.appendChild(option);
                    }
                });
            }
        } catch (error: any) {
            console.error('Error loading laundry routines:', error);
        }
    }

    // Enable/disable start button based on selection
    laundryRoutineSelect?.addEventListener('change', (e) => {
        if (startLaundryRoutineBtn) {
            startLaundryRoutineBtn.disabled = !(e.target as HTMLSelectElement).value;
        }
    });

    // Start laundry routine guidance
    startLaundryRoutineBtn?.addEventListener('click', async () => {
        const selectedRoutineId = laundryRoutineSelect?.value;
        if (!selectedRoutineId || !laundryRoutineStatus) return;
        
        startLaundryRoutineBtn.disabled = true;
        laundryRoutineStatus.style.display = 'block';
        laundryRoutineStatus.style.backgroundColor = 'var(--bg-secondary)';
        laundryRoutineStatus.style.color = 'var(--text)';
        laundryRoutineStatus.textContent = 'Starting wash cycle...';
        
        try {
            const response = await fetch(`${API_BASE_URL}/laundry-routine-guidance/start`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    routine_id: selectedRoutineId
                })
            });
            
            const data = await response.json();
            
            if (data.status === 'success') {
                laundryRoutineStatus.style.backgroundColor = '#d4edda';
                laundryRoutineStatus.style.color = '#155724';
                laundryRoutineStatus.textContent = `Wash cycle "${data.routine_name}" started! Follow the audio instructions and press the pressure sensor for next step.`;
                
                // Update UI - show stop button, hide start button
                if (startLaundryRoutineBtn) startLaundryRoutineBtn.style.display = 'none';
                if (stopLaundryRoutineBtn) stopLaundryRoutineBtn.style.display = 'block';
                if (laundryRoutineSelect) laundryRoutineSelect.disabled = true;
            } else {
                laundryRoutineStatus.style.backgroundColor = '#f8d7da';
                laundryRoutineStatus.style.color = '#721c24';
                laundryRoutineStatus.textContent = `Error: ${data.message || 'Failed to start wash cycle'}`;
                startLaundryRoutineBtn.disabled = false;
            }
        } catch (error: any) {
            laundryRoutineStatus.style.backgroundColor = '#f8d7da';
            laundryRoutineStatus.style.color = '#721c24';
            const errorMsg = error.message || 'Failed to start wash cycle';
            if (errorMsg.includes('fetch') || errorMsg.includes('network')) {
                laundryRoutineStatus.textContent = `Error: Cannot connect to API server. Make sure the API server is running on ${API_BASE_URL}`;
            } else {
                laundryRoutineStatus.textContent = `Error: ${errorMsg}`;
            }
            startLaundryRoutineBtn.disabled = false;
        }
    });

    // Stop laundry routine guidance
    stopLaundryRoutineBtn?.addEventListener('click', async () => {
        if (!laundryRoutineStatus) return;
        
        stopLaundryRoutineBtn.disabled = true;
        laundryRoutineStatus.style.display = 'block';
        laundryRoutineStatus.style.backgroundColor = 'var(--bg-secondary)';
        laundryRoutineStatus.style.color = 'var(--text)';
        laundryRoutineStatus.textContent = 'Stopping wash cycle...';
        
        try {
            const response = await fetch(`${API_BASE_URL}/laundry-routine-guidance/stop`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            const data = await response.json();
            
            if (data.status === 'success') {
                laundryRoutineStatus.style.backgroundColor = '#d4edda';
                laundryRoutineStatus.style.color = '#155724';
                laundryRoutineStatus.textContent = `Wash cycle stopped.`;
                
                // Update UI - show start button, hide stop button
                if (startLaundryRoutineBtn) {
                    startLaundryRoutineBtn.style.display = 'block';
                    startLaundryRoutineBtn.disabled = false;
                }
                if (stopLaundryRoutineBtn) {
                    stopLaundryRoutineBtn.style.display = 'none';
                    stopLaundryRoutineBtn.disabled = false;
                }
                if (laundryRoutineSelect) laundryRoutineSelect.disabled = false;
            } else {
                laundryRoutineStatus.style.backgroundColor = '#f8d7da';
                laundryRoutineStatus.style.color = '#721c24';
                laundryRoutineStatus.textContent = `Error: ${data.message || 'Failed to stop wash cycle'}`;
                stopLaundryRoutineBtn.disabled = false;
            }
        } catch (error: any) {
            laundryRoutineStatus.style.backgroundColor = '#f8d7da';
            laundryRoutineStatus.style.color = '#721c24';
            laundryRoutineStatus.textContent = `Error: ${error.message || 'Failed to stop wash cycle'}`;
            stopLaundryRoutineBtn.disabled = false;
        }
    });

    // 7. Daily Log Generation
    const generateDailyLogBtn = document.getElementById('generate-daily-log-btn') as HTMLButtonElement;
    const dailyLogStatus = document.getElementById('daily-log-status');
    
    generateDailyLogBtn?.addEventListener('click', async () => {
        if (!generateDailyLogBtn || !dailyLogStatus) return;
        
        // Disable button and show loading
        generateDailyLogBtn.disabled = true;
        generateDailyLogBtn.textContent = 'Generating...';
        dailyLogStatus.style.display = 'block';
        dailyLogStatus.style.backgroundColor = 'var(--bg-secondary)';
        dailyLogStatus.style.color = 'var(--text)';
        dailyLogStatus.textContent = 'Generating daily log from last 24 hours...';
        
        try {
            const response = await fetch(`${API_BASE_URL}/daily-log/generate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            const data = await response.json();
            
            if (data.status === 'success' && data.note_created) {
                dailyLogStatus.style.backgroundColor = '#d4edda';
                dailyLogStatus.style.color = '#155724';
                dailyLogStatus.innerHTML = `
                    <strong>Daily log created successfully!</strong><br/>
                    ${data.event_count} events processed.<br/>
                    <a href="https://opennote.com" target="_blank" rel="noopener noreferrer" 
                       style="color: #155724; text-decoration: underline; margin-top: 10px; display: inline-block;">
                        View on OpenNote →
                    </a>
                `;
            } else if (data.status === 'success' && !data.note_created) {
                dailyLogStatus.style.backgroundColor = '#fff3cd';
                dailyLogStatus.style.color = '#856404';
                dailyLogStatus.innerHTML = `<strong>Info: ${data.message}</strong>`;
            } else {
                throw new Error(data.message || 'Failed to generate daily log');
            }
        } catch (error: any) {
            dailyLogStatus.style.backgroundColor = '#f8d7da';
            dailyLogStatus.style.color = '#721c24';
            dailyLogStatus.innerHTML = `<strong>Error:</strong> ${error.message || 'Failed to generate daily log. Make sure the API server is running.'}`;
        } finally {
            generateDailyLogBtn.disabled = false;
            generateDailyLogBtn.textContent = 'Generate Daily Log';
        }
    });

    // 5. Activity Monitor - Fetch and Display Events
    const activityEventList = document.getElementById('activity-event-list');
    let eventRefreshInterval: number | null = null;

    function formatTimeAgo(timestamp: number): string {
        const seconds = Math.floor((Date.now() / 1000) - timestamp);
        if (seconds < 60) return `${seconds} sec${seconds !== 1 ? 's' : ''} ago`;
        const minutes = Math.floor(seconds / 60);
        if (minutes < 60) return `${minutes} min${minutes !== 1 ? 's' : ''} ago`;
        const hours = Math.floor(minutes / 60);
        if (hours < 24) return `${hours} hour${hours !== 1 ? 's' : ''} ago`;
        const days = Math.floor(hours / 24);
        return `${days} day${days !== 1 ? 's' : ''} ago`;
    }

    function formatEventMessage(event: any): string {
        // Format event message based on type
        const timeAgo = formatTimeAgo(event.timestamp);
        
        switch (event.event_type) {
            case 'proximity_warning':
                return `Proximity warning: Hand near loud object (${timeAgo})`;
            case 'heat_warning':
                const temp = event.metadata?.temperature_c?.toFixed(1) || 'unknown';
                return `Stove temperature warning: ${temp}°C (${timeAgo})`;
            case 'heat_warning_critical':
                const critTemp = event.metadata?.temperature_c?.toFixed(1) || 'unknown';
                return `Critical: Stove too hot (${critTemp}°C) (${timeAgo})`;
            case 'decibel_warning':
                const volume = event.metadata?.volume || 'high';
                return `High volume detected (${timeAgo})`;
            case 'laundry_cycle_complete':
                return `${event.message} (${timeAgo})`;
            default:
                return `${event.message} (${timeAgo})`;
        }
    }

    async function fetchActivityEvents(room: string = 'kitchen') {
        if (!activityEventList) {
            console.warn('Activity event list element not found');
            return;
        }

        try {
            const url = `${API_BASE_URL}/events/${room}?limit=10`;
            console.log(`Fetching events from: ${url}`);
            
            const response = await fetch(url);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            
            console.log(`Received ${data.events?.length || 0} events:`, data);
            
            if (data.events && data.events.length > 0) {
                activityEventList.innerHTML = data.events.map((event: any) => {
                    const message = formatEventMessage(event);
                    const severityClass = event.severity === 'critical' ? 'critical' : 
                                         event.severity === 'warning' ? 'warning' : '';
                    return `<li class="${severityClass}">${message}</li>`;
                }).join('');
            } else {
                activityEventList.innerHTML = '<li>No recent events</li>';
            }
        } catch (error: any) {
            console.error('Error fetching events:', error);
            const errorMsg = error.message || 'Unknown error';
            activityEventList.innerHTML = `<li style="color: red;">Unable to load events: ${errorMsg}<br/>Make sure the API server is running on port 5001</li>`;
        }
    }

    function startEventRefresh(room: string = 'kitchen') {
        // Use panel-aware version
        startEventRefreshForPanel(room);
    }

    function stopEventRefresh() {
        if (eventRefreshInterval !== null) {
            clearInterval(eventRefreshInterval);
            eventRefreshInterval = null;
        }
    }

    // Monitor when Activity Monitor panel becomes visible to start/stop refresh
    if (userPanelMonitor) {
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.type === 'attributes' && mutation.attributeName === 'class') {
                    const target = mutation.target as HTMLElement;
                    if (target.classList.contains('visible')) {
                        // Check which room is active
                        const activeRoom = userKitchenBtn?.classList.contains('active') ? 'kitchen' : 'bathroom';
                        startEventRefreshForPanel(activeRoom);
                    } else {
                        stopEventRefresh();
                    }
                }
            });
        });
        observer.observe(userPanelMonitor, { attributes: true, attributeFilter: ['class'] });
    }

    // Monitor when Laundry panel becomes visible to start/stop refresh
    if (userPanelLaundry) {
        const laundryObserver = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.type === 'attributes' && mutation.attributeName === 'class') {
                    const target = mutation.target as HTMLElement;
                    if (target.classList.contains('visible')) {
                        startEventRefreshForPanel('laundry');
                    } else {
                        stopEventRefresh();
                    }
                }
            });
        });
        laundryObserver.observe(userPanelLaundry, { attributes: true, attributeFilter: ['class'] });
    }


    // Track last shown laundry cycle complete event to avoid duplicate popups
    let lastShownLaundryCompleteEventId: string | null = null;
    let popupTimeoutId: number | null = null;
    let isPopupShowing: boolean = false;

    // Function to show laundry cycle complete popup
    function showLaundryCompletePopup(message: string) {
        const popup = document.getElementById('laundry-popup-notification');
        const popupMessage = document.getElementById('laundry-popup-message');
        
        if (!popup || !popupMessage) {
            console.warn('Laundry popup elements not found');
            return;
        }

        // If popup is already showing, don't show it again
        if (isPopupShowing) {
            console.log('Popup already showing, skipping duplicate');
            return;
        }

        // Clear any existing timeout
        if (popupTimeoutId !== null) {
            clearTimeout(popupTimeoutId);
            popupTimeoutId = null;
        }

        // Set message
        popupMessage.textContent = message || 'Your laundry cycle has finished!';
        
        // Show popup (remove hiding class if present)
        popup.classList.remove('hiding');
        popup.style.display = 'block';
        isPopupShowing = true;

        // Hide popup after 6 seconds
        popupTimeoutId = window.setTimeout(() => {
            popup.classList.add('hiding');
            // Remove from DOM after animation completes (300ms)
            setTimeout(() => {
                popup.style.display = 'none';
                popup.classList.remove('hiding');
                isPopupShowing = false;
                popupTimeoutId = null;
            }, 300);
        }, 6000);
    }

    // Panel-aware version of fetchActivityEvents that updates the correct list
    async function fetchActivityEventsForPanel(room: string = 'kitchen') {
        const targetList = (room === 'laundry' && laundryEventList) ? laundryEventList : activityEventList;
        if (!targetList) {
            console.warn('Activity event list element not found');
            return;
        }

        try {
            const url = `${API_BASE_URL}/events/${room}?limit=10`;
            console.log(`Fetching events from: ${url}`);
            
            const response = await fetch(url);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            
            console.log(`Received ${data.events?.length || 0} events:`, data);
            
            if (data.events && data.events.length > 0) {
                // Check for new laundry_cycle_complete event when fetching laundry events
                if (room === 'laundry') {
                    const laundryCompleteEvent = data.events.find((event: any) => 
                        event.event_type === 'laundry_cycle_complete' && 
                        event.id !== lastShownLaundryCompleteEventId
                    );
                    
                    if (laundryCompleteEvent) {
                        lastShownLaundryCompleteEventId = laundryCompleteEvent.id;
                        showLaundryCompletePopup(laundryCompleteEvent.message || 'Laundry cycle completed!');
                    }
                }
                
                targetList.innerHTML = data.events.map((event: any) => {
                    const message = formatEventMessage(event);
                    const severityClass = event.severity === 'critical' ? 'critical' : 
                                         event.severity === 'warning' ? 'warning' : '';
                    return `<li class="${severityClass}">${message}</li>`;
                }).join('');
            } else {
                targetList.innerHTML = '<li>No recent events</li>';
            }
        } catch (error: any) {
            console.error('Error fetching events:', error);
            const errorMsg = error.message || 'Unknown error';
            if (targetList) {
                targetList.innerHTML = `<li style="color: red;">Unable to load events: ${errorMsg}<br/>Make sure the API server is running on port 5001</li>`;
            }
        }
    }

    // Panel-aware version of startEventRefresh
    function startEventRefreshForPanel(room: string = 'kitchen') {
        // Clear existing interval
        if (eventRefreshInterval !== null) {
            clearInterval(eventRefreshInterval);
        }
        // Fetch events immediately
        fetchActivityEventsForPanel(room);
        // Set up periodic refresh (every 5 seconds)
        eventRefreshInterval = window.setInterval(() => {
            fetchActivityEventsForPanel(room);
        }, 5000);
    }
}