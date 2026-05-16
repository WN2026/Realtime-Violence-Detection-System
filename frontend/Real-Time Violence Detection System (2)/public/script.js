// Global State
let currentUser = null;
let users = [
    {
        id: 1,
        name: 'John Anderson',
        email: 'john.anderson@security.com',
        phone: '+1 (555) 123-4567',
        role: 'Admin',
        status: 'Active',
        lastLogin: '2026-02-03 14:30',
        createdAt: '2025-01-15'
    },
    {
        id: 2,
        name: 'Sarah Miller',
        email: 'sarah.miller@security.com',
        phone: '+1 (555) 234-5678',
        role: 'Operator',
        status: 'Active',
        lastLogin: '2026-02-03 13:45',
        createdAt: '2025-02-20'
    },
    {
        id: 3,
        name: 'Michael Chen',
        email: 'michael.chen@security.com',
        phone: '+1 (555) 345-6789',
        role: 'Operator',
        status: 'Active',
        lastLogin: '2026-02-03 10:15',
        createdAt: '2025-03-10'
    },
    {
        id: 4,
        name: 'Emma Wilson',
        email: 'emma.wilson@security.com',
        phone: '+1 (555) 456-7890',
        role: 'Viewer',
        status: 'Active',
        lastLogin: '2026-02-02 16:20',
        createdAt: '2025-04-05'
    },
    {
        id: 5,
        name: 'David Brown',
        email: 'david.brown@security.com',
        phone: '+1 (555) 567-8901',
        role: 'Viewer',
        status: 'Inactive',
        lastLogin: '2026-01-28 09:30',
        createdAt: '2025-05-12'
    }
];

let incidents = [
    {
        id: 1,
        timestamp: '2026-02-03 14:23:15',
        cameraId: 'CAM-01',
        cameraName: 'Entrance Gate',
        severity: 'High',
        confidence: 94,
        status: 'Active',
        description: 'Aggressive behavior detected'
    },
    {
        id: 2,
        timestamp: '2026-02-03 13:45:22',
        cameraId: 'CAM-05',
        cameraName: 'Parking Lot B',
        severity: 'Medium',
        confidence: 78,
        status: 'Under Review',
        description: 'Suspicious activity observed'
    },
    {
        id: 3,
        timestamp: '2026-02-03 12:10:45',
        cameraId: 'CAM-03',
        cameraName: 'Corridor B',
        severity: 'Low',
        confidence: 65,
        status: 'Resolved',
        description: 'Minor altercation detected'
    },
    {
        id: 4,
        timestamp: '2026-02-03 11:30:18',
        cameraId: 'CAM-02',
        cameraName: 'Parking Lot A',
        severity: 'High',
        confidence: 91,
        status: 'Resolved',
        description: 'Physical confrontation detected'
    },
    {
        id: 5,
        timestamp: '2026-02-03 10:15:33',
        cameraId: 'CAM-06',
        cameraName: 'Reception',
        severity: 'Medium',
        confidence: 72,
        status: 'Resolved',
        description: 'Elevated voice levels detected'
    },
    {
        id: 6,
        timestamp: '2026-02-02 18:45:12',
        cameraId: 'CAM-04',
        cameraName: 'Cafeteria',
        severity: 'Low',
        confidence: 68,
        status: 'Resolved',
        description: 'Crowd gathering observed'
    }
];

let cameras = [
    { id: 1, name: 'Entrance Gate', location: 'Main Entrance', status: 'active', alert: true, confidence: 92 },
    { id: 2, name: 'Parking Lot A', location: 'Parking Area', status: 'active', alert: false, confidence: 0 },
    { id: 3, name: 'Corridor B', location: 'Floor 2', status: 'active', alert: false, confidence: 0 },
    { id: 4, name: 'Cafeteria', location: 'Ground Floor', status: 'active', alert: false, confidence: 0 },
    { id: 5, name: 'Parking Lot B', location: 'Parking Area', status: 'active', alert: true, confidence: 78 },
    { id: 6, name: 'Reception', location: 'Main Lobby', status: 'active', alert: false, confidence: 0 },
    { id: 7, name: 'Stairwell A', location: 'Floor 1-3', status: 'active', alert: false, confidence: 0 },
    { id: 8, name: 'Loading Dock', location: 'Rear Entrance', status: 'active', alert: false, confidence: 0 },
    { id: 9, name: 'Server Room', location: 'Basement', status: 'maintenance', alert: false, confidence: 0 }
];

