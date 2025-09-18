package main

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"path/filepath"
	"strings"
	"sync"
	"time"
)

// RealTimeVaultSync provides real-time synchronization and monitoring
type RealTimeVaultSync struct {
	vaultPath     string
	apiBaseURL    string
	apiToken      string
	clients       map[string]*SyncClient
	clientsMutex  sync.RWMutex
	changeBuffer  chan VaultChange
	bufferMutex   sync.Mutex
	lastSyncTime  time.Time
	syncInterval  time.Duration
	isRunning     bool
	stopChan      chan bool
	conflictQueue []ConflictResolution
	conflictMutex sync.Mutex
}

// SyncClient represents a connected client for real-time updates
type SyncClient struct {
	ID            string
	LastSeen      time.Time
	Subscriptions []string
	UpdateChan    chan VaultChange
	IsActive      bool
}

// VaultChange represents a change in the vault
type VaultChange struct {
	Type      ChangeType             `json:"type"`
	Path      string                 `json:"path"`
	Timestamp time.Time              `json:"timestamp"`
	Content   string                 `json:"content,omitempty"`
	Metadata  map[string]interface{} `json:"metadata,omitempty"`
	ClientID  string                 `json:"client_id,omitempty"`
}

// ChangeType represents the type of change
type ChangeType string

const (
	ChangeTypeCreate ChangeType = "create"
	ChangeTypeModify ChangeType = "modify"
	ChangeTypeDelete ChangeType = "delete"
	ChangeTypeRename ChangeType = "rename"
	ChangeTypeMove   ChangeType = "move"
)

// ConflictResolution represents a conflict that needs resolution
type ConflictResolution struct {
	ID           string         `json:"id"`
	Path         string         `json:"path"`
	LocalChange  VaultChange    `json:"local_change"`
	RemoteChange VaultChange    `json:"remote_change"`
	Timestamp    time.Time      `json:"timestamp"`
	Status       ConflictStatus `json:"status"`
	Resolution   string         `json:"resolution,omitempty"`
}

// ConflictStatus represents the status of a conflict
type ConflictStatus string

const (
	ConflictStatusPending  ConflictStatus = "pending"
	ConflictStatusResolved ConflictStatus = "resolved"
	ConflictStatusIgnored  ConflictStatus = "ignored"
)

// SyncStats provides synchronization statistics
type SyncStats struct {
	TotalChanges    int           `json:"total_changes"`
	SuccessfulSyncs int           `json:"successful_syncs"`
	FailedSyncs     int           `json:"failed_syncs"`
	ActiveClients   int           `json:"active_clients"`
	LastSyncTime    time.Time     `json:"last_sync_time"`
	SyncDuration    time.Duration `json:"sync_duration"`
	ConflictsCount  int           `json:"conflicts_count"`
}

// NewRealTimeVaultSync creates a new real-time vault synchronization instance
func NewRealTimeVaultSync(vaultPath, apiBaseURL, apiToken string) (*RealTimeVaultSync, error) {
	return &RealTimeVaultSync{
		vaultPath:     vaultPath,
		apiBaseURL:    apiBaseURL,
		apiToken:      apiToken,
		clients:       make(map[string]*SyncClient),
		changeBuffer:  make(chan VaultChange, 1000),
		syncInterval:  5 * time.Second,
		stopChan:      make(chan bool),
		conflictQueue: make([]ConflictResolution, 0),
	}, nil
}

// Start begins the real-time synchronization
func (r *RealTimeVaultSync) Start() error {
	if r.isRunning {
		return fmt.Errorf("synchronization is already running")
	}

	r.isRunning = true

	// Start goroutines for different sync operations
	go r.watchFileChanges()
	go r.processChangeBuffer()
	go r.syncWithRemote()
	go r.handleConflicts()
	go r.cleanupInactiveClients()

	log.Println("Real-time vault synchronization started")
	return nil
}

// Stop stops the real-time synchronization
func (r *RealTimeVaultSync) Stop() error {
	if !r.isRunning {
		return fmt.Errorf("synchronization is not running")
	}

	r.isRunning = false
	r.stopChan <- true

	log.Println("Real-time vault synchronization stopped")
	return nil
}

