let socket;
let pitch = 0;
let yaw = 0;
let roll = 0;

let emgValues = [];  // Store recent EMG values
let maxValues = 100; // Maximum number of values to display

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
    socket.send("javascript");
  };

  // Handle incoming messages
  socket.onmessage = (event) => {
    const data = JSON.parse(event.data); // Expecting JSON object with all values at once
    console.log("Received from server:", data);

    if (data.EMG !== undefined) addEmgValue(data.EMG);
    if (data.PITCH !== undefined) pitch = data.PITCH;
    if (data.ROLL !== undefined) roll = data.ROLL;
    if (data.YAW !== undefined) yaw = data.YAW;

    drawCircle();  // Draw only on new data received
  };

  // Handle disconnections and try to reconnect
  socket.onclose = () => {
    console.log("Disconnected from server, attempting to reconnect...");
    setTimeout(connectWebSocket, 1000); // Try to reconnect after 1 second
  };
}

function draw() {
  // Kept empty to avoid redundant rendering. Drawing is triggered by `drawCircle` on data receipt.
}

function drawCircle() {
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
  if (emgValues.length > maxValues) emgValues.shift();
}