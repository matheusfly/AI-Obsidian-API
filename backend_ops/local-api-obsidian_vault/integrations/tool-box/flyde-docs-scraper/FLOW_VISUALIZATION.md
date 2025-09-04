# 🎨 Flyde Hello World Flow Visualization

## Visual Flow Structure

```
┌─────────────┐    ┌─────────────────┐    ┌─────────────────┐
│    Start    │───▶│   Target URL     │───▶│   Scrape URL     │
│   Trigger   │    │  (blog-generator)│    │   (scrapfly)     │
└─────────────┘    └─────────────────┘    └─────────────────┘
       │                     │                       │
       │                     │                       │
       ▼                     ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Scraper Type    │───▶│   Extract Text   │    │  Extract Links   │
│   (scrapfly)     │    │  (HTML → Text)   │    │  (Find URLs)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                       │
                                                       │
                                                       ▼
                                              ┌─────────────────┐
                                              │   Save Result    │
                                              │  (JSON File)     │
                                              └─────────────────┘
                                                       │
                                                       ▼
                                              ┌─────────────────┐
                                              │ Display Result  │
                                              │  (Summary)      │
                                              └─────────────────┘
```

## Flow Description

### 1. **Start Trigger** 🚀
- Initiates the flow execution
- Provides the trigger signal to begin scraping

### 2. **Target URL** 🎯
- Contains the URL: `https://flyde.dev/playground/blog-generator`
- This is the Flyde blog generator playground page

### 3. **Scraper Selector** ⚙️
- Chooses which scraping engine to use
- Options: `scrapfly`, `playwright`, `scrapy`
- Default: `scrapfly`

### 4. **Scrape URL** 🌐
- Executes the web scraping
- Uses the selected scraper to fetch the page content
- Returns HTML content and metadata

### 5. **Extract Text** 📝
- Processes the HTML content
- Removes HTML tags and formatting
- Extracts clean, readable text

### 6. **Extract Links** 🔗
- Finds all links in the HTML content
- Converts relative URLs to absolute URLs
- Removes duplicate links

### 7. **Save Result** 💾
- Combines all extracted data
- Saves to a JSON file with timestamp
- Stores in the `data/` directory

### 8. **Display Result** 📊
- Shows a summary of the scraping operation
- Displays statistics and preview
- Confirms successful completion

## How to Run

### Option 1: Command Line
```powershell
.\launch_flyde_flow.ps1
```

### Option 2: VS Code Extension
1. Install the Flyde VS Code extension
2. Open `flows/hello-world.flyde`
3. Use "Flyde: Test Flow" command
4. Watch the visual execution in real-time

### Option 3: Node.js Direct
```bash
node run_flyde_flow.js
```

## Expected Output

When you run this flow, you'll see:

```
🚀 Running Flyde Hello World Flow...
Target URL: https://flyde.dev/playground/blog-generator

✅ Flow completed successfully!
📊 Results:
{
  "output": {
    "message": "🎉 Hello World Scraping Completed!",
    "filename": "hello-world-result-2025-01-09T14-30-22-123Z.json",
    "url": "https://flyde.dev/playground/blog-generator",
    "scraper": "scrapfly",
    "statistics": {
      "content_length": 15420,
      "text_length": 3240,
      "links_found": 15
    },
    "preview": {
      "text_preview": "Flyde Playground - Blog Generator. Create beautiful blog posts with AI...",
      "first_links": [
        "https://flyde.dev/docs",
        "https://flyde.dev/playground",
        "https://github.com/flydelabs/flyde"
      ]
    }
  }
}
```

## Visual Flow Benefits

1. **Visual Debugging** 👁️
   - See data flow between nodes in real-time
   - Identify bottlenecks and errors visually
   - Understand the scraping process step-by-step

2. **Easy Modification** 🔧
   - Change target URL by editing the value node
   - Switch scrapers by modifying the selector
   - Add new processing steps visually

3. **Reusable Components** ♻️
   - Each node can be reused in other flows
   - Create custom nodes for specific scraping tasks
   - Build complex scraping pipelines

4. **Real-time Monitoring** 📈
   - Watch data transformation as it happens
   - See intermediate results at each step
   - Debug issues with visual feedback

## Next Steps

1. **Open in VS Code**: Install Flyde extension and open the flow
2. **Test the Flow**: Use "Flyde: Test Flow" to run it visually
3. **Modify**: Change URLs, scrapers, or add new processing steps
4. **Extend**: Create more complex flows for different scraping tasks

This visual flow demonstrates how Flyde makes web scraping accessible and understandable through visual programming! 🎉