// RegisterClient registers a new client for real-time updates
func (r *RealTimeVaultSync) RegisterClient(clientID string, subscriptions []string) *SyncClient {
	r.clientsMutex.Lock()
	defer r.clientsMutex.Unlock()

	client := &SyncClient{
		ID:            clientID,
		LastSeen:      time.Now(),
		Subscriptions: subscriptions,
		UpdateChan:    make(chan VaultChange, 100),
		IsActive:      true,
	}

	r.clients[clientID] = client
	log.Printf("Client %s registered with subscriptions: %v", clientID, subscriptions)
	return client
}

// UnregisterClient removes a client from real-time updates
func (r *RealTimeVaultSync) UnregisterClient(clientID string) {
	r.clientsMutex.Lock()
	defer r.clientsMutex.Unlock()

	if client, exists := r.clients[clientID]; exists {
		close(client.UpdateChan)
		delete(r.clients, clientID)
		log.Printf("Client %s unregistered", clientID)
	}
}

// GetClient returns a client by ID
func (r *RealTimeVaultSync) GetClient(clientID string) (*SyncClient, bool) {
	r.clientsMutex.RLock()
	defer r.clientsMutex.RUnlock()

	client, exists := r.clients[clientID]
	return client, exists
}

// UpdateClientLastSeen updates the last seen time for a client
func (r *RealTimeVaultSync) UpdateClientLastSeen(clientID string) {
	r.clientsMutex.Lock()
	defer r.clientsMutex.Unlock()

	if client, exists := r.clients[clientID]; exists {
		client.LastSeen = time.Now()
	}
}

// watchFileChanges monitors file system changes (simplified polling-based approach)
func (r *RealTimeVaultSync) watchFileChanges() {
	ticker := time.NewTicker(2 * time.Second)
	defer ticker.Stop()

	lastModTimes := make(map[string]time.Time)

	// Initialize with current file mod times
	r.scanFiles(lastModTimes)

	for {
		select {
		case <-ticker.C:
			r.scanFiles(lastModTimes)
		case <-r.stopChan:
			return
		}
	}
}

// scanFiles scans files for changes
func (r *RealTimeVaultSync) scanFiles(lastModTimes map[string]time.Time) {
	filepath.Walk(r.vaultPath, func(path string, info os.FileInfo, err error) error {
		if err != nil {
			return err
		}

		if info.IsDir() || !strings.HasSuffix(path, ".md") {
			return nil
		}

		relPath, err := filepath.Rel(r.vaultPath, path)
		if err != nil {
			return err
		}

		currentModTime := info.ModTime()
		if lastModTime, exists := lastModTimes[relPath]; exists {
			if currentModTime.After(lastModTime) {
				// File was modified
				change := &VaultChange{
					Type:      ChangeTypeModify,
					Path:      relPath,
					Timestamp: time.Now(),
					Metadata: map[string]interface{}{
						"absolute_path": path,
						"operation":     "modify",
					},
				}
				r.changeBuffer <- *change
			}
		} else {
			// New file
			change := &VaultChange{
				Type:      ChangeTypeCreate,
				Path:      relPath,
				Timestamp: time.Now(),
				Metadata: map[string]interface{}{
					"absolute_path": path,
					"operation":     "create",
				},
			}
			r.changeBuffer <- *change
		}

		lastModTimes[relPath] = currentModTime
		return nil
	})
}

// processChangeBuffer processes buffered changes
func (r *RealTimeVaultSync) processChangeBuffer() {
	for {
		select {
		case change := <-r.changeBuffer:
			r.broadcastChange(change)
			r.detectConflicts(change)

		case <-r.stopChan:
			return
		}
	}
}

// broadcastChange broadcasts a change to all subscribed clients
func (r *RealTimeVaultSync) broadcastChange(change VaultChange) {
	r.clientsMutex.RLock()
	defer r.clientsMutex.RUnlock()

	for _, client := range r.clients {
		if !client.IsActive {
			continue
		}

		// Check if client is subscribed to this change
		if r.isClientSubscribed(client, change) {
			select {
			case client.UpdateChan <- change:
			default:
				log.Printf("Warning: Failed to send update to client %s (channel full)", client.ID)
			}
		}
	}
}

// isClientSubscribed checks if a client is subscribed to a change
func (r *RealTimeVaultSync) isClientSubscribed(client *SyncClient, change VaultChange) bool {
	if len(client.Subscriptions) == 0 {
		return true // Subscribe to all if no specific subscriptions
	}

	for _, subscription := range client.Subscriptions {
		if strings.Contains(change.Path, subscription) {
			return true
		}
	}

	return false
}

