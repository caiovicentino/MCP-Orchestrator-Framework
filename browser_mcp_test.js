// Simple script to test Browser MCP
const { exec } = require('child_process');
const http = require('http');

// Start the Browser MCP server
console.log('Starting Browser MCP server...');
const serverProcess = exec('npx @browsermcp/mcp@latest', (error, stdout, stderr) => {
  if (error) {
    console.error(`Error starting server: ${error.message}`);
    return;
  }
  if (stderr) {
    console.error(`Server stderr: ${stderr}`);
    return;
  }
  console.log(`Server stdout: ${stdout}`);
});

// Wait for the server to start
setTimeout(() => {
  console.log('Sending command to Browser MCP...');

  // Prepare the command data
  const data = JSON.stringify({
    command: 'Go to google.com'
  });

  // Options for the HTTP request
  const options = {
    hostname: 'localhost',
    port: 9009,  // Default port for Browser MCP
    path: '/execute',
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Content-Length': data.length
    }
  };

  // Send the command to the server
  const req = http.request(options, (res) => {
    console.log(`Status Code: ${res.statusCode}`);

    res.on('data', (chunk) => {
      console.log(`Response: ${chunk}`);
    });

    res.on('end', () => {
      console.log('Command sent successfully');

      // Wait a bit before stopping the server
      setTimeout(() => {
        console.log('Stopping server...');
        serverProcess.kill();
        console.log('Server stopped');
      }, 10000);
    });
  });

  req.on('error', (error) => {
    console.error(`Error sending command: ${error.message}`);

    // Try with a different port
    console.log('Trying with port 3000...');
    options.port = 3000;

    const req2 = http.request(options, (res) => {
      console.log(`Status Code: ${res.statusCode}`);

      res.on('data', (chunk) => {
        console.log(`Response: ${chunk}`);
      });

      res.on('end', () => {
        console.log('Command sent successfully');

        // Wait a bit before stopping the server
        setTimeout(() => {
          console.log('Stopping server...');
          serverProcess.kill();
          console.log('Server stopped');
        }, 10000);
      });
    });

    req2.on('error', (error) => {
      console.error(`Error sending command to port 3000: ${error.message}`);
      console.log('Stopping server...');
      serverProcess.kill();
      console.log('Server stopped');
    });

    req2.write(data);
    req2.end();
  });

  req.write(data);
  req.end();
}, 5000);
