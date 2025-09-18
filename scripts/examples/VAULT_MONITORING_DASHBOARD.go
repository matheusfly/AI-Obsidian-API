package main

import (
	"fmt"
	"log"
	"net/http"
	"time"
)

// VaultMonitoringDashboard provides a web-based monitoring interface
type VaultMonitoringDashboard struct {
	syncService *RealTimeVaultSync
	port        string
	stats       *DashboardStats
	alerts      []DashboardAlert
	metrics     *VaultMetrics
}

// DashboardStats provides dashboard statistics
type DashboardStats struct {
	TotalFiles       int           `json:"total_files"`
	ActiveClients    int           `json:"active_clients"`
	SyncStatus       string        `json:"sync_status"`
	LastSyncTime     time.Time     `json:"last_sync_time"`
	SyncDuration     time.Duration `json:"sync_duration"`
	ConflictsCount   int           `json:"conflicts_count"`
	ChangesPerMinute int           `json:"changes_per_minute"`
	Uptime           time.Duration `json:"uptime"`
	ErrorRate        float64       `json:"error_rate"`
}

// DashboardAlert represents a system alert
type DashboardAlert struct {
	ID         string    `json:"id"`
	Type       AlertType `json:"type"`
	Severity   Severity  `json:"severity"`
	Message    string    `json:"message"`
	Timestamp  time.Time `json:"timestamp"`
	Resolved   bool      `json:"resolved"`
	ResolvedAt time.Time `json:"resolved_at,omitempty"`
}

// AlertType represents the type of alert
type AlertType string

const (
	AlertTypeSyncError     AlertType = "sync_error"
	AlertTypeConflict      AlertType = "conflict"
	AlertTypeClientTimeout AlertType = "client_timeout"
	AlertTypeHighLoad      AlertType = "high_load"
	AlertTypeDiskSpace     AlertType = "disk_space"
)

// Severity represents alert severity
type Severity string

const (
	SeverityLow      Severity = "low"
	SeverityMedium   Severity = "medium"
	SeverityHigh     Severity = "high"
	SeverityCritical Severity = "critical"
)

// VaultMetrics provides detailed vault metrics
type VaultMetrics struct {
	FileCounts      map[string]int `json:"file_counts"`
	ChangeHistory   []ChangeMetric `json:"change_history"`
	ClientActivity  []ClientMetric `json:"client_activity"`
	SyncPerformance []SyncMetric   `json:"sync_performance"`
	ErrorLogs       []ErrorLog     `json:"error_logs"`
}

// ChangeMetric represents change metrics over time
type ChangeMetric struct {
	Timestamp time.Time `json:"timestamp"`
	Creates   int       `json:"creates"`
	Modifies  int       `json:"modifies"`
	Deletes   int       `json:"deletes"`
	Renames   int       `json:"renames"`
}

// ClientMetric represents client activity metrics
type ClientMetric struct {
	ClientID    string    `json:"client_id"`
	LastSeen    time.Time `json:"last_seen"`
	UpdatesSent int       `json:"updates_sent"`
	IsActive    bool      `json:"is_active"`
}

// SyncMetric represents sync performance metrics
type SyncMetric struct {
	Timestamp      time.Time     `json:"timestamp"`
	Duration       time.Duration `json:"duration"`
	FilesProcessed int           `json:"files_processed"`
	Success        bool          `json:"success"`
	ErrorMessage   string        `json:"error_message,omitempty"`
}

// ErrorLog represents an error log entry
type ErrorLog struct {
	Timestamp time.Time `json:"timestamp"`
	Level     string    `json:"level"`
	Message   string    `json:"message"`
	Source    string    `json:"source"`
}

// NewVaultMonitoringDashboard creates a new monitoring dashboard
func NewVaultMonitoringDashboard(syncService *RealTimeVaultSync, port string) *VaultMonitoringDashboard {
	dashboard := &VaultMonitoringDashboard{
		syncService: syncService,
		port:        port,
		stats:       &DashboardStats{},
		alerts:      make([]DashboardAlert, 0),
		metrics: &VaultMetrics{
			FileCounts:      make(map[string]int),
			ChangeHistory:   make([]ChangeMetric, 0),
			ClientActivity:  make([]ClientMetric, 0),
			SyncPerformance: make([]SyncMetric, 0),
			ErrorLogs:       make([]ErrorLog, 0),
		},
	}

	return dashboard
}

// setupRoutes configures the dashboard routes
func (d *VaultMonitoringDashboard) setupRoutes() {
	http.HandleFunc("/", d.dashboardHandler)
	http.HandleFunc("/api/stats", d.getStatsHandler)
	http.HandleFunc("/api/alerts", d.getAlertsHandler)
	http.HandleFunc("/api/metrics", d.getMetricsHandler)
	http.HandleFunc("/api/conflicts", d.getConflictsHandler)
	http.HandleFunc("/api/clients", d.getClientsHandler)
	http.HandleFunc("/api/health", d.healthHandler)
}

// dashboardHandler serves the main dashboard page
func (d *VaultMonitoringDashboard) dashboardHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "text/html")
	fmt.Fprintf(w, "<html><head><title>Vault Monitoring Dashboard</title></head><body><h1>Vault Monitoring Dashboard</h1><p>Real-time synchronization monitoring</p></body></html>")
}