// detectConflicts detects potential conflicts
func (r *RealTimeVaultSync) detectConflicts(change VaultChange) {
	// Check if there's a recent change to the same file from a different source
	r.conflictMutex.Lock()
	defer r.conflictMutex.Unlock()

	// Simple conflict detection - in a real implementation, this would be more sophisticated
	for _, existingConflict := range r.conflictQueue {
		if existingConflict.Path == change.Path && existingConflict.Status == ConflictStatusPending {
			// Conflict already exists for this file
			return
		}
	}

	// For now, we'll create a mock conflict for demonstration
	if change.Type == ChangeTypeModify && len(change.Content) > 0 {
		conflict := ConflictResolution{
			ID:          fmt.Sprintf("conflict_%d", time.Now().UnixNano()),
			Path:        change.Path,
			LocalChange: change,
			RemoteChange: VaultChange{
				Type:      ChangeTypeModify,
				Path:      change.Path,
				Timestamp: change.Timestamp.Add(-1 * time.Minute),
				Content:   "Remote content that conflicts",
				ClientID:  "remote_client",
			},
			Timestamp: time.Now(),
			Status:    ConflictStatusPending,
		}

		r.conflictQueue = append(r.conflictQueue, conflict)
		log.Printf("Conflict detected for file: %s", change.Path)
	}
}

// syncWithRemote synchronizes changes with the remote Obsidian API
func (r *RealTimeVaultSync) syncWithRemote() {
	ticker := time.NewTicker(r.syncInterval)
	defer ticker.Stop()

	for {
		select {
		case <-ticker.C:
			if err := r.performSync(); err != nil {
				log.Printf("Sync error: %v", err)
			}

		case <-r.stopChan:
			return
		}
	}
}

// performSync performs the actual synchronization
func (r *RealTimeVaultSync) performSync() error {
	startTime := time.Now()

	// Get list of files from remote API
	remoteFiles, err := r.getRemoteFiles()
	if err != nil {
		return fmt.Errorf("failed to get remote files: %w", err)
	}

	// Compare with local files
	localFiles, err := r.getLocalFiles()
	if err != nil {
		return fmt.Errorf("failed to get local files: %w", err)
	}

	// Detect differences and sync
	changes := r.detectDifferences(localFiles, remoteFiles)
	for _, change := range changes {
		if err := r.applyChange(change); err != nil {
			log.Printf("Failed to apply change %s: %v", change.Path, err)
		}
	}

	r.lastSyncTime = time.Now()
	log.Printf("Sync completed in %v, processed %d changes", time.Since(startTime), len(changes))
	return nil
}

// getRemoteFiles gets the list of files from the remote API
func (r *RealTimeVaultSync) getRemoteFiles() (map[string]VaultFileInfo, error) {
	client := &http.Client{Timeout: 30 * time.Second}
	req, err := http.NewRequest("GET", r.apiBaseURL+"/vault/", nil)
	if err != nil {
		return nil, err
	}

	req.Header.Set("Authorization", "Bearer "+r.apiToken)
	resp, err := client.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("API request failed with status: %d", resp.StatusCode)
	}

	var result struct {
		Data []struct {
			Name string `json:"name"`
			Path string `json:"path"`
		} `json:"data"`
	}

	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return nil, err
	}

	files := make(map[string]VaultFileInfo)
	for _, file := range result.Data {
		files[file.Path] = VaultFileInfo{
			Path: file.Path,
			Name: file.Name,
		}
	}

	return files, nil
}

// getLocalFiles gets the list of local files
func (r *RealTimeVaultSync) getLocalFiles() (map[string]VaultFileInfo, error) {
	files := make(map[string]VaultFileInfo)

	err := filepath.Walk(r.vaultPath, func(path string, info os.FileInfo, err error) error {
		if err != nil {
			return err
		}

		if !info.IsDir() && strings.HasSuffix(path, ".md") {
			relPath, err := filepath.Rel(r.vaultPath, path)
			if err != nil {
				return err
			}

			files[relPath] = VaultFileInfo{
				Path:    relPath,
				Name:    info.Name(),
				Size:    info.Size(),
				ModTime: info.ModTime(),
			}
		}

		return nil
	})

	return files, err
}

// VaultFileInfo represents file information
type VaultFileInfo struct {
	Path    string    `json:"path"`
	Name    string    `json:"name"`
	Size    int64     `json:"size,omitempty"`
	ModTime time.Time `json:"mod_time,omitempty"`
}

