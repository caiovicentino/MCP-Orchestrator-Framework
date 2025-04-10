// Simple script to send a command to Browser MCP
const WebSocket = require('ws');

// Command to execute
const command = process.argv[2] || 'Go to google.com';

console.log(`Attempting to send command: "${command}" to Browser MCP`);

// Connect to the WebSocket server
const ws = new WebSocket('ws://localhost:9009');

ws.on('open', () => {
  console.log('Connected to Browser MCP WebSocket server');
  
  // Send the command
  const message = {
    type: 'execute',
    command: command
  };
  
  console.log('Sending command:', message);
  ws.send(JSON.stringify(message));
  
  // Wait a bit before closing
  setTimeout(() => {
    console.log('Closing connection...');
    ws.close();
    console.log('Connection closed');
  }, 5000);
});

ws.on('message', (data) => {
  console.log('Received message:', data.toString());
});

ws.on('error', (error) => {
  console.error('WebSocket error:', error.message);
  console.log('Trying with port 3000...');
  
  const ws2 = new WebSocket('ws://localhost:3000');
  
  ws2.on('open', () => {
    console.log('Connected to Browser MCP WebSocket server on port 3000');
    
    // Send the command
    const message = {
      type: 'execute',
      command: command
    };
    
    console.log('Sending command:', message);
    ws2.send(JSON.stringify(message));
    
    // Wait a bit before closing
    setTimeout(() => {
      console.log('Closing connection...');
      ws2.close();
      console.log('Connection closed');
    }, 5000);
  });
  
  ws2.on('message', (data) => {
    console.log('Received message from port 3000:', data.toString());
  });
  
  ws2.on('error', (error) => {
    console.error('WebSocket error on port 3000:', error.message);
    process.exit(1);
  });
});
