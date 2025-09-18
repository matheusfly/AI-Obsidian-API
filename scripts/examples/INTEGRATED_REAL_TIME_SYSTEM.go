package main

import (
	"fmt"
	"log"
	"time"
)

// IntegratedRealTimeSystem provides a complete real-time synchronization system
type IntegratedRealTimeSystem struct {
	syncService *RealTimeVaultSync
	dashboard   *VaultMonitoringDashboard
	testSuite   *RealTimeSyncTestSuite
	isRunning   bool
}

// NewIntegratedRealTimeSystem creates a new integrated system
func NewIntegratedRealTimeSystem(vaultPath, apiBaseURL, apiToken string) (*IntegratedRealTimeSystem, error) {
	// Create sync service
	syncService, err := NewRealTimeVaultSync(vaultPath, apiBaseURL, apiToken)
	if err != nil {
		return nil, fmt.Errorf("failed to create sync service: %w", err)
	}

	// Create dashboard
	dashboard := NewVaultMonitoringDashboard(syncService, "8082")

	// Create test suite
	testSuite := NewRealTimeSyncTestSuite()

	return &IntegratedRealTimeSystem{
		syncService: syncService,
		dashboard:   dashboard,
		testSuite:   testSuite,
		isRunning:   false,
	}, nil
}

// Start starts the complete integrated system
func (s *IntegratedRealTimeSystem) Start() error {
	if s.isRunning {
		return fmt.Errorf("system is already running")
	}

	log.Println("🚀 Starting Integrated Real-Time Synchronization System...")

	// Start sync service
	err := s.syncService.Start()
	if err != nil {
		return fmt.Errorf("failed to start sync service: %w", err)
	}

	// Start dashboard in a goroutine
	go func() {
		if err := s.dashboard.Start(); err != nil {
			log.Printf("Dashboard error: %v", err)
		}
	}()

	s.isRunning = true
	log.Println("✅ Integrated system started successfully")
	return nil
}

// Stop stops the complete integrated system
func (s *IntegratedRealTimeSystem) Stop() error {
	if !s.isRunning {
		return fmt.Errorf("system is not running")
	}

	log.Println("🛑 Stopping Integrated Real-Time Synchronization System...")

	err := s.syncService.Stop()
	if err != nil {
		log.Printf("Error stopping sync service: %v", err)
	}

	s.isRunning = false
	log.Println("✅ Integrated system stopped")
	return nil
}

// RunTests runs the comprehensive test suite
func (s *IntegratedRealTimeSystem) RunTests() error {
	log.Println("🧪 Running comprehensive test suite...")

	// Setup test environment
	err := s.testSuite.SetupTestEnvironment()
	if err != nil {
		return fmt.Errorf("failed to setup test environment: %w", err)
	}
	defer s.testSuite.CleanupTestEnvironment()

	// Run all tests
	suite := s.testSuite.RunAllTests()

	// Print results
	s.testSuite.PrintTestResults()

	if suite.FailedTests > 0 {
		return fmt.Errorf("test suite failed with %d failed tests", suite.FailedTests)
	}

	log.Printf("🎉 All tests passed! Success rate: %.1f%%", suite.SuccessRate)
	return nil
}

// GetSystemStatus returns the current system status
func (s *IntegratedRealTimeSystem) GetSystemStatus() map[string]interface{} {
	status := map[string]interface{}{
		"is_running": s.isRunning,
		"timestamp":  time.Now(),
	}

	if s.isRunning {
		stats := s.syncService.GetStats()
		status["sync_stats"] = stats
		status["conflicts"] = s.syncService.GetConflicts()
	}

	return status
}

// AddSampleAlert adds a sample alert to the dashboard
func (s *IntegratedRealTimeSystem) AddSampleAlert(alertType AlertType, severity Severity, message string) {
	if s.dashboard != nil {
		s.dashboard.addAlert(alertType, severity, message)
	}
}

// DemoSystem demonstrates the complete system functionality
func (s *IntegratedRealTimeSystem) DemoSystem() error {
	log.Println("🎬 Starting system demonstration...")

	// Start the system
	err := s.Start()
	if err != nil {
		return fmt.Errorf("failed to start system: %w", err)
	}
	defer s.Stop()

	// Add some sample alerts
	s.AddSampleAlert(AlertTypeSyncError, SeverityMedium, "Demo sync error")
	s.AddSampleAlert(AlertTypeConflict, SeverityHigh, "Demo conflict detected")
	s.AddSampleAlert(AlertTypeHighLoad, SeverityLow, "Demo high load alert")

	// Register a demo client
	client := s.syncService.RegisterClient("demo_client", []string{"notes", "projects"})
	defer s.syncService.UnregisterClient("demo_client")

	// Monitor for changes
	go func() {
		for {
			select {
			case change := <-client.UpdateChan:
				log.Printf("📄 Change detected: %s %s at %v", change.Type, change.Path, change.Timestamp)
			}
		}
	}()

	// Print system information
	log.Println("\n📋 System Information:")
	log.Printf("   🔄 Sync Service: Active")
	log.Printf("   📊 Dashboard: http://localhost:8082")
	log.Printf("   👥 Active Clients: %d", s.syncService.GetStats().ActiveClients)
	log.Printf("   ⚠️ Conflicts: %d", s.syncService.GetStats().ConflictsCount)

	// Run for demonstration period
	log.Println("\n⏰ Running demonstration for 2 minutes...")
	time.Sleep(2 * time.Minute)

	log.Println("🎬 Demonstration completed")
	return nil
}

// Example usage and testing
func main() {
	// Configuration
	vaultPath := "D:\\Nomade Milionario"
	apiBaseURL := "http://localhost:27124"
	apiToken := "b26efa44ceb0bd4e1fae338cede5384237bbab8624c61927986aa3f06c2f5a70"

	// Create integrated system
	system, err := NewIntegratedRealTimeSystem(vaultPath, apiBaseURL, apiToken)
	if err != nil {
		log.Fatalf("Failed to create integrated system: %v", err)
	}

	// Run demonstration
	err = system.DemoSystem()
	if err != nil {
		log.Fatalf("Demo failed: %v", err)
	}

	log.Println("🎉 Integrated Real-Time Synchronization System demo completed successfully!")
}