// detectDifferences detects differences between local and remote files
func (r *RealTimeVaultSync) detectDifferences(localFiles, remoteFiles map[string]VaultFileInfo) []VaultChange {
	var changes []VaultChange

	// Check for files that exist locally but not remotely
	for path, localFile := range localFiles {
		if _, exists := remoteFiles[path]; !exists {
			changes = append(changes, VaultChange{
				Type:      ChangeTypeCreate,
				Path:      path,
				Timestamp: time.Now(),
				Metadata: map[string]interface{}{
					"action": "upload_to_remote",
					"size":   localFile.Size,
				},
			})
		}
	}

	// Check for files that exist remotely but not locally
	for path, remoteFile := range remoteFiles {
		if _, exists := localFiles[path]; !exists {
			changes = append(changes, VaultChange{
				Type:      ChangeTypeCreate,
				Path:      path,
				Timestamp: time.Now(),
				Metadata: map[string]interface{}{
					"action": "download_from_remote",
					"name":   remoteFile.Name,
				},
			})
		}
	}

	return changes
}

// applyChange applies a change to the vault
func (r *RealTimeVaultSync) applyChange(change VaultChange) error {
	switch change.Metadata["action"] {
	case "upload_to_remote":
		return r.uploadFileToRemote(change.Path)
	case "download_from_remote":
		return r.downloadFileFromRemote(change.Path)
	default:
		return fmt.Errorf("unknown action: %v", change.Metadata["action"])
	}
}

// uploadFileToRemote uploads a file to the remote API
func (r *RealTimeVaultSync) uploadFileToRemote(filePath string) error {
	localPath := filepath.Join(r.vaultPath, filePath)
	content, err := ioutil.ReadFile(localPath)
	if err != nil {
		return err
	}

	client := &http.Client{Timeout: 30 * time.Second}
	req, err := http.NewRequest("POST", r.apiBaseURL+"/vault/"+filePath, strings.NewReader(string(content)))
	if err != nil {
		return err
	}

	req.Header.Set("Authorization", "Bearer "+r.apiToken)
	req.Header.Set("Content-Type", "text/markdown")

	resp, err := client.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK && resp.StatusCode != http.StatusCreated {
		return fmt.Errorf("upload failed with status: %d", resp.StatusCode)
	}

	log.Printf("Uploaded file: %s", filePath)
	return nil
}

// downloadFileFromRemote downloads a file from the remote API
func (r *RealTimeVaultSync) downloadFileFromRemote(filePath string) error {
	client := &http.Client{Timeout: 30 * time.Second}
	req, err := http.NewRequest("GET", r.apiBaseURL+"/vault/"+filePath, nil)
	if err != nil {
		return err
	}

	req.Header.Set("Authorization", "Bearer "+r.apiToken)
	resp, err := client.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("download failed with status: %d", resp.StatusCode)
	}

	content, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		return err
	}

	localPath := filepath.Join(r.vaultPath, filePath)
	err = os.MkdirAll(filepath.Dir(localPath), 0755)
	if err != nil {
		return err
	}

	err = ioutil.WriteFile(localPath, content, 0644)
	if err != nil {
		return err
	}

	log.Printf("Downloaded file: %s", filePath)
	return nil
}

// handleConflicts handles conflict resolution
func (r *RealTimeVaultSync) handleConflicts() {
	ticker := time.NewTicker(10 * time.Second)
	defer ticker.Stop()

	for {
		select {
		case <-ticker.C:
			r.processConflicts()

		case <-r.stopChan:
			return
		}
	}
}

// processConflicts processes pending conflicts
func (r *RealTimeVaultSync) processConflicts() {
	r.conflictMutex.Lock()
	defer r.conflictMutex.Unlock()

	for i, conflict := range r.conflictQueue {
		if conflict.Status == ConflictStatusPending {
			// Auto-resolve simple conflicts (in a real implementation, this would be more sophisticated)
			if r.canAutoResolve(conflict) {
				r.conflictQueue[i].Status = ConflictStatusResolved
				r.conflictQueue[i].Resolution = "auto_resolved"
				log.Printf("Auto-resolved conflict for: %s", conflict.Path)
			}
		}
	}

	// Remove resolved conflicts older than 1 hour
	var activeConflicts []ConflictResolution
	for _, conflict := range r.conflictQueue {
		if conflict.Status == ConflictStatusPending || time.Since(conflict.Timestamp) < time.Hour {
			activeConflicts = append(activeConflicts, conflict)
		}
	}
	r.conflictQueue = activeConflicts
}

