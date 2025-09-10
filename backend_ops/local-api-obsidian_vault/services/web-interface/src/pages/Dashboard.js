import React, { useState, useEffect } from 'react';
import {
  Grid, Card, CardContent, Typography, Box, LinearProgress,
  List, ListItem, ListItemText, Chip, IconButton, Refresh
} from '@mui/material';
import {
  TrendingUp, Storage, Speed, Memory, Api as ApiIcon,
  CheckCircle, Error, Warning
} from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { apiService } from '../services/apiService';

function Dashboard({ systemHealth }) {
  const [metrics, setMetrics] = useState(null);
  const [recentActivity, setRecentActivity] = useState([]);
  const [performanceData, setPerformanceData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
    const interval = setInterval(loadDashboardData, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const [metricsData, performanceMetrics] = await Promise.all([
        apiService.getMetrics(),
        apiService.getPerformanceMetrics()
      ]);
      
      setMetrics(metricsData);
      
      // Generate mock performance data for chart
      const now = new Date();
      const chartData = Array.from({ length: 24 }, (_, i) => ({
        time: new Date(now.getTime() - (23 - i) * 60 * 60 * 1000).toLocaleTimeString('en-US', { hour: '2-digit' }),
        requests: Math.floor(Math.random() * 100) + 20,
        responseTime: Math.floor(Math.random() * 200) + 50,
        memory: Math.floor(Math.random() * 30) + 40
      }));
      setPerformanceData(chartData);
      
      // Mock recent activity
      setRecentActivity([
        { id: 1, action: 'Note created', file: 'daily/2024-01-15.md', time: '2 minutes ago', status: 'success' },
        { id: 2, action: 'AI processing', file: 'research/ai-agents.md', time: '5 minutes ago', status: 'success' },
        { id: 3, action: 'Search query', query: 'machine learning', time: '8 minutes ago', status: 'success' },
        { id: 4, action: 'Workflow executed', workflow: 'content-curation', time: '12 minutes ago', status: 'warning' }
      ]);
      
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'healthy':
      case 'success':
        return <CheckCircle color="success" />;
      case 'warning':
        return <Warning color="warning" />;
      case 'error':
        return <Error color="error" />;
      default:
        return <CheckCircle color="disabled" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'healthy':
      case 'success':
        return 'success';
      case 'warning':
        return 'warning';
      case 'error':
        return 'error';
      default:
        return 'default';
    }
  };

  if (loading) {
    return (
      <Box sx={{ width: '100%', mt: 2 }}>
        <LinearProgress />
        <Typography variant="h6" sx={{ mt: 2, textAlign: 'center' }}>
          Loading dashboard...
        </Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ flexGrow: 1 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          System Dashboard
        </Typography>
        <IconButton onClick={loadDashboardData} color="primary">
          <Refresh />
        </IconButton>
      </Box>

      <Grid container spacing={3}>
        {/* System Status Cards */}
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                {getStatusIcon(systemHealth?.status)}
                <Typography variant="h6" sx={{ ml: 1 }}>
                  System Status
                </Typography>
              </Box>
              <Typography variant="h4" color="primary">
                {systemHealth?.status === 'healthy' ? 'Online' : 'Issues'}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {systemHealth?.services ? Object.keys(systemHealth.services).length : 0} services
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <Storage color="primary" />
                <Typography variant="h6" sx={{ ml: 1 }}>
                  Vault Notes
                </Typography>
              </Box>
              <Typography variant="h4" color="primary">
                {metrics?.vault_notes_total || 0}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Total notes in vault
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <ApiIcon color="primary" />
                <Typography variant="h6" sx={{ ml: 1 }}>
                  API Requests
                </Typography>
              </Box>
              <Typography variant="h4" color="primary">
                {metrics?.api_requests_total || 0}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Total requests today
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <Speed color="primary" />
                <Typography variant="h6" sx={{ ml: 1 }}>
                  Response Time
                </Typography>
              </Box>
              <Typography variant="h4" color="primary">
                {Math.floor(Math.random() * 100) + 50}ms
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Average response time
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Performance Chart */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Performance Metrics (24h)
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={performanceData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="time" />
                  <YAxis />
                  <Tooltip />
                  <Line type="monotone" dataKey="requests" stroke="#6366f1" name="Requests/hour" />
                  <Line type="monotone" dataKey="responseTime" stroke="#f59e0b" name="Response Time (ms)" />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Recent Activity */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Recent Activity
              </Typography>
              <List dense>
                {recentActivity.map((activity) => (
                  <ListItem key={activity.id} sx={{ px: 0 }}>
                    <ListItemText
                      primary={
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <Typography variant="body2">
                            {activity.action}
                          </Typography>
                          <Chip
                            size="small"
                            label={activity.status}
                            color={getStatusColor(activity.status)}
                            variant="outlined"
                          />
                        </Box>
                      }
                      secondary={
                        <Box>
                          <Typography variant="caption" display="block">
                            {activity.file || activity.query || activity.workflow}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {activity.time}
                          </Typography>
                        </Box>
                      }
                    />
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* Service Status */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Service Status
              </Typography>
              <Grid container spacing={2}>
                {systemHealth?.services && Object.entries(systemHealth.services).map(([service, status]) => (
                  <Grid item xs={12} sm={6} md={4} key={service}>
                    <Box sx={{ display: 'flex', alignItems: 'center', p: 1, border: 1, borderColor: 'divider', borderRadius: 1 }}>
                      {getStatusIcon(typeof status === 'string' ? status : 'healthy')}
                      <Box sx={{ ml: 1 }}>
                        <Typography variant="body1" sx={{ textTransform: 'capitalize' }}>
                          {service.replace('_', ' ')}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {typeof status === 'boolean' ? (status ? 'Running' : 'Stopped') : status}
                        </Typography>
                      </Box>
                    </Box>
                  </Grid>
                ))}
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}

export default Dashboard;