let editingUserId = null;
let currentCameraFilter = 'all';
let selectedCameraId = null;

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    initializeLoginPage();
    initializeNavigation();
    initializeTime();
    initializeDashboard();
    initializeLiveMonitoring();
    initializeIncidents();
    initializeReports();
    initializeUsers();
});

// Login Page
function initializeLoginPage() {
    const loginForm = document.getElementById('login-form');
    const togglePassword = document.querySelector('.toggle-password');
    const passwordInput = document.getElementById('password');
    const errorMessage = document.getElementById('error-message');

    loginForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;

        if (username && password) {
            currentUser = username;
            document.getElementById('login-page').style.display = 'none';
            document.getElementById('main-app').style.display = 'flex';
        } else {
            errorMessage.textContent = 'Please enter both username and password';
            errorMessage.style.display = 'block';
        }
    });

    togglePassword.addEventListener('click', function() {
        const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
        passwordInput.setAttribute('type', type);
        const icon = this.querySelector('i');
        icon.classList.toggle('fa-eye');
        icon.classList.toggle('fa-eye-slash');
    });
}

// Navigation
function initializeNavigation() {
    const navItems = document.querySelectorAll('.nav-item:not(.logout-btn)');
    const logoutBtn = document.querySelector('.logout-btn');

    navItems.forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            const page = this.dataset.page;
            
            // Update active nav
            navItems.forEach(nav => nav.classList.remove('active'));
            this.classList.add('active');
            
            // Show page
            document.querySelectorAll('.content-page').forEach(p => p.classList.remove('active'));
            document.getElementById(page + '-page').classList.add('active');
        });
    });

    logoutBtn.addEventListener('click', function(e) {
        e.preventDefault();
        document.getElementById('main-app').style.display = 'none';
        document.getElementById('login-page').style.display = 'block';
        document.getElementById('login-form').reset();
        currentUser = null;
    });
}

// Time and Date
function initializeTime() {
    function updateTime() {
        const now = new Date();
        const timeElement = document.getElementById('current-time');
        const dateElement = document.getElementById('current-date');
        
        if (timeElement) {
            timeElement.textContent = now.toLocaleTimeString();
        }
        if (dateElement) {
            dateElement.textContent = now.toLocaleDateString('en-US', {
                weekday: 'long',
                year: 'numeric',
                month: 'long',
                day: 'numeric'
            });
        }
    }
    
    updateTime();
    setInterval(updateTime, 1000);
}

// Dashboard
function initializeDashboard() {
    renderAlerts();
}

function renderAlerts() {
    const container = document.getElementById('alerts-container');
    const activeAlerts = incidents.filter(i => i.status === 'Active' || i.status === 'Under Review').slice(0, 3);
    
    container.innerHTML = activeAlerts.map(alert => `
        <div class="alert-item">
            <div class="alert-header">
                <div class="alert-camera">
                    <span class="status-dot ${alert.status === 'Active' ? 'active' : 'review'}"></span>
                    <span>${alert.cameraName}</span>
                </div>
                <span class="severity-badge severity-${alert.severity.toLowerCase()}">${alert.severity}</span>
            </div>
            <p class="alert-time">${getTimeAgo(alert.timestamp)}</p>
            <div class="confidence-bar">
                <span>Confidence:</span>
                <div class="confidence-progress">
                    <div class="confidence-fill" style="width: ${alert.confidence}%; background: ${getConfidenceColor(alert.confidence)}"></div>
                </div>
                <span>${alert.confidence}%</span>
            </div>
        </div>
    `).join('');
}

