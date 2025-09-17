package algorithms

import (
	"bufio"
	"fmt"
	"io"
	"strings"
	"sync"
	"time"
)

// StreamingMerger merges incremental streaming chunks safely
// Handles large file contents with proper buffering
type StreamingMerger struct {
	bufferSize    int
	delimiter     string
	maxBufferSize int
	timeout       time.Duration
}

// StreamChunk represents a chunk of streaming data
type StreamChunk struct {
	Data      []byte
	Timestamp time.Time
	Index     int
	Complete  bool
}

// MergedResult represents a merged result from streaming
type MergedResult struct {
	Content    string
	ChunkCount int
	Duration   time.Duration
	Size       int
	Complete   bool
}

// StreamProcessor handles streaming data processing
type StreamProcessor struct {
	merger    *StreamingMerger
	buffer    strings.Builder
	chunks    []StreamChunk
	mutex     sync.RWMutex
	startTime time.Time
}

// NewStreamingMerger creates a new StreamingMerger instance
func NewStreamingMerger() *StreamingMerger {
	return &StreamingMerger{
		bufferSize:    4096,             // 4KB buffer
		delimiter:     "\n",             // Line delimiter
		maxBufferSize: 1024 * 1024,      // 1MB max buffer
		timeout:       30 * time.Second, // 30 second timeout
	}
}

// NewStreamProcessor creates a new StreamProcessor
func NewStreamProcessor(merger *StreamingMerger) *StreamProcessor {
	return &StreamProcessor{
		merger:    merger,
		buffer:    strings.Builder{},
		chunks:    []StreamChunk{},
		startTime: time.Now(),
	}
}

// ProcessStream processes a streaming response
func (sm *StreamingMerger) ProcessStream(reader io.Reader) (*MergedResult, error) {
	processor := NewStreamProcessor(sm)
	return processor.processStream(reader)
}

// processStream processes the actual stream
func (sp *StreamProcessor) processStream(reader io.Reader) (*MergedResult, error) {
	scanner := bufio.NewScanner(reader)
	scanner.Buffer(make([]byte, sp.merger.bufferSize), sp.merger.maxBufferSize)

	chunkIndex := 0

	for scanner.Scan() {
		line := scanner.Text()

		// Create chunk
		chunk := StreamChunk{
			Data:      []byte(line),
			Timestamp: time.Now(),
			Index:     chunkIndex,
			Complete:  false,
		}

		// Add to buffer
		sp.addChunk(chunk)

		// Check for complete lines
		if sp.hasCompleteLine() {
			sp.processCompleteLines()
		}

		chunkIndex++

		// Check timeout
		if time.Since(sp.startTime) > sp.merger.timeout {
			break
		}
	}

	// Process remaining buffer
	sp.processRemainingBuffer()

	// Check for scanner errors
	if err := scanner.Err(); err != nil {
		return nil, err
	}

	// Create result
	result := &MergedResult{
		Content:    sp.buffer.String(),
		ChunkCount: len(sp.chunks),
		Duration:   time.Since(sp.startTime),
		Size:       sp.buffer.Len(),
		Complete:   true,
	}

	return result, nil
}

// addChunk adds a chunk to the processor
func (sp *StreamProcessor) addChunk(chunk StreamChunk) {
	sp.mutex.Lock()
	defer sp.mutex.Unlock()

	sp.chunks = append(sp.chunks, chunk)
}

// hasCompleteLine checks if there are complete lines in the buffer
func (sp *StreamProcessor) hasCompleteLine() bool {
	sp.mutex.RLock()
	defer sp.mutex.RUnlock()

	content := sp.buffer.String()
	return strings.Contains(content, sp.merger.delimiter)
}

// processCompleteLines processes complete lines from the buffer
func (sp *StreamProcessor) processCompleteLines() {
	sp.mutex.Lock()
	defer sp.mutex.Unlock()

	content := sp.buffer.String()
	lines := strings.Split(content, sp.merger.delimiter)

	// Keep the last incomplete line in buffer
	if len(lines) > 1 {
		// Process all complete lines except the last one
		for i := 0; i < len(lines)-1; i++ {
			sp.processLine(lines[i])
		}

		// Keep the last line in buffer (might be incomplete)
		sp.buffer.Reset()
		sp.buffer.WriteString(lines[len(lines)-1])
	}
}

// processRemainingBuffer processes any remaining content in the buffer
func (sp *StreamProcessor) processRemainingBuffer() {
	sp.mutex.Lock()
	defer sp.mutex.Unlock()

	content := sp.buffer.String()
	if len(content) > 0 {
		sp.processLine(content)
	}
}

// processLine processes a single line
func (sp *StreamProcessor) processLine(line string) {
	// Add line to final content
	sp.buffer.WriteString(line)
	sp.buffer.WriteString(sp.merger.delimiter)
}