// canAutoResolve determines if a conflict can be automatically resolved
func (r *RealTimeVaultSync) canAutoResolve(conflict ConflictResolution) bool {
	// Simple auto-resolution logic
	// In a real implementation, this would be more sophisticated
	return conflict.LocalChange.Timestamp.After(conflict.RemoteChange.Timestamp)
}

// cleanupInactiveClients removes inactive clients
func (r *RealTimeVaultSync) cleanupInactiveClients() {
	ticker := time.NewTicker(5 * time.Minute)
	defer ticker.Stop()

	for {
		select {
		case <-ticker.C:
			r.clientsMutex.Lock()
			for clientID, client := range r.clients {
				if time.Since(client.LastSeen) > 10*time.Minute {
					client.IsActive = false
					log.Printf("Marked client %s as inactive", clientID)
				}
			}
			r.clientsMutex.Unlock()

		case <-r.stopChan:
			return
		}
	}
}

// GetStats returns synchronization statistics
func (r *RealTimeVaultSync) GetStats() SyncStats {
	r.clientsMutex.RLock()
	defer r.clientsMutex.RUnlock()

	activeClients := 0
	for _, client := range r.clients {
		if client.IsActive {
			activeClients++
		}
	}

	r.conflictMutex.Lock()
	defer r.conflictMutex.Unlock()

	return SyncStats{
		TotalChanges:    len(r.changeBuffer),
		SuccessfulSyncs: 0, // This would be tracked in a real implementation
		FailedSyncs:     0, // This would be tracked in a real implementation
		ActiveClients:   activeClients,
		LastSyncTime:    r.lastSyncTime,
		SyncDuration:    r.syncInterval,
		ConflictsCount:  len(r.conflictQueue),
	}
}

// GetConflicts returns pending conflicts
func (r *RealTimeVaultSync) GetConflicts() []ConflictResolution {
	r.conflictMutex.Lock()
	defer r.conflictMutex.Unlock()

	conflicts := make([]ConflictResolution, len(r.conflictQueue))
	copy(conflicts, r.conflictQueue)
	return conflicts
}

// ResolveConflict resolves a specific conflict
func (r *RealTimeVaultSync) ResolveConflict(conflictID, resolution string) error {
	r.conflictMutex.Lock()
	defer r.conflictMutex.Unlock()

	for i, conflict := range r.conflictQueue {
		if conflict.ID == conflictID {
			r.conflictQueue[i].Status = ConflictStatusResolved
			r.conflictQueue[i].Resolution = resolution
			log.Printf("Resolved conflict %s with resolution: %s", conflictID, resolution)
			return nil
		}
	}

	return fmt.Errorf("conflict not found: %s", conflictID)
}

// Example usage and testing
func runRealTimeSyncDemo() {
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

	// Register a test client
	client := sync.RegisterClient("test_client", []string{"notes", "projects"})
	defer sync.UnregisterClient("test_client")

	// Monitor for updates
	go func() {
		for {
			select {
			case change := <-client.UpdateChan:
				fmt.Printf("📄 Change detected: %s %s at %v\n", change.Type, change.Path, change.Timestamp)
				if change.Content != "" {
					fmt.Printf("   Content preview: %s...\n", change.Content[:minInt(50, len(change.Content))])
				}
			}
		}
	}()

	// Print stats every 30 seconds
	ticker := time.NewTicker(30 * time.Second)
	defer ticker.Stop()

	for {
		select {
		case <-ticker.C:
			stats := sync.GetStats()
			fmt.Printf("\n📊 Sync Stats:\n")
			fmt.Printf("   Active Clients: %d\n", stats.ActiveClients)
			fmt.Printf("   Pending Changes: %d\n", stats.TotalChanges)
			fmt.Printf("   Conflicts: %d\n", stats.ConflictsCount)
			fmt.Printf("   Last Sync: %v\n", stats.LastSyncTime.Format("15:04:05"))

			conflicts := sync.GetConflicts()
			if len(conflicts) > 0 {
				fmt.Printf("\n⚠️  Pending Conflicts:\n")
				for _, conflict := range conflicts {
					fmt.Printf("   %s: %s (%s)\n", conflict.ID, conflict.Path, conflict.Status)
				}
			}

		case <-time.After(5 * time.Minute):
			fmt.Println("\n🔄 Real-time synchronization demo completed")
			return
		}
	}
}

func minInt(a, b int) int {
	if a < b {
		return a
	}
	return b
}