function getTimeAgo(timestamp) {
    const now = new Date();
    const then = new Date(timestamp);
    const diff = Math.floor((now - then) / 60000); // minutes
    
    if (diff < 1) return 'Just now';
    if (diff < 60) return `${diff} minutes ago`;
    const hours = Math.floor(diff / 60);
    if (hours < 24) return `${hours} hour${hours > 1 ? 's' : ''} ago`;
    const days = Math.floor(hours / 24);
    return `${days} day${days > 1 ? 's' : ''} ago`;
}

function getConfidenceColor(confidence) {
    if (confidence > 80) return '#ef4444';
    if (confidence > 60) return '#eab308';
    return '#3b82f6';
}

// Live Monitoring
function initializeLiveMonitoring() {
    // Filter select
    const filterSelects = document.querySelectorAll('#live-monitoring-page .control-select');
    if (filterSelects.length > 0) {
        filterSelects[0].addEventListener('change', function(e) {
            currentCameraFilter = e.target.value;
            renderLiveCameras();
        });
    }
    
    renderLiveCameras();
    createCameraModal();
}

function renderLiveCameras() {
    const grid = document.getElementById('live-cameras-grid');
    
    // Filter cameras based on selection
    let filteredCameras = cameras;
    if (currentCameraFilter === 'Alert Only') {
        filteredCameras = cameras.filter(c => c.alert);
    } else if (currentCameraFilter === 'Main Entrance') {
        filteredCameras = cameras.filter(c => c.location.includes('Entrance'));
    } else if (currentCameraFilter === 'Parking Areas') {
        filteredCameras = cameras.filter(c => c.location.includes('Parking'));
    }
    
    grid.innerHTML = filteredCameras.map(camera => `
        <div class="live-camera-card ${camera.alert ? 'alert' : ''}" data-camera-id="${camera.id}">
            <div class="camera-video">
                <div class="feed-placeholder">
                    <i class="fas fa-camera"></i>
                    <p>Camera ${String(camera.id).padStart(2, '0')}</p>
                    <div class="live-indicator">
                        <span class="pulse"></span>
                        <span>LIVE</span>
                    </div>
                </div>
                ${camera.alert ? `
                    <div class="alert-overlay">
                        <div class="alert-banner">
                            <div>
                                <i class="fas fa-exclamation-triangle"></i>
                                VIOLENCE DETECTED
                            </div>
                            <span>${camera.confidence}% Confidence</span>
                        </div>
                    </div>
                ` : ''}
                <div class="camera-status ${camera.status === 'active' ? 'live' : ''}">${camera.status === 'active' ? 'LIVE' : 'OFFLINE'}</div>
            </div>
            <div class="camera-info">
                <h3>${camera.name}</h3>
                <p>${camera.location}</p>
            </div>
        </div>
    `).join('');
    
    // Add click event to each camera card
    const cameraCards = document.querySelectorAll('.live-camera-card');
    cameraCards.forEach(card => {
        card.addEventListener('click', function() {
            const cameraId = parseInt(this.dataset.cameraId);
            openCameraModal(cameraId);
        });
    });
}

function createCameraModal() {
    // Create modal if it doesn't exist
    if (!document.getElementById('camera-modal')) {
        const modal = document.createElement('div');
        modal.id = 'camera-modal';
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-content" style="max-width: 1200px;">
                <div class="camera-video" style="aspect-ratio: 16/9; background: #020617; position: relative;">
                    <div class="feed-placeholder">
                        <i class="fas fa-camera" style="font-size: 96px; color: #334155;"></i>
                        <p id="modal-camera-name" style="font-size: 24px; color: #94a3b8;"></p>
                        <div class="live-indicator" style="margin-top: 20px;">
                            <span class="pulse"></span>
                            <span>LIVE</span>
                        </div>
                    </div>
                    <div id="modal-alert-overlay"></div>
                </div>
                <div style="padding: 1.5rem; border-top: 1px solid #1e293b;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <h3 id="modal-camera-title" style="font-size: 24px; color: white; margin-bottom: 8px;"></h3>
                            <p id="modal-camera-location" style="color: #94a3b8;"></p>
                        </div>
                        <button class="btn-primary" onclick="closeCameraModal()">
                            <i class="fas fa-times"></i> Close
                        </button>
                    </div>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
        
        // Close modal on background click
        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
                closeCameraModal();
            }
        });
    }
}

