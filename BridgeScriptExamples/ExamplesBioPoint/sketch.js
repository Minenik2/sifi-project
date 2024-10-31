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
    socket.send("javascript")
  };

  // Log each incoming message
  socket.onmessage = (event) => {
    let data = JSON.parse(event.data)
    console.log("Received from server:", data);
    if (data[0] == "EMG") {
      addEmgValue(data[1])
    }
  };

  // Handle disconnections and try to reconnect
  socket.onclose = () => {
    console.log(socket.bufferedAmount)
    console.log("Disconnected from server, attempting to reconnect...");
    setTimeout(connectWebSocket, 20); // Try to reconnect after 1 second
  };
}

function draw() {
  background(0);
  noFill();
  stroke(255);

  // Draw each EMG value as a circle or bar on the screen
  let barWidth = width / maxValues;
  for (let i = 0; i < emgValues.length; i++) {
    let x = i * barWidth;
    let y = map(emgValues[i], 0, 1023, height, 0); // Mapping EMG to height

    // Draw a circle that scales with EMG data
    let size = map(emgValues[i]*2, 0, 70, 10, 100); 
    fill(255, 100, 150, 150); 
    ellipse(x, height / 2, size, size); 
  }
}

function addEmgValue(newValue) {
  // Add new value to array and remove oldest if over limit
  emgValues.push(newValue);
  if (emgValues.length > maxValues) {
    emgValues.shift();
  }
}

