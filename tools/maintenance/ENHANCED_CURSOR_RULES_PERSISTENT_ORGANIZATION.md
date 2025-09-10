# 🎯 **ENHANCED CURSOR RULES - PERSISTENT FILE ORGANIZATION**

**Version:** 3.0.0  
**Last Updated:** September 6, 2025  
**Status:** ✅ **ACTIVE RULES**

---

## 📋 **RULE OVERVIEW**

This document defines enhanced cursor rules for persistent file and folder organization, ensuring that all files are properly categorized, temp files are managed efficiently, and the project structure remains clean and organized at all times.

---

## 🔧 **CORE ORGANIZATION RULES**

### **Rule 1: Mandatory File Organization**
```
ALWAYS organize files according to project structure:
- Core logic → core_services/
- Monitoring tools → monitoring_tools/
- Test files → test_suites/
- Documentation → docs/ or documentation/
- Deployment scripts → deployment/
- Examples → examples/
- Requirements → requirements/
- Temporary files → temp_files/ with appropriate subfolders
- Reports → reports/ with proper categorization
- Cleanup tools → cleanup_system/
- MCP tools → mcp_tools/
- LangGraph workflows → langgraph_workflows/
```

### **Rule 2: Temp File Management**
```
MANDATORY: All temporary files must be organized:
- Active tests → scripts/temp/active_tests/[feature_name]/
- Feature development → scripts/temp/feature_development/[feature_name]/
- Experimental code → scripts/temp/experimental/
- Generated scripts → scripts/temp/generated_scripts/
- Backup files → scripts/temp/backup/
- Logs → temp_files/logs/[feature_name]/
- Reports → temp_files/reports/[feature_name]/
- Test results → temp_files/test_results/[feature_name]/
```

### **Rule 3: Feature-Based Organization**
```
REQUIRE: For each new feature being tested:
1. Create feature-specific temp folders
2. Use consistent naming: [feature_name]
3. Organize all related files in feature folders
4. Move to definitive locations when feature is complete
5. Clean up temp files after feature completion
```

---

## 🚀 **IMPLEMENTATION RULES**

### **Rule 4: Task Start Workflow**
```
MANDATORY workflow when starting any task:
1. Identify if this is a new feature or existing work
2. If new feature: Run persistent_file_organization.ps1 -Action create_temp -FeatureName [feature_name]
3. Create appropriate temp folder structure
4. Document the feature being developed
5. Set up proper file organization from the start
```

### **Rule 5: Task Completion Workflow**
```
MANDATORY workflow when completing any task:
1. Complete the main task
2. Run persistent_file_organization.ps1 -Action move_to_definitive -FeatureName [feature_name]
3. Move files from temp to definitive locations
4. Clean up temporary files
5. Run comprehensive_cleanup.ps1 for final organization
6. Generate success report
7. Update changelog
8. Include "CENTRALIZED REPORTS & CHANGELOG SYSTEM COMPLETE!" in summary
```

### **Rule 6: Ongoing Maintenance Workflow**
```
REQUIRE: Regular maintenance workflow:
1. Daily: Run persistent_file_organization.ps1 -Action organize
2. Weekly: Run comprehensive_cleanup.ps1
3. Monthly: Deep cleanup and organization review
4. Per feature: Clean up temp files after feature completion
```

---

## 📁 **FOLDER STRUCTURE RULES**

### **Rule 7: Root Directory Cleanliness**
```
ENFORCE: Root directory must contain only:
- Essential configuration files (README.md, docker-compose.yml, etc.)
- Core project files (requirements.txt, pyproject.toml, etc.)
- Main documentation (PROJECT_ORGANIZATION.md)
- NO temporary files
- NO test files
- NO development scripts
- NO generated reports
```

### **Rule 8: Scripts Directory Organization**
```
REQUIRE: Scripts directory structure:
scripts/
├── temp/                          # Temporary scripts
│   ├── active_tests/              # Active testing scripts
│   │   └── [feature_name]/        # Feature-specific test scripts
│   ├── feature_development/       # Feature development scripts
│   │   └── [feature_name]/        # Feature-specific dev scripts
│   ├── experimental/              # Experimental scripts
│   ├── backup/                    # Backup scripts
│   └── generated_scripts/         # Auto-generated scripts
└── [definitive_scripts]           # Only essential, permanent scripts
```