function openCameraModal(cameraId) {
    const camera = cameras.find(c => c.id === cameraId);
    if (!camera) return;
    
    const modal = document.getElementById('camera-modal');
    document.getElementById('modal-camera-name').textContent = `Camera ${String(camera.id).padStart(2, '0')}`;
    document.getElementById('modal-camera-title').textContent = camera.name;
    document.getElementById('modal-camera-location').textContent = camera.location;
    
    const alertOverlay = document.getElementById('modal-alert-overlay');
    if (camera.alert) {
        alertOverlay.innerHTML = `
            <div class="alert-overlay">
                <div class="alert-banner" style="font-size: 16px; padding: 16px 24px;">
                    <div>
                        <i class="fas fa-exclamation-triangle"></i>
                        VIOLENCE DETECTED
                    </div>
                    <span>${camera.confidence}% Confidence</span>
                </div>
            </div>
        `;
    } else {
        alertOverlay.innerHTML = '';
    }
    
    modal.classList.add('active');
}

function closeCameraModal() {
    const modal = document.getElementById('camera-modal');
    modal.classList.remove('active');
}

// Incidents Page
function initializeIncidents() {
    const searchInput = document.getElementById('incident-search');
    const severityFilter = document.getElementById('filter-severity');
    const statusFilter = document.getElementById('filter-status');
    const sortBy = document.getElementById('sort-by');
    const viewBtns = document.querySelectorAll('.view-btn');

    searchInput.addEventListener('input', renderIncidents);
    severityFilter.addEventListener('change', renderIncidents);
    statusFilter.addEventListener('change', renderIncidents);
    sortBy.addEventListener('change', renderIncidents);

    viewBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            viewBtns.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            
            const view = this.dataset.view;
            if (view === 'table') {
                document.getElementById('incidents-table-view').style.display = 'block';
                document.getElementById('incidents-cards-view').style.display = 'none';
            } else {
                document.getElementById('incidents-table-view').style.display = 'none';
                document.getElementById('incidents-cards-view').style.display = 'grid';
            }
        });
    });

    renderIncidents();
}

function renderIncidents() {
    const searchTerm = document.getElementById('incident-search').value.toLowerCase();
    const severity = document.getElementById('filter-severity').value;
    const status = document.getElementById('filter-status').value;
    const sort = document.getElementById('sort-by').value;

    let filtered = incidents.filter(incident => {
        const matchSearch = incident.cameraName.toLowerCase().includes(searchTerm) ||
                          incident.cameraId.toLowerCase().includes(searchTerm) ||
                          incident.description.toLowerCase().includes(searchTerm);
        const matchSeverity = severity === 'all' || incident.severity.toLowerCase() === severity;
        const matchStatus = status === 'all' || incident.status.toLowerCase().replace(' ', '-') === status;
        
        return matchSearch && matchSeverity && matchStatus;
    });

    // Sort
    if (sort === 'newest') {
        filtered.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
    } else if (sort === 'oldest') {
        filtered.sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
    } else if (sort === 'severity') {
        const order = { High: 3, Medium: 2, Low: 1 };
        filtered.sort((a, b) => order[b.severity] - order[a.severity]);
    }

    document.getElementById('incidents-count').textContent = `Showing ${filtered.length} of ${incidents.length} incidents`;

    renderIncidentsTable(filtered);
    renderIncidentsCards(filtered);
}

