let socket;
let ecgData = [];
let emgData = [];
let edaData = [];

let emgValues = [];  // Store recent EMG values
let maxValues = 100; // Maximum number of values to display

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
    addEmgValue(event.data)
  };

  // Handle disconnections and try to reconnect
  socket.onclose = () => {
    console.log("Disconnected from server, attempting to reconnect...");
    setTimeout(connectWebSocket, 20); // Try to reconnect after 1 second
  };
}

function draw() {
  background(0);

  // Draw the waveform line
  stroke(255, 100, 150);  // Pink color for the line
  strokeWeight(2);
  noFill();
  beginShape();  // Start a continuous line shape

  for (let i = 0; i < emgValues.length; i++) {
    let x = map(i, 0, maxValues, 0, width);  // Spread points across the width
    let y = map(emgValues[i], 0, 1023, height, 0);  // Map EMG values to height

    vertex(x, y);  // Create a point in the waveform
  }

  endShape();  // Finish the continuous line shape

  // Optional: Draw circles along the waveform
  for (let i = 0; i < emgValues.length; i++) {
    let x = map(i, 0, maxValues, 0, width);
    let y = map(emgValues[i], 0, 1023, height, 0);

    fill(255, 100, 150, 150);
    noStroke();
    ellipse(x, y, 5, 5);  // Small circle at each data point for effect
  }
}

function addEmgValue(newValue) {
  // Add new value to array and remove oldest if over limit
  emgValues.push(newValue);
  if (emgValues.length > maxValues) {
    emgValues.shift();
  }
}

