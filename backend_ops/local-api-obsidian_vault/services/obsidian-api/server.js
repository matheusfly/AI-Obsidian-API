const express = require('express');
const cors = require('cors');
const fs = require('fs-extra');
const path = require('path');

const app = express();
const PORT = process.env.API_PORT || 27123;
const VAULT_PATH = process.env.VAULT_PATH || '/vault';

app.use(cors());
app.use(express.json());

// Health check
app.get('/health', (req, res) => {
    res.json({ status: 'healthy', timestamp: new Date().toISOString() });
});

// Get vault info
app.get('/vault/info', async (req, res) => {
    try {
        const stats = await fs.stat(VAULT_PATH);
        const files = await fs.readdir(VAULT_PATH);
        const mdFiles = files.filter(f => f.endsWith('.md'));
        
        res.json({
            path: VAULT_PATH,
            exists: true,
            totalFiles: files.length,
            markdownFiles: mdFiles.length,
            lastModified: stats.mtime
        });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// List files
app.get('/files', async (req, res) => {
    try {
        const folderPath = req.query.path || '';
        const fullPath = path.join(VAULT_PATH, folderPath);
        
        const files = await fs.readdir(fullPath);
        const fileList = [];
        
        for (const file of files) {
            const filePath = path.join(fullPath, file);
            const stats = await fs.stat(filePath);
            
            fileList.push({
                name: file,
                path: path.join(folderPath, file).replace(/\\/g, '/'),
                isDirectory: stats.isDirectory(),
                size: stats.size,
                modified: stats.mtime
            });
        }
        
        res.json({ files: fileList, path: folderPath });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Read file
app.get('/files/*', async (req, res) => {
    try {
        const filePath = req.params[0];
        const fullPath = path.join(VAULT_PATH, filePath);
        
        const content = await fs.readFile(fullPath, 'utf8');
        const stats = await fs.stat(fullPath);
        
        res.json({
            path: filePath,
            content: content,
            size: stats.size,
            modified: stats.mtime
        });
    } catch (error) {
        res.status(404).json({ error: 'File not found' });
    }
});

// Create/Update file
app.post('/files', async (req, res) => {
    try {
        const { path: filePath, content } = req.body;
        const fullPath = path.join(VAULT_PATH, filePath);
        
        await fs.ensureDir(path.dirname(fullPath));
        await fs.writeFile(fullPath, content, 'utf8');
        
        res.json({ success: true, path: filePath, message: 'File created/updated' });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Search vault
app.post('/vault/search', async (req, res) => {
    try {
        const { query, caseSensitive = false } = req.body;
        const results = [];
        
        const searchFiles = async (dir) => {
            const files = await fs.readdir(dir);
            
            for (const file of files) {
                const filePath = path.join(dir, file);
                const stats = await fs.stat(filePath);
                
                if (stats.isDirectory()) {
                    await searchFiles(filePath);
                } else if (file.endsWith('.md')) {
                    const content = await fs.readFile(filePath, 'utf8');
                    const searchText = caseSensitive ? content : content.toLowerCase();
                    const searchQuery = caseSensitive ? query : query.toLowerCase();
                    
                    if (searchText.includes(searchQuery)) {
                        const relativePath = path.relative(VAULT_PATH, filePath).replace(/\\/g, '/');
                        results.push({
                            path: relativePath,
                            name: file,
                            matches: (content.match(new RegExp(query, caseSensitive ? 'g' : 'gi')) || []).length
                        });
                    }
                }
            }
        };
        
        await searchFiles(VAULT_PATH);
        res.json({ query, results, total: results.length });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

app.listen(PORT, '0.0.0.0', () => {
    console.log(`Obsidian API server running on port ${PORT}`);
    console.log(`Vault path: ${VAULT_PATH}`);
});