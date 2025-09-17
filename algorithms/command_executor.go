package algorithms

import (
	"bytes"
	"crypto/tls"
	"encoding/json"
	"fmt"
	"net/http"
	"strings"
	"time"
)

// CommandExecutor safely executes commands via /commands/{id} with parameter handling
type CommandExecutor struct {
	apiKey     string
	baseURL    string
	httpClient *http.Client
	commands   map[string]CommandInfo
	stats      ExecutionStats
}

// CommandInfo represents information about an available command
type CommandInfo struct {
	ID          string                 `json:"id"`
	Name        string                 `json:"name"`
	Description string                 `json:"description,omitempty"`
	Parameters  map[string]interface{} `json:"parameters,omitempty"`
}

// ExecutionStats tracks command execution statistics
type ExecutionStats struct {
	Executed     int            `json:"executed"`
	Successful   int            `json:"successful"`
	Failed       int            `json:"failed"`
	TotalTime    time.Duration  `json:"total_time"`
	LastExecuted time.Time      `json:"last_executed"`
	Commands     map[string]int `json:"commands"` // Command ID -> execution count
}

// ExecutionResult represents the result of a command execution
type ExecutionResult struct {
	Success     bool          `json:"success"`
	CommandID   string        `json:"command_id"`
	CommandName string        `json:"command_name"`
	Result      interface{}   `json:"result"`
	Error       string        `json:"error,omitempty"`
	Duration    time.Duration `json:"duration"`
	Timestamp   time.Time     `json:"timestamp"`
}

// NewCommandExecutor creates a new CommandExecutor instance
func NewCommandExecutor(apiKey, baseURL string) *CommandExecutor {
	// Configure HTTP client with TLS bypass for self-signed certificates
	tr := &http.Transport{
		TLSClientConfig: &tls.Config{InsecureSkipVerify: true},
	}

	return &CommandExecutor{
		apiKey:     apiKey,
		baseURL:    baseURL,
		httpClient: &http.Client{Transport: tr, Timeout: 60 * time.Second},
		commands:   make(map[string]CommandInfo),
		stats:      ExecutionStats{Commands: make(map[string]int)},
	}
}

