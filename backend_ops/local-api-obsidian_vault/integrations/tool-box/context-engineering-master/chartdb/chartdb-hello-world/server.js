const express = require('express');
const cors = require('cors');
const WebSocket = require('ws');
const path = require('path');

const app = express();
const PORT = 3001;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static('public'));

// Sample data for interactive nodes
const sampleData = {
  nodes: [
    { id: 1, label: 'Hello World', group: 'start', x: 100, y: 100, color: '#FF6B6B' },
    { id: 2, label: 'Data Input', group: 'input', x: 300, y: 100, color: '#4ECDC4' },
    { id: 3, label: 'Process', group: 'process', x: 500, y: 100, color: '#45B7D1' },
    { id: 4, label: 'Visualize', group: 'output', x: 700, y: 100, color: '#96CEB4' },
    { id: 5, label: 'Result', group: 'end', x: 900, y: 100, color: '#FFEAA7' }
  ],
  edges: [
    { from: 1, to: 2, label: 'start' },
    { from: 2, to: 3, label: 'process' },
    { from: 3, to: 4, label: 'visualize' },
    { from: 4, to: 5, label: 'complete' }
  ],
  charts: [
    {
      id: 'hello-chart',
      type: 'bar',
      title: 'Hello World Data',
      data: {
        labels: ['Node 1', 'Node 2', 'Node 3', 'Node 4', 'Node 5'],
        datasets: [{
          label: 'Activity Level',
          data: [12, 19, 3, 5, 2],
          backgroundColor: ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
        }]
      }
    },
    {
      id: 'network-chart',
      type: 'network',
      title: 'Interactive Network',
      data: {
        nodes: [
          { id: 'A', label: 'Start', group: 'start' },
          { id: 'B', label: 'Process', group: 'process' },
          { id: 'C', label: 'Visualize', group: 'output' },
          { id: 'D', label: 'End', group: 'end' }
        ],
        edges: [
          { from: 'A', to: 'B' },
          { from: 'B', to: 'C' },
          { from: 'C', to: 'D' }
        ]
      }
    }
  ]
};

// API Routes
app.get('/api/hello', (req, res) => {
  res.json({ 
    message: 'Hello from ChartDB Interactive World!', 
    timestamp: new Date().toISOString(),
    features: ['Interactive Nodes', 'Real-time Updates', 'Visual Charts', 'Network Graphs']
  });
});

app.get('/api/nodes', (req, res) => {
  res.json(sampleData);
});

app.get('/api/charts', (req, res) => {
  res.json(sampleData.charts);
});

app.post('/api/nodes/:id/click', (req, res) => {
  const nodeId = parseInt(req.params.id);
  const node = sampleData.nodes.find(n => n.id === nodeId);
  
  if (node) {
    // Simulate node interaction
    node.clicked = true;
    node.clickCount = (node.clickCount || 0) + 1;
    
    // Broadcast update to all connected clients
    wss.clients.forEach(client => {
      if (client.readyState === WebSocket.OPEN) {
        client.send(JSON.stringify({
          type: 'node_clicked',
          nodeId: nodeId,
          node: node
        }));
      }
    });
    
    res.json({ success: true, node: node });
  } else {
    res.status(404).json({ error: 'Node not found' });
  }
});

app.post('/api/nodes/:id/update', (req, res) => {
  const nodeId = parseInt(req.params.id);
  const updates = req.body;
  
  const node = sampleData.nodes.find(n => n.id === nodeId);
  if (node) {
    Object.assign(node, updates);
    
    // Broadcast update
    wss.clients.forEach(client => {
      if (client.readyState === WebSocket.OPEN) {
        client.send(JSON.stringify({
          type: 'node_updated',
          nodeId: nodeId,
          node: node
        }));
      }
    });
    
    res.json({ success: true, node: node });
  } else {
    res.status(404).json({ error: 'Node not found' });
  }
});

// WebSocket server
const server = require('http').createServer(app);
const wss = new WebSocket.Server({ server });

wss.on('connection', (ws) => {
  console.log('Client connected to ChartDB Hello World');
  
  // Send initial data
  ws.send(JSON.stringify({
    type: 'initial_data',
    data: sampleData
  }));
  
  ws.on('message', (message) => {
    try {
      const data = JSON.parse(message);
      console.log('Received:', data);
      
      // Echo back to all clients
      wss.clients.forEach(client => {
        if (client.readyState === WebSocket.OPEN) {
          client.send(JSON.stringify({
            type: 'broadcast',
            data: data
          }));
        }
      });
    } catch (error) {
      console.error('Error parsing message:', error);
    }
  });
  
  ws.on('close', () => {
    console.log('Client disconnected from ChartDB Hello World');
  });
});

// Start server
server.listen(PORT, () => {
  console.log(`🚀 ChartDB Hello World server running on http://localhost:${PORT}`);
  console.log(`📊 Interactive UI available at http://localhost:${PORT}`);
  console.log(`🔌 WebSocket server ready for real-time updates`);
});
