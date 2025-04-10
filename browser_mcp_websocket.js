// Test Browser MCP using WebSocket
const { exec } = require('child_process');
const WebSocket = require('ws');

// First, install the ws package if not already installed
console.log('Installing WebSocket package...');
exec('npm install ws', (error, stdout, stderr) => {
  if (error) {
    console.error(`Error installing ws: ${error.message}`);
    return;
  }
  
  // Start the Browser MCP server
  console.log('Starting Browser MCP server...');
  const serverProcess = exec('npx @browsermcp/mcp@latest', (error, stdout, stderr) => {
    if (error) {
      console.error(`Error starting server: ${error.message}`);
      return;
    }
    if (stderr) {
      console.error(`Server stderr: ${stderr}`);
    }
    if (stdout) {
      console.log(`Server stdout: ${stdout}`);
    }
  });
  
  // Wait for the server to start
  setTimeout(() => {
    console.log('Connecting to Browser MCP WebSocket server...');
    
    // Try to connect to the WebSocket server
    const ws = new WebSocket('ws://localhost:9009');
    
    ws.on('open', () => {
      console.log('Connected to Browser MCP WebSocket server');
      
      // Send a command to the server
      const command = {
        type: 'execute',
        command: 'Go to google.com'
      };
      
      console.log('Sending command:', command);
      ws.send(JSON.stringify(command));
    });
    
    ws.on('message', (data) => {
      console.log('Received message:', data.toString());
    });
    
    ws.on('error', (error) => {
      console.error('WebSocket error:', error.message);
      
      // Try with a different port
      console.log('Trying with port 3000...');
      const ws2 = new WebSocket('ws://localhost:3000');
      
      ws2.on('open', () => {
        console.log('Connected to Browser MCP WebSocket server on port 3000');
        
        // Send a command to the server
        const command = {
          type: 'execute',
          command: 'Go to google.com'
        };
        
        console.log('Sending command:', command);
        ws2.send(JSON.stringify(command));
      });
      
      ws2.on('message', (data) => {
        console.log('Received message from port 3000:', data.toString());
      });
      
      ws2.on('error', (error) => {
        console.error('WebSocket error on port 3000:', error.message);
        console.log('Stopping server...');
        serverProcess.kill();
        console.log('Server stopped');
      });
    });
    
    // Wait a bit before stopping the server
    setTimeout(() => {
      console.log('Stopping server...');
      if (ws.readyState === WebSocket.OPEN) {
        ws.close();
      }
      serverProcess.kill();
      console.log('Server stopped');
    }, 30000);
  }, 5000);
});