function renderIncidentsTable(data) {
    const tbody = document.getElementById('incidents-table-body');
    
    tbody.innerHTML = data.map(incident => `
        <tr>
            <td style="color: #cbd5e1; font-family: monospace;">#${incident.id}</td>
            <td style="color: #cbd5e1; font-size: 14px;">${incident.timestamp}</td>
            <td>
                <div class="table-camera-info">
                    <h4 style="color: white;">${incident.cameraName}</h4>
                    <p>${incident.cameraId}</p>
                </div>
            </td>
            <td>
                <span class="severity-badge severity-${incident.severity.toLowerCase()}">${incident.severity}</span>
            </td>
            <td>
                <div class="confidence-bar">
                    <div class="confidence-progress">
                        <div class="confidence-fill" style="width: ${incident.confidence}%; background: ${getConfidenceColor(incident.confidence)}"></div>
                    </div>
                    <span style="color: white; font-weight: 600;">${incident.confidence}%</span>
                </div>
            </td>
            <td>
                <span class="severity-badge status-${incident.status.toLowerCase().replace(' ', '-')}">${incident.status}</span>
            </td>
            <td style="color: #cbd5e1;">${incident.description}</td>
            <td>
                <div class="table-actions">
                    <button class="action-btn">
                        <i class="fas fa-eye" style="color: #94a3b8;"></i>
                    </button>
                </div>
            </td>
        </tr>
    `).join('');
}

function renderIncidentsCards(data) {
    const container = document.getElementById('incidents-cards-view');
    
    container.innerHTML = data.map(incident => `
        <div class="incident-card">
            <div class="incident-preview">
                <i class="fas fa-camera"></i>
                <div class="preview-badges">
                    <span class="severity-badge severity-${incident.severity.toLowerCase()}">${incident.severity}</span>
                    <span class="confidence-badge">${incident.confidence}%</span>
                </div>
            </div>
            <div class="incident-content">
                <div class="incident-header">
                    <div class="incident-camera">
                        <h3>${incident.cameraName}</h3>
                        <p>${incident.cameraId}</p>
                    </div>
                    <span class="severity-badge status-${incident.status.toLowerCase().replace(' ', '-')}">${incident.status}</span>
                </div>
                <p class="incident-description">${incident.description}</p>
                <div class="incident-time">
                    <i class="fas fa-calendar"></i>
                    <span>${incident.timestamp}</span>
                </div>
                <button class="btn-view">
                    <i class="fas fa-eye"></i>
                    View Details
                </button>
            </div>
        </div>
    `).join('');
}

// Reports Page
function initializeReports() {
    createDailyChart();
    createSeverityChart();
    createHourlyChart();
    createCameraChart();
}

function createDailyChart() {
    const ctx = document.getElementById('dailyChart');
    if (!ctx) return;
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            datasets: [
                {
                    label: 'High',
                    data: [1, 2, 1, 3, 2, 0, 0],
                    backgroundColor: '#ef4444'
                },
                {
                    label: 'Medium',
                    data: [2, 3, 1, 3, 2, 1, 0],
                    backgroundColor: '#eab308'
                },
                {
                    label: 'Low',
                    data: [1, 2, 1, 2, 1, 1, 1],
                    backgroundColor: '#3b82f6'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                x: { 
                    stacked: true,
                    grid: { color: '#334155' },
                    ticks: { color: '#94a3b8' }
                },
                y: { 
                    stacked: true,
                    grid: { color: '#334155' },
                    ticks: { color: '#94a3b8' }
                }
            },
            plugins: {
                legend: {
                    labels: { color: '#f1f5f9' }
                }
            }
        }
    });
}

function createSeverityChart() {
    const ctx = document.getElementById('severityChart');
    if (!ctx) return;
    
    new Chart(ctx, {
        type: 'pie',
        data: {
            labels: ['High', 'Medium', 'Low'],
            datasets: [{
                data: [12, 18, 10],
                backgroundColor: ['#ef4444', '#eab308', '#3b82f6']
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { color: '#f1f5f9' }
                }
            }
        }
    });
}