// MergeChunks merges multiple chunks into a single result
func (sm *StreamingMerger) MergeChunks(chunks []StreamChunk) *MergedResult {
	var content strings.Builder
	startTime := time.Now()

	for _, chunk := range chunks {
		content.Write(chunk.Data)
		if !chunk.Complete {
			content.WriteString(sm.delimiter)
		}
	}

	return &MergedResult{
		Content:    content.String(),
		ChunkCount: len(chunks),
		Duration:   time.Since(startTime),
		Size:       content.Len(),
		Complete:   true,
	}
}

// StreamFileContent streams file content with proper buffering
func (sm *StreamingMerger) StreamFileContent(filePath string, apiKey, baseURL string) (*MergedResult, error) {
	// This would typically make an HTTP request to get file content
	// For now, we'll simulate with a mock reader

	// In a real implementation, this would be:
	// resp, err := http.Get(baseURL + "/vault/" + filePath)
	// if err != nil {
	//     return nil, err
	// }
	// defer resp.Body.Close()
	// return sm.ProcessStream(resp.Body)

	// Mock implementation for demonstration
	mockContent := "This is mock file content\nwith multiple lines\nfor streaming demonstration"
	reader := strings.NewReader(mockContent)

	return sm.ProcessStream(reader)
}

// SetBufferSize sets the buffer size for streaming
func (sm *StreamingMerger) SetBufferSize(size int) {
	if size > 0 {
		sm.bufferSize = size
	}
}

// SetDelimiter sets the delimiter for line processing
func (sm *StreamingMerger) SetDelimiter(delimiter string) {
	sm.delimiter = delimiter
}

// SetTimeout sets the timeout for streaming operations
func (sm *StreamingMerger) SetTimeout(timeout time.Duration) {
	sm.timeout = timeout
}

// GetStreamingStats returns statistics about streaming operations
func (sm *StreamingMerger) GetStreamingStats(result *MergedResult) map[string]interface{} {
	if result == nil {
		return map[string]interface{}{
			"chunk_count": 0,
			"duration":    0,
			"size":        0,
			"complete":    false,
		}
	}

	return map[string]interface{}{
		"chunk_count": result.ChunkCount,
		"duration":    result.Duration,
		"size":        result.Size,
		"complete":    result.Complete,
		"buffer_size": sm.bufferSize,
		"delimiter":   sm.delimiter,
		"timeout":     sm.timeout,
	}
}

// OptimizeStreaming optimizes streaming parameters based on content type
func (sm *StreamingMerger) OptimizeStreaming(contentType string) {
	switch contentType {
	case "text/plain":
		sm.delimiter = "\n"
		sm.bufferSize = 4096
	case "application/json":
		sm.delimiter = "\n"
		sm.bufferSize = 8192
	case "text/markdown":
		sm.delimiter = "\n"
		sm.bufferSize = 4096
	default:
		sm.delimiter = "\n"
		sm.bufferSize = 4096
	}
}

// ConcurrentStreamProcessor handles concurrent streaming
type ConcurrentStreamProcessor struct {
	merger     *StreamingMerger
	processors []*StreamProcessor
	results    chan *MergedResult
	errors     chan error
	wg         sync.WaitGroup
}

// NewConcurrentStreamProcessor creates a new concurrent stream processor
func NewConcurrentStreamProcessor(merger *StreamingMerger, concurrency int) *ConcurrentStreamProcessor {
	return &ConcurrentStreamProcessor{
		merger:     merger,
		processors: make([]*StreamProcessor, concurrency),
		results:    make(chan *MergedResult, concurrency),
		errors:     make(chan error, concurrency),
	}
}

// ProcessMultipleStreams processes multiple streams concurrently
func (csp *ConcurrentStreamProcessor) ProcessMultipleStreams(readers []io.Reader) ([]*MergedResult, error) {
	// Start goroutines for each reader
	for i, reader := range readers {
		csp.wg.Add(1)
		go func(index int, r io.Reader) {
			defer csp.wg.Done()

			processor := NewStreamProcessor(csp.merger)
			result, err := processor.processStream(r)

			if err != nil {
				csp.errors <- err
			} else {
				csp.results <- result
			}
		}(i, reader)
	}

	// Wait for all goroutines to complete
	csp.wg.Wait()
	close(csp.results)
	close(csp.errors)

	// Collect results
	var results []*MergedResult
	for result := range csp.results {
		results = append(results, result)
	}

	// Check for errors
	select {
	case err := <-csp.errors:
		return results, err
	default:
		return results, nil
	}
}

// Helper functions

// estimateStreamSize estimates the size of a stream
func estimateStreamSize(reader io.Reader) (int64, error) {
	// This is a simplified estimation
	// In practice, you might peek at the first few bytes
	return 0, nil
}

// validateStream validates a stream before processing
func validateStream(reader io.Reader) error {
	// Basic validation - check if reader is nil
	if reader == nil {
		return fmt.Errorf("reader is nil")
	}
	return nil
}

// GetStats returns statistics about the StreamingMerger algorithm
func (sm *StreamingMerger) GetStats() map[string]interface{} {
	return map[string]interface{}{
		"buffer_size": sm.bufferSize,
		"delimiter":   sm.delimiter,
		"timeout":     sm.timeout,
	}
}