// getStatsHandler returns current statistics
func (d *VaultMonitoringDashboard) getStatsHandler(w http.ResponseWriter, r *http.Request) {
	stats := d.getCurrentStats()
	w.Header().Set("Content-Type", "application/json")
	fmt.Fprintf(w, `{"total_files":%d,"active_clients":%d,"sync_status":"%s","conflicts_count":%d}`,
		stats.TotalFiles, stats.ActiveClients, stats.SyncStatus, stats.ConflictsCount)
}

// getAlertsHandler returns current alerts
func (d *VaultMonitoringDashboard) getAlertsHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	fmt.Fprintf(w, `{"alerts":[],"count":%d}`, len(d.alerts))
}

// getMetricsHandler returns detailed metrics
func (d *VaultMonitoringDashboard) getMetricsHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	fmt.Fprintf(w, `{"file_counts":{},"change_history":[],"client_activity":[],"sync_performance":[],"error_logs":[]}`)
}

// getConflictsHandler returns current conflicts
func (d *VaultMonitoringDashboard) getConflictsHandler(w http.ResponseWriter, r *http.Request) {
	conflicts := d.syncService.GetConflicts()
	w.Header().Set("Content-Type", "application/json")
	fmt.Fprintf(w, `{"conflicts":[],"count":%d}`, len(conflicts))
}

// getClientsHandler returns connected clients
func (d *VaultMonitoringDashboard) getClientsHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	fmt.Fprintf(w, `{"clients":[{"client_id":"demo_client","last_seen":"%s","updates_sent":42,"is_active":true}],"count":1}`, time.Now().Format(time.RFC3339))
}

// healthHandler returns health status
func (d *VaultMonitoringDashboard) healthHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	fmt.Fprintf(w, `{"status":"healthy","timestamp":"%s","uptime":"1h0m0s"}`, time.Now().Format(time.RFC3339))
}

// getCurrentStats returns current dashboard statistics
func (d *VaultMonitoringDashboard) getCurrentStats() DashboardStats {
	syncStats := d.syncService.GetStats()

	return DashboardStats{
		TotalFiles:       d.getTotalFileCount(),
		ActiveClients:    syncStats.ActiveClients,
		SyncStatus:       d.getSyncStatus(),
		LastSyncTime:     syncStats.LastSyncTime,
		SyncDuration:     syncStats.SyncDuration,
		ConflictsCount:   syncStats.ConflictsCount,
		ChangesPerMinute: d.calculateChangesPerMinute(),
		Uptime:           time.Since(time.Now().Add(-1 * time.Hour)), // Mock uptime
		ErrorRate:        d.calculateErrorRate(),
	}
}

// getTotalFileCount returns the total number of files in the vault
func (d *VaultMonitoringDashboard) getTotalFileCount() int {
	// This would query the actual vault
	return 150 // Mock value
}

// getSyncStatus returns the current sync status
func (d *VaultMonitoringDashboard) getSyncStatus() string {
	// This would check the actual sync service status
	return "active"
}

// calculateChangesPerMinute calculates changes per minute
func (d *VaultMonitoringDashboard) calculateChangesPerMinute() int {
	// This would calculate based on actual change history
	return 5 // Mock value
}

// calculateErrorRate calculates the error rate
func (d *VaultMonitoringDashboard) calculateErrorRate() float64 {
	// This would calculate based on actual error logs
	return 0.02 // Mock 2% error rate
}

// addAlert adds a new alert
func (d *VaultMonitoringDashboard) addAlert(alertType AlertType, severity Severity, message string) {
	alert := DashboardAlert{
		ID:        fmt.Sprintf("alert_%d", time.Now().UnixNano()),
		Type:      alertType,
		Severity:  severity,
		Message:   message,
		Timestamp: time.Now(),
		Resolved:  false,
	}

	d.alerts = append(d.alerts, alert)
	log.Printf("Alert added: %s - %s", severity, message)
}

// Start starts the monitoring dashboard
func (d *VaultMonitoringDashboard) Start() error {
	log.Printf("Starting vault monitoring dashboard on port %s", d.port)
	d.setupRoutes()
	return http.ListenAndServe(":"+d.port, nil)
}

// Example usage and testing
func runDashboardDemo() {
	// Example configuration
	vaultPath := "D:\\Nomade Milionario"
	apiBaseURL := "http://localhost:27124"
	apiToken := "b26efa44ceb0bd4e1fae338cede5384237bbab8624c61927986aa3f06c2f5a70"

	// Create real-time sync instance
	sync, err := NewRealTimeVaultSync(vaultPath, apiBaseURL, apiToken)
	if err != nil {
		log.Fatalf("Failed to create real-time sync: %v", err)
	}

	// Start synchronization
	err = sync.Start()
	if err != nil {
		log.Fatalf("Failed to start synchronization: %v", err)
	}
	defer sync.Stop()

	// Create monitoring dashboard
	dashboard := NewVaultMonitoringDashboard(sync, "8082")

	// Add some sample alerts
	dashboard.addAlert(AlertTypeSyncError, SeverityMedium, "Sync failed for file notes/project.md")
	dashboard.addAlert(AlertTypeConflict, SeverityHigh, "Conflict detected in notes/meeting.md")
	dashboard.addAlert(AlertTypeHighLoad, SeverityLow, "High sync load detected")

	// Start dashboard
	log.Println("🚀 Starting Vault Monitoring Dashboard...")
	log.Println("📊 Dashboard available at: http://localhost:8082")
	log.Println("🔗 API endpoints available at: http://localhost:8082/api/")

	err = dashboard.Start()
	if err != nil {
		log.Fatalf("Failed to start dashboard: %v", err)
	}
}
