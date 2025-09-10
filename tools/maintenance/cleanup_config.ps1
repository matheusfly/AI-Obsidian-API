# Cleanup System Configuration
# This file contains all configuration settings for the cleanup system

# Essential files that should NEVER be deleted
$Global:EssentialFiles = @(
    "README.md",
    "PROJECT_ORGANIZATION.md",
    "docker-compose.yml",
    "requirements.txt",
    "pyproject.toml",
    "uv.lock",
    "mcp.json",
    "langgraph.json",
    ".gitignore",
    ".env",
    ".dockerignore"
)

# Essential directories that should NEVER be modified
$Global:EssentialDirs = @(
    "core_services",
    "monitoring_tools", 
    "test_suites",
    "documentation",
    "deployment",
    "examples",
    "requirements",
    "temp_files",
    "reports",
    "docs",
    "mcp_tools",
    "langgraph_workflows",
    "api_gateway",
    "config",
    "data",
    "data_pipeline",
    "graph_db",
    "indexer",
    "langgraph_project",
    "langgraph_server",
    "logs",
    "monitoring",
    "tests",
    "utils",
    "vector_db",
    "vault",
    "context-cache",
    "image",
    "cleanup_system"
)

# Patterns for unusual files
$Global:UnusualPatterns = @(
    "*test*test*",           # Multiple test in name
    "*final*final*",         # Multiple final in name
    "*ultimate*ultimate*",   # Multiple ultimate in name
    "*110*110*",             # Multiple 110 in name
    "*achievement*achievement*", # Multiple achievement in name
    "*110-percent*110-percent*", # Multiple 110-percent in name
    "*hotfix*hotfix*",       # Multiple hotfix in name
    "*simple*simple*",       # Multiple simple in name
    "*debug*debug*",         # Multiple debug in name
    "*diagnostic*diagnostic*", # Multiple diagnostic in name
    "*setup*setup*",         # Multiple setup in name
    "*observability*observability*" # Multiple observability in name
)

# Duplicate script patterns
$Global:DuplicateScripts = @(
    "achieve-110-percent-final.ps1",
    "achieve-110-percent.ps1", 
    "final-110-percent-achievement.ps1",
    "final-110-percent-test.ps1",
    "mission-accomplished-110.ps1",
    "ultimate-110-achievement.ps1",
    "ultimate-110-percent-achievement.ps1",
    "ultimate-110-percent-cli.ps1",
    "ultimate-110-percent-final.ps1",
    "ultimate-110-percent-test.ps1",
    "ultimate-performance-test.ps1",
    "build-v0_1.ps1",
    "build-v0_2.ps1", 
    "build-v0_3.ps1",
    "simple-hotfix.ps1",
    "hotfix-deploy.ps1",
    "simple-observability-setup.ps1",
    "setup-observability-simple.ps1",
    "setup-observability-complete.ps1",
    "ultimate-observability-setup.ps1",
    "simple-agent-revival.ps1",
    "agent-revival-no-emoji.ps1",
    "ultimate-agent-revival.ps1",
    "simple-start.ps1",
    "start-all-services.ps1",
    "quick-diagnostic.ps1",
    "quick-fix.ps1",
    "debug-system.ps1",
    "ultimate-diagnostic-and-fix.ps1",
    "final-test-suite.ps1",
    "final-test.ps1",
    "run-tests-debug.ps1",
    "test-mcp.ps1"
)

# File age thresholds (in days)
$Global:AgeThresholds = @{
    OldTestFiles = 7
    OldReportFiles = 30
    OldLogFiles = 14
    OldBackupFiles = 90
}

# File size thresholds
$Global:SizeThresholds = @{
    EmptyFile = 0
    SmallFile = 1024  # 1KB
    LargeFile = 10485760  # 10MB
}

# Backup configuration
$Global:BackupConfig = @{
    BasePath = "temp_files\backup"
    TimestampFormat = "yyyyMMdd_HHmmss"
    MaxBackups = 10
    CompressBackups = $false
}

# Logging configuration
$Global:LogConfig = @{
    LogLevel = "INFO"
    LogFile = "cleanup_system\cleanup.log"
    MaxLogSize = 10485760  # 10MB
    MaxLogFiles = 5
}

# Cleanup rules
$Global:CleanupRules = @{
    RemoveEmptyFiles = $true
    RemoveDuplicateFiles = $true
    RemoveOldTestFiles = $true
    RemoveOldReportFiles = $true
    RemoveOldLogFiles = $true
    RemoveUnusualPatterns = $true
    BackupBeforeDelete = $true
    DryRunByDefault = $false
}

# Project structure rules
$Global:ProjectStructure = @{
    RootMaxFiles = 20
    ScriptsMaxFiles = 10
    ReportsMaxFiles = 50
    TempFilesMaxFiles = 100
    LogsMaxFiles = 30
}

# Configuration variables are now available globally
# No need to export as this is not a module
