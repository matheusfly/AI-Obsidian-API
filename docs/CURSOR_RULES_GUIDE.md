# 🎯 Cursor Rules Guide - API-MCP-Simbiosis

## 📋 **OVERVIEW**

This guide explains how to use the `.cursorrules` file to maintain the clean folder structure and professional organization of the API-MCP-Simbiosis project.

---

## 🚀 **QUICK START**

### **1. Enable Cursor Rules**
- The `.cursorrules` file is automatically loaded by Cursor
- Rules are enforced in real-time as you work
- Cursor will suggest corrections based on the rules

### **2. Follow the Rules**
- **Green suggestions**: Follow these recommendations
- **Red warnings**: Fix these issues immediately
- **Yellow hints**: Consider these improvements

---

## 📁 **FOLDER STRUCTURE ENFORCEMENT**

### ✅ **What Cursor Will Enforce**

#### **Test Files → test_scripts/**
```bash
# ❌ WRONG - Cursor will warn you
test_search.go          # In root directory

# ✅ CORRECT - Cursor will approve
test_scripts/test_search.go
```

#### **Example Files → example_scripts/**
```bash
# ❌ WRONG - Cursor will warn you
demo_search.go          # In root directory
run_search.go           # In root directory

# ✅ CORRECT - Cursor will approve
example_scripts/demo_search.go
example_scripts/run_search.go
```

#### **Debug Files → temp_files/**
```bash
# ❌ WRONG - Cursor will warn you
debug_vault.go          # In root directory
temp_test.go            # In root directory

# ✅ CORRECT - Cursor will approve
temp_files/debug_vault.go
temp_files/temp_test.go
```

### 🚫 **What Cursor Will Block**

#### **Prohibited in Root Directory**
- `test_*.go` files
- `*demo*.go` files
- `debug_*.go` files
- `temp_*.go` files
- `run_*.go` files
- `simple_*.go` files

#### **Allowed in Root Directory**
- `interactive_cli.go` (main CLI)
- `interactive_search_engine.go` (core engine)
- `go.mod` and `go.sum`
- Documentation files (`*.md`)

---

## 📝 **FILE NAMING ENFORCEMENT**

### ✅ **Correct Naming Patterns**

#### **Test Files**
```bash
test_search.go          # ✅ Correct
test_http_client.go     # ✅ Correct
search_test.go          # ✅ Correct
```

#### **Example Files**
```bash
demo_search.go          # ✅ Correct
example_basic.go        # ✅ Correct
run_search.go           # ✅ Correct
simple_demo.go          # ✅ Correct
```

#### **Debug Files**
```bash
debug_vault.go          # ✅ Correct
temp_test.go            # ✅ Correct
debug_response.go       # ✅ Correct
```

### 🚫 **Incorrect Naming Patterns**

```bash
TestSearch.go           # ❌ Wrong case
test search.go          # ❌ Spaces
test-search.go          # ❌ Hyphens
testSearch.go           # ❌ CamelCase
123test.go              # ❌ Numbers first
```

---

## 🧹 **CLEANUP ENFORCEMENT**

### ✅ **Automatic Cleanup Suggestions**

#### **Before Committing**
Cursor will remind you to:
1. Move test files to `test_scripts/`
2. Move example files to `example_scripts/`
3. Move debug files to `temp_files/`
4. Remove unused imports
5. Remove unused variables
6. Update documentation

#### **Weekly Maintenance**
Cursor will suggest:
1. Clean up `temp_files/` directory
2. Review `test_scripts/` organization
3. Review `example_scripts/` organization
4. Update `CHANGELOG.md`
5. Update `README.md` if needed

---

## 🔧 **CODE QUALITY ENFORCEMENT**

### ✅ **Automatic Quality Checks**

#### **Go Formatting**
```bash
# Cursor will suggest:
go fmt ./...
goimports -w .
```

#### **Go Linting**
```bash
# Cursor will suggest:
golangci-lint run
```

#### **Go Testing**
```bash
# Cursor will suggest:
go test ./tests/... -v
go test ./algorithms/... -v
go test ./client/... -v
```

### 🚫 **Code Quality Violations**

#### **Unused Imports**
```go
// ❌ WRONG - Cursor will warn
import (
    "fmt"        // Used
    "os"         // Unused - Cursor will suggest removal
    "strings"    // Used
)
```

#### **Unused Variables**
```go
// ❌ WRONG - Cursor will warn
func testFunction() {
    result := "test"     // Unused - Cursor will suggest removal
    fmt.Println("test")
}
```

#### **Long Functions**
```go
// ❌ WRONG - Cursor will warn (if >50 lines)
func veryLongFunction() {
    // ... 60 lines of code
}
```

