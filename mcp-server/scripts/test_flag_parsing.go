package main

import (
	"flag"
	"fmt"
)

func main() {
	// Parse command line flags
	mockMode := flag.Bool("mock", false, "Run in mock mode (no external dependencies)")
	port := flag.String("port", "3010", "Server port")
	configPath := flag.String("config", "configs/config.yaml", "Configuration file path")
	flag.Parse()

	fmt.Printf("Mock Mode: %v\n", *mockMode)
	fmt.Printf("Port: %s\n", *port)
	fmt.Printf("Config Path: %s\n", *configPath)
	
	if *mockMode {
		fmt.Println("Server will run in MOCK MODE")
	} else {
		fmt.Println("Server will run in REAL MODE")
	}
}
