const express = require('express');
const path = require('path');
const cors = require('cors');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.static('.'));
app.use('/assets', express.static(path.join(__dirname, 'assets')));
app.use('/pages', express.static(path.join(__dirname, 'pages')));
app.use('/chatbot', express.static(path.join(__dirname, 'chatbot')));

// API proxy for development
app.use('/api', (req, res) => {
  res.json({ 
    message: 'Frontend server running. Backend API should be on port 5000',
    backend_url: 'http://localhost:5000/api'
  });
});

// Routes for all pages
const routes = {
  '/': 'index.html',
  '/login': 'login.html',
  '/register': 'register.html',
  '/forgot-password': 'forgot-password.html',
  '/reset-password': 'reset-password.html',
  '/verify-otp': 'verify-otp.html',
  '/dashboard': 'dashboard.html',
  '/file-complaint': 'file-complaint.html',
  '/my-complaints': 'my-complaints.html',
  '/track': 'track.html',
  '/view': 'view.html',
  '/police': 'police.html',
  '/admin-dashboard': 'admin-dashboard.html',
  '/awareness': 'awareness.html',
  '/learning': 'learning.html',
  '/user': 'user.html'
};

// Set up routes
Object.entries(routes).forEach(([route, file]) => {
  app.get(route, (req, res) => {
    res.sendFile(path.join(__dirname, 'pages', file));
  });
});

// Catch all handler
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'pages', 'index.html'));
});

// Start server
app.listen(PORT, () => {
  console.log(`🚀 iReport Frontend Server running on http://localhost:${PORT}`);
  console.log(`📊 Backend API should be running on http://localhost:5000`);
  console.log(`🔗 Make sure both servers are running for full functionality`);
});