---

## 📚 **DOCUMENTATION ENFORCEMENT**

### ✅ **Required Documentation**

#### **File Headers**
```go
// ✅ CORRECT - Cursor will approve
// Package algorithms provides search algorithms for the API-MCP-Simbiosis project.
// This file implements the QueryComposer algorithm for query expansion and field boosting.
package algorithms
```

#### **Function Documentation**
```go
// ✅ CORRECT - Cursor will approve
// NewQueryComposer creates a new QueryComposer instance with the specified configuration.
// Parameters:
//   - config: QueryComposer configuration
// Returns:
//   - *QueryComposer: New QueryComposer instance
func NewQueryComposer(config Config) *QueryComposer {
    // ...
}
```

### 🚫 **Missing Documentation**

```go
// ❌ WRONG - Cursor will warn
func newQueryComposer(config Config) *QueryComposer {
    // Missing documentation
}
```

---

## 🧪 **TESTING ENFORCEMENT**

### ✅ **Required Tests**

#### **Algorithm Tests**
```go
// ✅ CORRECT - Cursor will approve
func TestQueryComposer(t *testing.T) {
    // Test implementation
}
```

#### **Client Tests**
```go
// ✅ CORRECT - Cursor will approve
func TestHTTPClient(t *testing.T) {
    // Test implementation
}
```

### 🚫 **Missing Tests**

```go
// ❌ WRONG - Cursor will warn
func QueryComposer() {
    // No test - Cursor will suggest adding test
}
```

---

## 🚀 **DEPLOYMENT ENFORCEMENT**

### ✅ **Production Readiness Checks**

#### **Main CLI**
- `interactive_cli.go` must be production ready
- All features must be implemented
- All errors must be handled
- All documentation must be complete

#### **Core Engine**
- `interactive_search_engine.go` must be production ready
- All algorithms must be working
- All performance targets must be met
- All tests must pass

### 🚫 **Deployment Blockers**

- Test files in root directory
- Example files in root directory
- Debug files in root directory
- Failing tests
- Compilation errors
- Missing documentation

---

## 📊 **METRICS MONITORING**

### ✅ **Track These Metrics**

#### **Folder Structure Compliance**
- Target: 100%
- Check: All files in correct directories
- Monitor: Root directory cleanliness

#### **File Naming Compliance**
- Target: 100%
- Check: All files follow naming conventions
- Monitor: Consistent naming patterns

#### **Code Quality Score**
- Target: >90%
- Check: Linting, formatting, testing
- Monitor: Code quality trends

#### **Test Coverage**
- Target: >80%
- Check: All code paths tested
- Monitor: Test coverage trends

#### **Documentation Coverage**
- Target: 100%
- Check: All files documented
- Monitor: Documentation completeness

---

## 🎯 **USAGE EXAMPLES**

### **Example 1: Adding a New Test File**

```bash
# ❌ WRONG - Cursor will warn
touch test_new_algorithm.go

# ✅ CORRECT - Cursor will approve
touch test_scripts/test_new_algorithm.go
```

### **Example 2: Adding a New Example File**

```bash
# ❌ WRONG - Cursor will warn
touch demo_new_feature.go

# ✅ CORRECT - Cursor will approve
touch example_scripts/demo_new_feature.go
```

### **Example 3: Adding a New Debug File**

```bash
# ❌ WRONG - Cursor will warn
touch debug_new_issue.go

# ✅ CORRECT - Cursor will approve
touch temp_files/debug_new_issue.go
```

---

## 🔄 **WORKFLOW INTEGRATION**

### **1. Development Workflow**
1. Create files in correct directories
2. Follow naming conventions
3. Add proper documentation
4. Write tests
5. Run quality checks
6. Commit changes

### **2. Maintenance Workflow**
1. Weekly cleanup of temp_files/
2. Review and organize test_scripts/
3. Review and organize example_scripts/
4. Update documentation
5. Run full test suite
6. Update changelog

### **3. Release Workflow**
1. Ensure all rules are followed
2. Run all tests
3. Update documentation
4. Update changelog
5. Create release
6. Tag version

---

## 🎉 **SUCCESS INDICATORS**

**You're following the rules correctly when:**
- ✅ Cursor shows green suggestions
- ✅ No red warnings
- ✅ All files in correct directories
- ✅ All files follow naming conventions
- ✅ All tests pass
- ✅ All documentation is complete
- ✅ Root directory is clean
- ✅ Code quality is high

**🚀 MAINTAIN THIS STANDARD AT ALL TIMES!**

---

*Generated by AI Assistant - API-MCP-Simbiosis Project*  
*Cursor Rules Guide v1.0.0 - Folder Structure Maintenance*
