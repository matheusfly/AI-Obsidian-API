package config

import (
	"fmt"
	"github.com/spf13/viper"
)

// Config holds all application configuration
type Config struct {
	API struct {
		BaseURL string `mapstructure:"base_url"`
		Token   string `mapstructure:"token"`
	} `mapstructure:"api"`
	Server struct {
		Port string `mapstructure:"port"`
		Auth string `mapstructure:"auth"`
	} `mapstructure:"server"`
	Retrieval struct {
		ChunkSize      int    `mapstructure:"chunk_size"`
		EmbeddingModel string `mapstructure:"embedding_model"`
		VectorDB       string `mapstructure:"vector_db"`
	} `mapstructure:"retrieval"`
	Ollama struct {
		Host  string `mapstructure:"host"`
		Model string `mapstructure:"model"`
	} `mapstructure:"ollama"`
	Vault struct {
		Path       string `mapstructure:"path"`
		EnableCache bool   `mapstructure:"enable_cache"`
		CacheTTL   string `mapstructure:"cache_ttl"`
	} `mapstructure:"vault"`
}

// LoadConfig reads configuration from file or environment variables.
func LoadConfig(configPath string) (*Config, error) {
	viper.SetConfigFile(configPath)
	viper.SetConfigType("yaml")

	viper.SetDefault("api.base_url", "http://localhost:27124")
	viper.SetDefault("api.token", "b26efa44ceb0bd4e1fae338cede5384237bbab8624c61927986aa3f06c2f5a70")
	viper.SetDefault("server.port", "3010")
	viper.SetDefault("server.auth", "local-token")
	viper.SetDefault("retrieval.chunk_size", 1024)
	viper.SetDefault("retrieval.embedding_model", "deepseek-r1:8b")
	viper.SetDefault("retrieval.vector_db", "in-memory")
	viper.SetDefault("ollama.host", "http://localhost:11434")
	viper.SetDefault("ollama.model", "deepseek-r1:8b")
	viper.SetDefault("vault.path", "D:\\Nomade Milionario")
	viper.SetDefault("vault.enable_cache", true)
	viper.SetDefault("vault.cache_ttl", "5m")

	if err := viper.ReadInConfig(); err != nil {
		if _, ok := err.(viper.ConfigFileNotFoundError); ok {
			fmt.Printf("Config file not found at %s, using defaults.\n", configPath)
		} else {
			return nil, fmt.Errorf("failed to read config file: %w", err)
		}
	}

	var cfg Config
	if err := viper.Unmarshal(&cfg); err != nil {
		return nil, fmt.Errorf("failed to unmarshal config: %w", err)
	}

	return &cfg, nil
}
