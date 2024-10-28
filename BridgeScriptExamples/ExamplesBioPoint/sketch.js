let biopointData;

function preload() {
  biopointData = loadJSON('biopoint_data.json');
}

function setup() {
  createCanvas(800, 600);
  background(220);
  displayData(biopointData);
}

function displayData(data) {
  // Example: Display ECG data points if available
  if (data.ECG.length > 0) {
    for (let i = 0; i < data.ECG.length; i++) {
      ellipse(i * 10, height / 2 - data.ECG[i] * 10, 5, 5); // Adjust positioning & scaling
    }
  }
}