let socket;
let ecgData = [];
let emgData = [];
let edaData = [];

console.log("hello")

function setup() {
  createCanvas(800, 600);
  background(220);

  // Initialize the WebSocket connection
  connectWebSocket();
}

function connectWebSocket() {
  // Create a new WebSocket connection
  socket = new WebSocket("ws://localhost:8765");

  // When connected to the server
  socket.onopen = () => {
    console.log("Connected to the server");
    socket.send("javascript");
  };

  // Log each incoming message
  socket.onmessage = (event) => {
    console.log("Received from server:", event.data);
    emgData.push(event.data)
  };

  // Handle disconnections and try to reconnect
  socket.onclose = () => {
    console.log("Disconnected from server, attempting to reconnect...");
    setTimeout(connectWebSocket, 20); // Try to reconnect after 1 second
  };
}

function draw() {
  background(220);

  // Plot ECG Data
  stroke(255, 0, 0);
  noFill();
  beginShape();
  for (let i = 0; i < ecgData.length; i++) {
    vertex(i, height / 3 - ecgData[i] * 100);
  }
  endShape();

  // Plot EMG Data
  stroke(0, 255, 0);
  noFill();
  beginShape();
  for (let i = 0; i < emgData.length; i++) {
    vertex(i, height / 2 - emgData[i] * 100);
  }
  endShape();

  // Plot EDA Data
  stroke(0, 0, 255);
  noFill();
  beginShape();
  for (let i = 0; i < edaData.length; i++) {
    vertex(i, (2 * height) / 3 - edaData[i] * 100);
  }
  endShape();
}