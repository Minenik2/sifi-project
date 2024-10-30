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
  const sampleRate = 1; // Adjust to control density
  const spacing = 10;     // Distance between points
  let x = 0;
  let y = 0;

  for (let i = 0; i < data.ECG.length; i += sampleRate) {
    // Calculate the next position
    x = (i / sampleRate) % (width / spacing) * spacing;
    y = Math.floor((i / sampleRate) / (width / spacing)) * spacing;

    // Use fill color or size to enhance visualization if needed
    const intensity = map(data.ECG[i], 0, max(data.ECG), 0, 255);
    fill(255, 0, 0, intensity); // Color based on intensity
    ellipse(x, y, 5, 5);
  }
}