function createHourlyChart() {
    const ctx = document.getElementById('hourlyChart');
    if (!ctx) return;
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['00:00', '03:00', '06:00', '09:00', '12:00', '15:00', '18:00', '21:00'],
            datasets: [{
                label: 'Incidents',
                data: [1, 0, 2, 5, 8, 6, 4, 3],
                borderColor: '#ef4444',
                backgroundColor: 'rgba(239, 68, 68, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                x: { 
                    grid: { color: '#334155' },
                    ticks: { color: '#94a3b8' }
                },
                y: { 
                    grid: { color: '#334155' },
                    ticks: { color: '#94a3b8' }
                }
            },
            plugins: {
                legend: {
                    labels: { color: '#f1f5f9' }
                }
            }
        }
    });
}

function createCameraChart() {
    const ctx = document.getElementById('cameraChart');
    if (!ctx) return;
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['CAM-01', 'CAM-02', 'CAM-03', 'CAM-04', 'CAM-05', 'CAM-06'],
            datasets: [{
                label: 'Incidents',
                data: [15, 12, 8, 6, 10, 5],
                backgroundColor: '#ef4444'
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                x: { 
                    grid: { color: '#334155' },
                    ticks: { color: '#94a3b8' }
                },
                y: { 
                    grid: { color: '#334155' },
                    ticks: { color: '#94a3b8' }
                }
            },
            plugins: {
                legend: {
                    labels: { color: '#f1f5f9' }
                }
            }
        }
    });
}

// Users Page
function initializeUsers() {
    const addUserBtn = document.getElementById('add-user-btn');
    const userSearch = document.getElementById('user-search');
    const modal = document.getElementById('user-modal');
    const cancelBtn = document.getElementById('cancel-user-btn');
    const saveBtn = document.getElementById('save-user-btn');
    const userForm = document.getElementById('user-form');

    addUserBtn.addEventListener('click', () => {
        editingUserId = null;
        document.getElementById('modal-title').textContent = 'Add New User';
        userForm.reset();
        modal.classList.add('active');
    });

    cancelBtn.addEventListener('click', () => {
        modal.classList.remove('active');
        editingUserId = null;
    });

    saveBtn.addEventListener('click', saveUser);
    userSearch.addEventListener('input', renderUsers);

    // Close modal on background click
    modal.addEventListener('click', function(e) {
        if (e.target === modal) {
            modal.classList.remove('active');
            editingUserId = null;
        }
    });

    renderUsers();
    updateUserStats();
}

function renderUsers() {
    const searchTerm = document.getElementById('user-search').value.toLowerCase();
    const filtered = users.filter(user => 
        user.name.toLowerCase().includes(searchTerm) ||
        user.email.toLowerCase().includes(searchTerm) ||
        user.role.toLowerCase().includes(searchTerm)
    );

    const tbody = document.getElementById('users-table-body');
    tbody.innerHTML = filtered.map(user => `
        <tr>
            <td>
                <div style="display: flex; align-items: center; gap: 12px;">
                    <div class="user-avatar">
                        <i class="fas fa-user"></i>
                    </div>
                    <div class="user-info">
                        <h4 style="color: white;">${user.name}</h4>
                        <p>${user.email}</p>
                    </div>
                </div>
            </td>
            <td>
                <div class="contact-info">
                    <div class="contact-item">
                        <i class="fas fa-envelope"></i>
                        <span>${user.email}</span>
                    </div>
                    <div class="contact-item">
                        <i class="fas fa-phone"></i>
                        <span>${user.phone}</span>
                    </div>
                </div>
            </td>
            <td>
                <span class="severity-badge role-${user.role.toLowerCase()}">${user.role}</span>
            </td>
            <td>
                <span class="severity-badge status-${user.status.toLowerCase()}">${user.status}</span>
            </td>
            <td style="color: #cbd5e1; font-size: 14px;">${user.lastLogin}</td>
            <td style="color: #cbd5e1; font-size: 14px;">${user.createdAt}</td>
            <td>
                <div class="table-actions">
                    <button class="action-btn" onclick="editUser(${user.id})">
                        <i class="fas fa-edit" style="color: #3b82f6;"></i>
                    </button>
                    <button class="action-btn" onclick="deleteUser(${user.id})">
                        <i class="fas fa-trash" style="color: #ef4444;"></i>
                    </button>
                </div>
            </td>
        </tr>
    `).join('');
}