### **Rule 9: Temp Files Directory Organization**
```
REQUIRE: Temp files directory structure:
temp_files/
├── logs/                          # Temporary log files
│   └── [feature_name]/            # Feature-specific logs
├── reports/                       # Temporary report files
│   └── [feature_name]/            # Feature-specific reports
├── test_results/                  # Temporary test results
│   └── [feature_name]/            # Feature-specific test results
├── json_data/                     # Temporary JSON data
├── scripts/                       # Temporary scripts
└── backup/                        # Backup files
```

---

## 🔄 **AUTOMATION RULES**

### **Rule 10: Automated Organization**
```
ENABLE: Automated organization for:
- New file creation (immediate categorization)
- Feature development (temp folder creation)
- Feature completion (move to definitive locations)
- Regular cleanup (temp file removal)
- Project maintenance (structure validation)
```

### **Rule 11: Feature Lifecycle Management**
```
IMPLEMENT: Feature lifecycle management:
1. Feature Start: Create temp folders, document feature
2. Feature Development: Organize files in temp folders
3. Feature Testing: Use active_tests folders
4. Feature Completion: Move to definitive locations
5. Feature Cleanup: Remove temp files, update documentation
```

### **Rule 12: File Naming Conventions**
```
ENFORCE: Consistent file naming:
- Python files: snake_case.py
- PowerShell files: kebab-case.ps1
- Markdown files: UPPER_CASE.md
- Configuration files: lowercase.ext
- Test files: test_*.py or *_test.py
- Feature files: [feature_name]_*.ext
```

---

## 🧹 **CLEANUP RULES**

### **Rule 13: Temp File Cleanup**
```
REQUIRE: Regular temp file cleanup:
- Daily: Clean old temp files (7+ days)
- Weekly: Clean feature-specific temp files
- Monthly: Deep cleanup of all temp directories
- Per feature: Clean up after feature completion
```

### **Rule 14: File Movement Rules**
```
ENFORCE: File movement rules:
- Temp → Definitive: Only when feature is complete
- Root → Appropriate folder: Immediately
- Duplicate files: Remove duplicates, keep best version
- Empty folders: Remove after cleanup
```

### **Rule 15: Backup Management**
```
MAINTAIN: Backup management:
- All deletions backed up before removal
- Timestamped backup directories
- Regular backup cleanup (90+ days)
- Easy recovery process
```

---

## 📊 **REPORTING RULES**

### **Rule 16: Organization Reports**
```
GENERATE: Organization reports for:
- File organization operations
- Temp file cleanup operations
- Feature completion operations
- Structure validation operations
- Maintenance operations
```

### **Rule 17: Feature Reports**
```
REQUIRE: Feature reports for:
- Feature start (temp folder creation)
- Feature progress (file organization status)
- Feature completion (move to definitive)
- Feature cleanup (temp file removal)
```

### **Rule 18: Maintenance Reports**
```
MAINTAIN: Maintenance reports for:
- Daily organization operations
- Weekly cleanup operations
- Monthly deep cleanup
- Structure health metrics
- File organization statistics
```

---

## 🔧 **TOOL USAGE RULES**

### **Rule 19: Organization Tool Usage**
```
USE organization tools in this order:
1. persistent_file_organization.ps1 -Action create_temp -FeatureName [name]
2. [develop feature with organized temp files]
3. persistent_file_organization.ps1 -Action move_to_definitive -FeatureName [name]
4. comprehensive_cleanup.ps1
5. Generate reports and update changelog
```

### **Rule 20: Cleanup Tool Usage**
```
USE cleanup tools in this order:
1. persistent_file_organization.ps1 -Action organize
2. comprehensive_cleanup.ps1 -DryRun -Detailed
3. comprehensive_cleanup.ps1 -Detailed
4. targeted_cleanup.ps1 (if needed)
5. Generate cleanup reports
```

---

## 🎯 **QUALITY ASSURANCE RULES**

### **Rule 21: Organization Validation**
```
VALIDATE: Every organization operation must:
- Preserve essential files
- Maintain project structure
- Follow naming conventions
- Clean up temp files appropriately
- Generate proper reports
```

