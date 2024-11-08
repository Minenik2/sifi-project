const socket = new WebSocket('ws://193.157.192.121:31000'); // Your IP address and WebSocket port
const cursor = document.createElement('div');
cursor.style.position = 'absolute';
cursor.style.width = '30px';
cursor.style.height = '30px';
cursor.style.backgroundColor = 'red';
cursor.style.borderRadius = '50%';
document.body.appendChild(cursor);

// Variables to store cursor position
let xPos = window.innerWidth / 2;
let yPos = window.innerHeight / 2;

// Slower sensitivity factors for movement
const verticalSensitivity = 15;  // Reduced vertical sensitivity (slower)
const horizontalSensitivity = 30; // Reduced horizontal sensitivity (slower)

// Thresholds for movement
const PITCH_THRESHOLD = 0.05;  // Pitch threshold for up/down
const YAW_THRESHOLD = 0.1;  // Yaw threshold for left/right

// Initialize initial pitch and yaw
let initialPitch = null;
let initialYaw = null;

// WebSocket client: open connection
socket.addEventListener('open', () => {
  console.log('WebSocket connection established');
});

// WebSocket client: message handler
socket.addEventListener('message', (event) => {
  console.log('Received WebSocket message:', event.data); // Log received data

  const data = JSON.parse(event.data); // Parse the JSON message
  if (data.pitch !== undefined && data.roll !== undefined && data.yaw !== undefined) {
    // Log the values received from the WebSocket
    console.log('Pitch:', data.pitch, 'Roll:', data.roll, 'Yaw:', data.yaw);

    // Update the position of the cursor with adjusted sensitivity and direction swapped
    moveCursor(data.pitch, data.roll, data.yaw);
  }
});

// Move the cursor based on the threshold logic
function moveCursor(pitch, roll, yaw) {
  // Initialize pitch and yaw if not yet done
  if (initialPitch === null || initialYaw === null) {
    initialPitch = pitch;
    initialYaw = yaw;
    console.log("Initial pitch and yaw set.");
    return;
  }

  // Calculate the relative pitch and yaw
  const relativePitch = pitch - initialPitch;
  const relativeYaw = yaw - initialYaw;

  // Print out the relative values (for debugging)
  console.log(`Relative Pitch: ${relativePitch}, Relative Yaw: ${relativeYaw}`);

  // Logic for vertical movement (up/down) based on pitch
  if (relativePitch > PITCH_THRESHOLD) {
    yPos -= verticalSensitivity;  // Move cursor up
  } else if (relativePitch < -PITCH_THRESHOLD) {
    yPos += verticalSensitivity;  // Move cursor down
  }

  // Logic for horizontal movement (left/right) based on yaw
  if (relativeYaw > YAW_THRESHOLD) {
    xPos -= horizontalSensitivity;  // Move cursor left (inverted)
  } else if (relativeYaw < -YAW_THRESHOLD) {
    xPos += horizontalSensitivity;  // Move cursor right (inverted)
  }

  // Boundary checks to keep the cursor within the window bounds
  xPos = Math.max(0, Math.min(window.innerWidth, xPos));
  yPos = Math.max(0, Math.min(window.innerHeight, yPos));

  // Update the position of the cursor element
  cursor.style.left = `${xPos}px`;
  cursor.style.top = `${yPos}px`;
}