function updateUserStats() {
    document.getElementById('total-users').textContent = users.length;
    document.getElementById('active-users').textContent = users.filter(u => u.status === 'Active').length;
    document.getElementById('admin-users').textContent = users.filter(u => u.role === 'Admin').length;
}

function editUser(userId) {
    const user = users.find(u => u.id === userId);
    if (!user) return;

    editingUserId = userId;
    document.getElementById('modal-title').textContent = 'Edit User';
    document.getElementById('user-name').value = user.name;
    document.getElementById('user-email').value = user.email;
    document.getElementById('user-phone').value = user.phone;
    document.getElementById('user-role').value = user.role;
    document.getElementById('user-status').value = user.status;
    document.getElementById('user-modal').classList.add('active');
}

function deleteUser(userId) {
    if (!confirm('Are you sure you want to delete this user?')) return;
    
    users = users.filter(u => u.id !== userId);
    renderUsers();
    updateUserStats();
}

function saveUser() {
    const name = document.getElementById('user-name').value;
    const email = document.getElementById('user-email').value;
    const phone = document.getElementById('user-phone').value;
    const role = document.getElementById('user-role').value;
    const status = document.getElementById('user-status').value;

    if (!name || !email || !phone) {
        alert('Please fill in all required fields');
        return;
    }

    if (editingUserId) {
        // Update existing user
        const index = users.findIndex(u => u.id === editingUserId);
        if (index !== -1) {
            users[index] = {
                ...users[index],
                name,
                email,
                phone,
                role,
                status
            };
        }
    } else {
        // Add new user
        const newUser = {
            id: Math.max(...users.map(u => u.id)) + 1,
            name,
            email,
            phone,
            role,
            status,
            lastLogin: 'Never',
            createdAt: new Date().toISOString().split('T')[0]
        };
        users.push(newUser);
    }

    document.getElementById('user-modal').classList.remove('active');
    editingUserId = null;
    renderUsers();
    updateUserStats();
}

// ══════════════════════════════════════════════════════════════
//  REAL-TIME ALERTS via WebSocket (alerts_manager → frontend)
// ══════════════════════════════════════════════════════════════

const WS_URL = 'ws://localhost:8765';
let ws = null;
let wsReconnectTimer = null;

function connectWebSocket() {
    if (ws && ws.readyState === WebSocket.OPEN) return;

    ws = new WebSocket(WS_URL);

    ws.onopen = () => {
        console.log('WebSocket connected');
        updateWsStatus(true);
        if (wsReconnectTimer) { clearTimeout(wsReconnectTimer); wsReconnectTimer = null; }
    };

    ws.onclose = () => {
        updateWsStatus(false);
        wsReconnectTimer = setTimeout(connectWebSocket, 4000);
    };

    ws.onerror = () => updateWsStatus(false);

    ws.onmessage = (event) => {
        try {
            const data = JSON.parse(event.data);
            if (data.type === 'VIOLENCE_ALERT') handleLiveAlert(data);
        } catch (e) { console.error('WS parse error', e); }
    };
}

function updateWsStatus(connected) {
    const dot  = document.getElementById('ws-status-dot');
    const text = document.getElementById('ws-status-text');
    if (!dot || !text) return;
    dot.style.background  = connected ? '#22c55e' : '#ef4444';
    text.textContent      = connected ? 'Live' : 'Reconnecting…';
}

function handleLiveAlert(data) {
    // 1. Add to incidents array
    const newIncident = {
        id:          incidents.length + 1,
        timestamp:   data.timestamp,
        cameraId:    data.camera,
        cameraName:  data.camera,
        severity:    capitalize(data.severity),
        confidence:  Math.round(data.score * 100),
        status:      'Active',
        description: `Weapon detected: ${data.weapon}`
    };
    incidents.unshift(newIncident);

    // 2. Re-render affected sections
    renderAlerts();
    renderIncidents();
    updateDashboardCounts();
    showToast(data);
}

function capitalize(str) {
    if (!str) return '';
    return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
}