// ListCommands retrieves all available commands from the API
func (ce *CommandExecutor) ListCommands() ([]CommandInfo, error) {
	url := ce.baseURL + "/commands/"
	req, err := http.NewRequest("GET", url, nil)
	if err != nil {
		return nil, fmt.Errorf("failed to create request: %w", err)
	}

	req.Header.Add("Authorization", "Bearer "+ce.apiKey)
	req.Header.Add("Accept", "application/json")

	resp, err := ce.httpClient.Do(req)
	if err != nil {
		return nil, fmt.Errorf("failed to execute request: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != 200 {
		return nil, fmt.Errorf("API request failed with status %d", resp.StatusCode)
	}

	var commands []CommandInfo
	if err := json.NewDecoder(resp.Body).Decode(&commands); err != nil {
		return nil, fmt.Errorf("failed to decode response: %w", err)
	}

	// Cache commands
	ce.commands = make(map[string]CommandInfo)
	for _, cmd := range commands {
		ce.commands[cmd.ID] = cmd
	}

	return commands, nil
}

// Execute executes a command by ID with optional parameters
func (ce *CommandExecutor) Execute(commandID string, parameters map[string]interface{}) (*ExecutionResult, error) {
	startTime := time.Now()
	result := &ExecutionResult{
		CommandID: commandID,
		Timestamp: time.Now(),
	}

	// Get command info
	command, exists := ce.commands[commandID]
	if !exists {
		// Try to refresh commands list
		if _, err := ce.ListCommands(); err != nil {
			result.Error = fmt.Sprintf("command not found and failed to refresh commands: %v", err)
			ce.stats.Failed++
			return result, fmt.Errorf("command %s not found", commandID)
		}

		command, exists = ce.commands[commandID]
		if !exists {
			result.Error = "command not found after refresh"
			ce.stats.Failed++
			return result, fmt.Errorf("command %s not found", commandID)
		}
	}

	result.CommandName = command.Name
	ce.stats.Executed++
	ce.stats.Commands[commandID]++

	// Prepare request
	url := ce.baseURL + "/commands/" + commandID
	jsonData, err := json.Marshal(parameters)
	if err != nil {
		result.Error = fmt.Sprintf("failed to marshal parameters: %v", err)
		ce.stats.Failed++
		return result, err
	}

	req, err := http.NewRequest("POST", url, bytes.NewBuffer(jsonData))
	if err != nil {
		result.Error = fmt.Sprintf("failed to create request: %v", err)
		ce.stats.Failed++
		return result, err
	}

	req.Header.Add("Authorization", "Bearer "+ce.apiKey)
	req.Header.Add("Content-Type", "application/json")

	// Execute command
	resp, err := ce.httpClient.Do(req)
	if err != nil {
		result.Error = fmt.Sprintf("failed to execute request: %v", err)
		ce.stats.Failed++
		return result, err
	}
	defer resp.Body.Close()

	result.Duration = time.Since(startTime)
	ce.stats.TotalTime += result.Duration
	ce.stats.LastExecuted = time.Now()

	if resp.StatusCode == 200 {
		// Parse response
		var responseData interface{}
		if err := json.NewDecoder(resp.Body).Decode(&responseData); err != nil {
			result.Error = fmt.Sprintf("failed to decode response: %v", err)
			ce.stats.Failed++
			return result, err
		}

		result.Success = true
		result.Result = responseData
		ce.stats.Successful++
	} else {
		result.Error = fmt.Sprintf("command execution failed with status %d", resp.StatusCode)
		ce.stats.Failed++
	}

	return result, nil
}

// ExecuteByName executes a command by name (searches for matching command)
func (ce *CommandExecutor) ExecuteByName(commandName string, parameters map[string]interface{}) (*ExecutionResult, error) {
	// Find command by name
	var commandID string
	for id, cmd := range ce.commands {
		if strings.EqualFold(cmd.Name, commandName) {
			commandID = id
			break
		}
	}

	if commandID == "" {
		return nil, fmt.Errorf("command with name '%s' not found", commandName)
	}

	return ce.Execute(commandID, parameters)
}

// GetCommandInfo retrieves information about a specific command
func (ce *CommandExecutor) GetCommandInfo(commandID string) (*CommandInfo, error) {
	command, exists := ce.commands[commandID]
	if !exists {
		// Try to refresh commands list
		if _, err := ce.ListCommands(); err != nil {
			return nil, fmt.Errorf("command not found and failed to refresh commands: %w", err)
		}

		command, exists = ce.commands[commandID]
		if !exists {
			return nil, fmt.Errorf("command %s not found", commandID)
		}
	}

	return &command, nil
}

// GetCommandByName finds a command by name
func (ce *CommandExecutor) GetCommandByName(commandName string) (*CommandInfo, error) {
	for _, cmd := range ce.commands {
		if strings.EqualFold(cmd.Name, commandName) {
			return &cmd, nil
		}
	}
	return nil, fmt.Errorf("command with name '%s' not found", commandName)
}

// ListCommandNames returns a list of all available command names
func (ce *CommandExecutor) ListCommandNames() []string {
	names := make([]string, 0, len(ce.commands))
	for _, cmd := range ce.commands {
		names = append(names, cmd.Name)
	}
	return names
}

// GetStats returns execution statistics
func (ce *CommandExecutor) GetStats() ExecutionStats {
	return ce.stats
}

// ResetStats resets the statistics
func (ce *CommandExecutor) ResetStats() {
	ce.stats = ExecutionStats{Commands: make(map[string]int)}
}

// GetSuccessRate returns the success rate as a percentage
func (ce *CommandExecutor) GetSuccessRate() float64 {
	if ce.stats.Executed == 0 {
		return 0.0
	}
	return float64(ce.stats.Successful) / float64(ce.stats.Executed) * 100.0
}

// GetAverageTime returns the average execution time
func (ce *CommandExecutor) GetAverageTime() time.Duration {
	if ce.stats.Executed == 0 {
		return 0
	}
	return ce.stats.TotalTime / time.Duration(ce.stats.Executed)
}

// GetMostUsedCommand returns the most frequently used command
func (ce *CommandExecutor) GetMostUsedCommand() (string, int) {
	maxCount := 0
	var mostUsed string

	for commandID, count := range ce.stats.Commands {
		if count > maxCount {
			maxCount = count
			mostUsed = commandID
		}
	}

	return mostUsed, maxCount
}

// BatchExecute executes multiple commands in sequence
func (ce *CommandExecutor) BatchExecute(commands []struct {
	ID         string
	Parameters map[string]interface{}
}) ([]ExecutionResult, error) {
	results := make([]ExecutionResult, 0, len(commands))

	for _, cmd := range commands {
		result, err := ce.Execute(cmd.ID, cmd.Parameters)
		if err != nil {
			result = &ExecutionResult{
				Success:   false,
				CommandID: cmd.ID,
				Error:     err.Error(),
			}
		}
		results = append(results, *result)
	}

	return results, nil
}

// ExecuteWithRetry executes a command with retry logic
func (ce *CommandExecutor) ExecuteWithRetry(commandID string, parameters map[string]interface{}, maxRetries int) (*ExecutionResult, error) {
	var lastResult *ExecutionResult
	var lastError error

	for i := 0; i <= maxRetries; i++ {
		result, err := ce.Execute(commandID, parameters)
		if err == nil && result.Success {
			return result, nil
		}

		lastResult = result
		lastError = err

		// Wait before retry (exponential backoff)
		if i < maxRetries {
			waitTime := time.Duration(1<<uint(i)) * time.Second
			time.Sleep(waitTime)
		}
	}

	return lastResult, lastError
}

// ValidateCommand checks if a command exists and is valid
func (ce *CommandExecutor) ValidateCommand(commandID string) error {
	_, exists := ce.commands[commandID]
	if !exists {
		// Try to refresh commands list
		if _, err := ce.ListCommands(); err != nil {
			return fmt.Errorf("command not found and failed to refresh commands: %w", err)
		}

		_, exists = ce.commands[commandID]
		if !exists {
			return fmt.Errorf("command %s not found", commandID)
		}
	}

	return nil
}

// SearchCommands searches for commands by name or description
func (ce *CommandExecutor) SearchCommands(query string) []CommandInfo {
	query = strings.ToLower(query)
	results := make([]CommandInfo, 0)

	for _, cmd := range ce.commands {
		if strings.Contains(strings.ToLower(cmd.Name), query) ||
			strings.Contains(strings.ToLower(cmd.Description), query) {
			results = append(results, cmd)
		}
	}

	return results
}

// GetCommandCount returns the total number of available commands
func (ce *CommandExecutor) GetCommandCount() int {
	return len(ce.commands)
}

// IsCommandAvailable checks if a command is available
func (ce *CommandExecutor) IsCommandAvailable(commandID string) bool {
	_, exists := ce.commands[commandID]
	return exists
}
