# 🚀 CLI Quick Reference Card

## ⚡ Essential Commands

### 🎯 Quick Start
```powershell
.\plugins.ps1 -Help                    # Show help
.\plugins.ps1 -Version                 # Show version
.\plugins.ps1 -Interactive             # Enter interactive mode
.\plugins.ps1 status                   # Show current status
```

### 🏗️ Setup
```powershell
.\plugins.ps1 setup flyde [name]       # Setup Flyde
.\plugins.ps1 setup motia [name]       # Setup Motia
.\plugins.ps1 setup both [name]        # Setup both
```

### 🎨 Launch
```powershell
.\plugins.ps1 launch flyde [port]      # Launch Flyde Studio
.\plugins.ps1 launch motia [port]      # Launch Motia Dev Server
.\plugins.ps1 launch both [flyde-port] [motia-port] # Launch both
```

### 🔄 Execute
```powershell
.\plugins.ps1 run flyde [flow] [input] [output]    # Run Flyde flow
.\plugins.ps1 run motia [step] [input] [output]    # Run Motia step
```

### 🧪 Test
```powershell
.\plugins.ps1 test flyde [flow]        # Test Flyde flow
.\plugins.ps1 test motia [step]        # Test Motia step
.\plugins.ps1 test all                 # Test everything
```

### 📦 Build
```powershell
.\plugins.ps1 build flyde [output]     # Build Flyde
.\plugins.ps1 build motia [output]     # Build Motia
.\plugins.ps1 build all [output]       # Build both
```

### 🔍 Analyze
```powershell
.\plugins.ps1 analyze flyde [flow]     # Analyze Flyde
.\plugins.ps1 analyze motia [step]     # Analyze Motia
.\plugins.ps1 analyze all              # Analyze all
```

### 📊 Monitor
```powershell
.\plugins.ps1 monitor flyde [endpoint] # Monitor Flyde
.\plugins.ps1 monitor motia [endpoint] # Monitor Motia
.\plugins.ps1 monitor all              # Monitor both
```

### 🚀 Deploy
```powershell
.\plugins.ps1 deploy flyde [target] [env]  # Deploy Flyde
.\plugins.ps1 deploy motia [target] [env]  # Deploy Motia
.\plugins.ps1 deploy all [target] [env]    # Deploy both
```

### 🔧 Utilities
```powershell
.\plugins.ps1 clean                    # Clean artifacts
.\plugins.ps1 update                   # Update dependencies
```

---

## 🎮 Interactive Mode Commands

```powershell
plugins> help                          # Show help
plugins> status                        # Show status
plugins> setup flyde my-project        # Setup Flyde
plugins> setup motia my-project        # Setup Motia
plugins> launch both                   # Launch both tools
plugins> run flyde                     # Run default flow
plugins> run motia                     # Run default step
plugins> test all                      # Test everything
plugins> build all dist/               # Build for production
plugins> analyze all                   # Analyze all
plugins> monitor all                   # Monitor performance
plugins> deploy all vercel prod        # Deploy to production
plugins> clean                         # Clean artifacts
plugins> update                        # Update dependencies
plugins> exit                          # Exit interactive mode
```

---

## 🎯 Common Workflows

### 🚀 Complete Development Setup
```powershell
.\plugins.ps1 setup both my-project
.\plugins.ps1 launch both
.\plugins.ps1 test all
```

### 🔄 Development Cycle
```powershell
.\plugins.ps1 run flyde flows/hello.flyde
.\plugins.ps1 run motia steps/hello.step.ts
.\plugins.ps1 test all
.\plugins.ps1 build all dist/
```

### 🚀 Production Deployment
```powershell
.\plugins.ps1 test all
.\plugins.ps1 build all dist/
.\plugins.ps1 deploy all vercel production
```

---

## 🔧 Troubleshooting

### 🚨 Quick Fixes
```powershell
.\plugins.ps1 status                   # Check status
.\plugins.ps1 clean                    # Clean artifacts
.\plugins.ps1 update                   # Update dependencies
```

### 🐛 Debug Commands
```powershell
$env:DEBUG="*"                         # Enable debug mode
.\plugins.ps1 launch flyde             # Launch with debug
.\plugins.ps1 run flyde -Verbose       # Verbose execution
```

### 🔍 Port Issues
```powershell
netstat -an | findstr :3000            # Check port 3000
netstat -an | findstr :3001            # Check port 3001
Get-Process -Name node | Stop-Process -Force  # Kill Node processes
```

---

## 📊 Status Indicators

| Status | Meaning |
|--------|---------|
| ✅ | Success/Running |
| ❌ | Error/Not Found |
| ⚠️ | Warning |
| 🔴 | Port In Use |
| 🟢 | Port Available |
| 📦 | Installing |
| 🚀 | Launching |
| 🔄 | Executing |
| 🧪 | Testing |
| 📦 | Building |
| 🔍 | Analyzing |
| 📊 | Monitoring |
| 🚀 | Deploying |

---

## 🎯 Default Values

| Parameter | Default Value |
|-----------|---------------|
| Flyde Port | 3001 |
| Motia Port | 3000 |
| Host | localhost |
| Project Name | flyde-project / motia-project |
| Output Directory | dist/ |
| Environment | production |
| Target | vercel |

---

## 🚀 Pro Tips

1. **Use interactive mode** for development workflow
2. **Check status first** before running commands
3. **Test frequently** during development
4. **Monitor performance** in production
5. **Clean artifacts** regularly
6. **Update dependencies** monthly
7. **Use custom ports** to avoid conflicts
8. **Document custom configurations**
9. **Backup before major changes**
10. **Use version control** for all projects

---

## 📞 Support

- **Help**: `.\plugins.ps1 -Help`
- **Version**: `.\plugins.ps1 -Version`
- **Status**: `.\plugins.ps1 status`
- **Interactive**: `.\plugins.ps1 -Interactive`

This quick reference card provides instant access to all essential CLI commands and workflows for Flyde and Motia management.