function updateDashboardCounts() {
    const todayStr = new Date().toISOString().split('T')[0];
    const todayCount = incidents.filter(i => i.timestamp.startsWith(todayStr)).length;

    const totalEl = document.querySelector('.stat-card:nth-child(2) .stat-value');
    if (totalEl) totalEl.textContent = todayCount;

    const highCount   = incidents.filter(i => i.severity === 'High').length;
    const medCount    = incidents.filter(i => i.severity === 'Medium').length;
    const lowCount    = incidents.filter(i => i.severity === 'Low').length;

    const summaryVals = document.querySelectorAll('.summary-value');
    if (summaryVals[0]) summaryVals[0].textContent = highCount;
    if (summaryVals[1]) summaryVals[1].textContent = medCount;
    if (summaryVals[2]) summaryVals[2].textContent = lowCount;

    // Badge in alerts panel
    const badge = document.querySelector('.alerts-header .badge-red');
    const activeCount = incidents.filter(i => i.status === 'Active').length;
    if (badge) badge.textContent = `${activeCount} Active`;
}

// Toast notification
function showToast(data) {
    let toast = document.getElementById('alert-toast');
    if (!toast) {
        toast = document.createElement('div');
        toast.id = 'alert-toast';
        toast.style.cssText = `
            position: fixed; top: 24px; right: 24px; z-index: 9999;
            background: #1e293b; border: 1px solid #ef4444;
            border-left: 4px solid #ef4444; border-radius: 10px;
            padding: 16px 20px; min-width: 320px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.4);
            transform: translateX(120%); transition: transform 0.35s ease;
        `;
        document.body.appendChild(toast);
    }

    const color = data.severity === 'HIGH' ? '#ef4444' : '#eab308';
    toast.style.borderColor = color;
    toast.style.borderLeftColor = color;
    toast.innerHTML = `
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px">
            <i class="fas fa-exclamation-triangle" style="color:${color};font-size:18px"></i>
            <strong style="color:white;font-size:15px">Violence Alert [${data.severity}]</strong>
        </div>
        <p style="color:#94a3b8;font-size:13px;margin:0 0 4px">Camera: ${data.camera}</p>
        <p style="color:#94a3b8;font-size:13px;margin:0 0 4px">Weapon: ${data.weapon} &nbsp;|&nbsp; Score: ${(data.score*100).toFixed(0)}%</p>
        <p style="color:#64748b;font-size:12px;margin:0">${data.timestamp}</p>
    `;

    // Slide in
    setTimeout(() => toast.style.transform = 'translateX(0)', 10);
    // Slide out after 6s
    setTimeout(() => toast.style.transform = 'translateX(120%)', 6000);
}

// Add WS status indicator to sidebar header
function addWsStatusBar() {
    const sidebarHeader = document.querySelector('.sidebar-header');
    if (!sidebarHeader || document.getElementById('ws-status-dot')) return;
    const bar = document.createElement('div');
    bar.style.cssText = 'display:flex;align-items:center;gap:6px;margin-top:8px;font-size:12px;color:#94a3b8';
    bar.innerHTML = `
        <span id="ws-status-dot" style="width:8px;height:8px;border-radius:50%;background:#ef4444;display:inline-block"></span>
        <span id="ws-status-text">Connecting…</span>
    `;
    sidebarHeader.appendChild(bar);
}

// Start WebSocket after login
const origLogin = document.getElementById('login-form');
if (origLogin) {
    origLogin.addEventListener('submit', () => {
        setTimeout(() => {
            addWsStatusBar();
            connectWebSocket();
        }, 300);
    });
}
function doLogin() {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const errorMessage = document.getElementById('error-message');

    if (username && password) {
        currentUser = username;
        document.getElementById('login-page').style.display = 'none';
        document.getElementById('main-app').style.display = 'flex';
        setTimeout(() => {
            addWsStatusBar();
            connectWebSocket();
        }, 300);
    } else {
        errorMessage.textContent = 'Please enter both username and password';
        errorMessage.style.display = 'block';
    }
}

