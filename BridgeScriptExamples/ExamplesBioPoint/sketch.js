let socket;
let ecgData = [];
let emgData = [];
let edaData = [];

function setup() {
  createCanvas(800, 600);
  background(220);

  // Connect to WebSocket server
  socket = new WebSocket('ws://localhost:8765');
  socket.onmessage = function(event) {
    let data = JSON.parse(event.data);
    ecgData.push(data.ECG);
    emgData.push(data.EMG);
    edaData.push(data.EDA);

    // Limit stored data to avoid memory overload
    if (ecgData.length > width) ecgData.shift();
    if (emgData.length > width) emgData.shift();
    if (edaData.length > width) edaData.shift();
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