import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { CssBaseline, Box, AppBar, Toolbar, Typography, IconButton, Drawer, List, ListItem, ListItemIcon, ListItemText, Alert, Snackbar } from '@mui/material';
import { Menu as MenuIcon, Dashboard, Note, Search, Settings, Analytics, Api } from '@mui/icons-material';

import Dashboard from './pages/Dashboard';
import NotesManager from './pages/NotesManager';
import SearchInterface from './pages/SearchInterface';
import APITesting from './pages/APITesting';
import Analytics from './pages/Analytics';
import Settings from './pages/Settings';
import { apiService } from './services/apiService';

const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: { main: '#6366f1' },
    secondary: { main: '#f59e0b' },
    background: { default: '#0f172a', paper: '#1e293b' }
  }
});

const drawerWidth = 240;

function App() {
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [systemHealth, setSystemHealth] = useState(null);
  const [notification, setNotification] = useState({ open: false, message: '', severity: 'info' });

  const menuItems = [
    { text: 'Dashboard', icon: <Dashboard />, path: '/dashboard' },
    { text: 'Notes', icon: <Note />, path: '/notes' },
    { text: 'Search', icon: <Search />, path: '/search' },
    { text: 'API Testing', icon: <Api />, path: '/api' },
    { text: 'Analytics', icon: <Analytics />, path: '/analytics' },
    { text: 'Settings', icon: <Settings />, path: '/settings' }
  ];

  useEffect(() => {
    checkSystemHealth();
    const interval = setInterval(checkSystemHealth, 30000); // Check every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const checkSystemHealth = async () => {
    try {
      const health = await apiService.getHealth();
      setSystemHealth(health);
      if (health.status !== 'healthy') {
        showNotification('System health issues detected', 'warning');
      }
    } catch (error) {
      setSystemHealth({ status: 'error', message: error.message });
      showNotification('Cannot connect to backend services', 'error');
    }
  };

  const showNotification = (message, severity = 'info') => {
    setNotification({ open: true, message, severity });
  };

  const handleDrawerToggle = () => {
    setDrawerOpen(!drawerOpen);
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Box sx={{ display: 'flex' }}>
          <AppBar position="fixed" sx={{ zIndex: theme.zIndex.drawer + 1 }}>
            <Toolbar>
              <IconButton color="inherit" edge="start" onClick={handleDrawerToggle} sx={{ mr: 2 }}>
                <MenuIcon />
              </IconButton>
              <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
                Obsidian Vault AI System
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Box
                  sx={{
                    width: 12,
                    height: 12,
                    borderRadius: '50%',
                    backgroundColor: systemHealth?.status === 'healthy' ? 'success.main' : 'error.main'
                  }}
                />
                <Typography variant="body2">
                  {systemHealth?.status === 'healthy' ? 'Online' : 'Offline'}
                </Typography>
              </Box>
            </Toolbar>
          </AppBar>

          <Drawer
            variant="temporary"
            open={drawerOpen}
            onClose={handleDrawerToggle}
            sx={{
              width: drawerWidth,
              flexShrink: 0,
              '& .MuiDrawer-paper': { width: drawerWidth, boxSizing: 'border-box' }
            }}
          >
            <Toolbar />
            <Box sx={{ overflow: 'auto' }}>
              <List>
                {menuItems.map((item) => (
                  <ListItem button key={item.text} component="a" href={item.path}>
                    <ListItemIcon>{item.icon}</ListItemIcon>
                    <ListItemText primary={item.text} />
                  </ListItem>
                ))}
              </List>
            </Box>
          </Drawer>

          <Box component="main" sx={{ flexGrow: 1, p: 3 }}>
            <Toolbar />
            <Routes>
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              <Route path="/dashboard" element={<Dashboard systemHealth={systemHealth} />} />
              <Route path="/notes" element={<NotesManager />} />
              <Route path="/search" element={<SearchInterface />} />
              <Route path="/api" element={<APITesting />} />
              <Route path="/analytics" element={<Analytics />} />
              <Route path="/settings" element={<Settings />} />
            </Routes>
          </Box>
        </Box>

        <Snackbar
          open={notification.open}
          autoHideDuration={6000}
          onClose={() => setNotification({ ...notification, open: false })}
        >
          <Alert severity={notification.severity} onClose={() => setNotification({ ...notification, open: false })}>
            {notification.message}
          </Alert>
        </Snackbar>
      </Router>
    </ThemeProvider>
  );
}

export default App;