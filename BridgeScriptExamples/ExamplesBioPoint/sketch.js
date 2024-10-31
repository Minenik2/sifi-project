let socket;
let pitch = 0;
let yaw = 0;
let roll = 0;

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
  socket = new WebSocket("ws://localhost:8735");

  // When connected to the server
  socket.onopen = () => {
    console.log("Connected to the server");
    socket.send("javascript")
  };

  // Log each incoming message
  socket.onmessage = (event) => {
    let data = JSON.parse(event.data)
    console.log("Received from server:", data);
    if (data[0] == "EMG") {
      addEmgValue(data[1])
    }
    if (data[0] == "PITCH") {
      pitch = data[1];
    }
    if (data[0] == "ROLL") {
      roll = data[1];
    }
    if (data[0] == "YAW") {
      yaw = data[1];
    }
  };

  // Handle disconnections and try to reconnect
  socket.onclose = () => {
    console.log("Disconnected from server, attempting to reconnect...");
    setTimeout(connectWebSocket, 20); // Try to reconnect after 1 second
  };
}

function draw() {
  background(0);

  // Map pitch, yaw, and roll to screen coordinates or properties
  let x = map(yaw, -90, 90, 0, width);      // Adjust yaw to control x position
  let y = map(pitch, -90, 90, height, 0);   // Adjust pitch to control y position
  let size = map(abs(roll), 0, 180, 10, 100); // Adjust roll to control circle size

  // Draw the circle based on pitch, yaw, and roll values
  fill(100, 150, 255, 150);
  noStroke();
  ellipse(x, y, size + 1000);
  
}

function addEmgValue(newValue) {
  // Add new value to array and remove oldest if over limit
  emgValues.push(newValue);
  if (emgValues.length > maxValues) {
    emgValues.shift();
  }
}

