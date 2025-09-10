# 🧪 **TESTING RULES - NO SUCCESS REPORTS WITHOUT ACTUAL TESTING**

## 🚨 **CRITICAL RULE: TEST FIRST, REPORT AFTER**

### **❌ FORBIDDEN ACTIONS**
- **NO** success reports without actual testing
- **NO** "implementation complete" claims without verification
- **NO** theoretical-only responses
- **NO** assuming correctness without verification

### **✅ REQUIRED ACTIONS**
1. **TEST FIRST** - Always run actual tests before claiming success
2. **VERIFY RESULTS** - Confirm functionality works as expected
3. **SHOW EVIDENCE** - Provide actual output/proof of working functionality
4. **REPORT REALITY** - Only report what has been actually tested and verified

## 🎯 **TESTING WORKFLOW**

### **1. Implementation Phase**
- Write code/configuration
- **IMMEDIATELY** test functionality
- Fix any issues found
- **ONLY THEN** proceed to next step

### **2. Verification Phase**
- Run actual tests
- Verify endpoints respond correctly
- Confirm LLM calls work
- Test error handling

### **3. Reporting Phase**
- **ONLY** after successful testing
- Include actual test results
- Show real output/evidence
- Report actual performance metrics

## 🔧 **LLM TESTING REQUIREMENTS**

### **Before claiming LLM integration works:**
1. ✅ Test API key is set
2. ✅ Test Gemini library imports
3. ✅ Test actual API call
4. ✅ Verify response received
5. ✅ Test error handling

### **Example of CORRECT approach:**
```python
# Test first
response = model.generate_content("test")
print(f"Response: {response.text}")  # Show actual result

# Only then report success
print("✅ LLM integration working!")
```

### **Example of WRONG approach:**
```python
# Don't do this - no actual testing
print("✅ LLM integration complete!")
```

## 📊 **SUCCESS CRITERIA**

### **A feature is only "complete" when:**
- ✅ Code is written
- ✅ Tests are run
- ✅ Results are verified
- ✅ Evidence is shown
- ✅ Functionality is confirmed working

### **No shortcuts allowed:**
- No "assumed working" status
- No theoretical implementations
- No success reports without testing
- No claims without evidence

## 🎯 **ENFORCEMENT**

### **When user says "test it":**
1. **STOP** all reporting
2. **RUN** actual tests
3. **SHOW** real results
4. **FIX** any issues found
5. **ONLY THEN** report status

### **When user says "overtime" or "nothing":**
- This means testing failed
- **IMMEDIATELY** debug the issue
- **RUN** actual tests to find problems
- **FIX** before proceeding

## 🚀 **GOAL: REAL WORKING FUNCTIONALITY**

The goal is not to write reports about working systems, but to **ACTUALLY CREATE WORKING SYSTEMS** that have been tested and verified.

**Remember: Test first, report after!**
