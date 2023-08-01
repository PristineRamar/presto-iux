const express = require('express');
const app = express();
const PORT = 3000; 
const chatRoutes = require('./routes/chatRoutes');

// Add middleware and routes here
app.use('/chat', chatRoutes);

// Start the server
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
