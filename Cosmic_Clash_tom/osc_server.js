// Import the required libraries
const osc = require('osc');
const WebSocket = require('ws');

// Create a WebSocket server
const wss = new WebSocket.Server({ port: 8081 }); // WebSocket server listens on port 31000

// Set up WebSocket server events
wss.on('connection', (ws) => {
  console.log('WebSocket connection established.');

  // Handle incoming WebSocket messages
  ws.on('message', (message) => {
    console.log(`Received WebSocket message: ${message}`);
  });

  // Handle WebSocket connection close
  ws.on('close', () => {
    console.log('WebSocket connection closed.');
  });
});

// Create an OSC server
const oscServer = new osc.UDPPort({
  localAddress: '0.0.0.0', // Listen on all interfaces
  localPort: 31000,        // OSC server listens on port 31001
});

// Start the OSC server
oscServer.open(() => {
  console.log('OSC server started on port 31001');
});

// Listen for OSC messages
oscServer.on('message', (oscMessage) => {
  console.log('OSC message received:', oscMessage);

  // Check for the specific OSC address you're looking for (e.g., /gyrosc/gyro)
  if (oscMessage.address === '/gyrosc/gyro') {
    // Get the values (pitch, roll, yaw) from the OSC message args
    const [pitch, roll, yaw] = oscMessage.args;

    // Handle the OSC values (e.g., move the cursor based on the pitch, roll, yaw)
    if (wss.clients.size > 0) {
      // Send data to all connected WebSocket clients
      wss.clients.forEach((client) => {
        if (client.readyState === WebSocket.OPEN) {
          client.send(JSON.stringify({ pitch, roll, yaw }));
        }
      });
    }
  }
});