### **Rule 22: Feature Validation**
```
ENSURE: Every feature development must:
- Use proper temp folder structure
- Follow naming conventions
- Organize files appropriately
- Clean up after completion
- Update documentation
```

### **Rule 23: Structure Validation**
```
VERIFY: Project structure must:
- Follow established patterns
- Maintain clean organization
- Support easy navigation
- Enable efficient maintenance
- Scale with project growth
```

---

## 📝 **TEMPLATE RULES**

### **Rule 24: Feature Start Template**
```
USE this template when starting a new feature:
1. Run: .\cleanup_system\persistent_file_organization.ps1 -Action create_temp -FeatureName [feature_name]
2. Create feature documentation in temp folder
3. Set up proper file organization
4. Document feature requirements
5. Begin development with organized structure
```

### **Rule 25: Feature Completion Template**
```
USE this template when completing a feature:
1. Complete feature development
2. Run: .\cleanup_system\persistent_file_organization.ps1 -Action move_to_definitive -FeatureName [feature_name]
3. Run: .\cleanup_system\comprehensive_cleanup.ps1
4. Generate success report
5. Update changelog
6. Include "CENTRALIZED REPORTS & CHANGELOG SYSTEM COMPLETE!"
```

---

## 🚨 **ENFORCEMENT RULES**

### **Rule 26: Non-Compliance Handling**
```
IF organization rules are not followed:
- Stop current operation
- Run organization tools
- Fix file structure
- Generate proper reports
- Complete with proper organization
```

### **Rule 27: Quality Enforcement**
```
ENFORCE: All organization operations must meet quality standards:
- Zero data loss
- Proper file categorization
- Clean project structure
- Complete documentation
- Accurate reporting
```

---

## 📚 **REFERENCE RULES**

### **Rule 28: Documentation References**
```
ALWAYS reference these documents:
- cleanup_system/README.md - Tool documentation
- FOLDER_STRUCTURE_GUIDE.md - Structure management
- persistent_file_organization.ps1 - Organization tool
- cleanup_config.ps1 - Configuration settings
- PROJECT_ORGANIZATION.md - Project structure guide
```

### **Rule 29: Tool References**
```
ALWAYS use these tools:
- persistent_file_organization.ps1 - Main organization tool
- comprehensive_cleanup.ps1 - Main cleanup tool
- master_cleanup.ps1 - Orchestrated cleanup
- organize_remaining_files.ps1 - Remaining files organization
```

---

## 🎯 **SUCCESS CRITERIA**

### **Rule 30: Organization Success Criteria**
```
ORGANIZATION is successful when:
- All files properly categorized
- Temp files organized by feature
- Root directory clean
- Project structure maintained
- Documentation updated
- Reports generated
```

### **Rule 31: Feature Success Criteria**
```
FEATURE is successful when:
- Proper temp folder structure
- Files organized during development
- Moved to definitive locations on completion
- Temp files cleaned up
- Documentation updated
- Reports generated
```

---

## 🔄 **CONTINUOUS IMPROVEMENT RULES**

### **Rule 32: Regular Updates**
```
UPDATE regularly:
- Organization tools
- Folder structure rules
- Naming conventions
- Cleanup procedures
- Documentation
- Reports
```

### **Rule 33: Feedback Integration**
```
INTEGRATE feedback:
- User suggestions
- Organization improvements
- Tool enhancements
- Process optimizations
- Documentation updates
```

---

## 🎉 **FINAL RULES**

### **Rule 34: Mandatory Completion Phrase**
```
MANDATORY: Every task completion must end with:
"CENTRALIZED REPORTS & CHANGELOG SYSTEM COMPLETE!"

This phrase confirms:
- Cleanup system executed
- Files properly organized
- Reports generated
- Changelog updated
- System organized
- Documentation complete
```

### **Rule 35: Persistent Organization Commitment**
```
COMMIT to persistent organization:
- Always organize files properly
- Use temp folders for development
- Move to definitive locations when complete
- Clean up temp files regularly
- Maintain clean project structure
- Generate proper reports
- Update documentation
```

---

*Generated by AI Assistant - Data Vault Obsidian Project*  
*Enhanced Cursor Rules for Persistent File Organization v3.0.0*
