let screenWidth = 800, screenHeight = 600;
let playerWidth = 50, playerHeight = 30;
let playerX, playerY, playerSpeed = 5;

let bulletWidth = 5, bulletHeight = 10, bulletSpeed = 7;
let bullets = [];

let obstacles = [];
let hearts = [];
let tripleShots = [];
let lives = 3;
let invincible = false;
let invincibleStartTime = 0;
let invincibleDuration = 5000; // 5 seconds in milliseconds
let tripleShot = false;
let tripleShotStartTime = 0;
let tripleShotDuration = 10000; // 10 seconds in milliseconds
let gameOver = false;
let score = 0;

// Gyroscope threshold values
let pitchThreshold = 0.1; // Adjusted for sensitivity
let yawThreshold = 0.1;  // Adjusted for sensitivity

// This will store the gyroscope data from WebSocket or OSC
let gyroData = { pitch: 0, yaw: 0, yaw: 0 };

// Setup the WebSocket to receive gyroscope data
let socket = new WebSocket('ws://localhost:8081'); // replace with actual server address

socket.onmessage = function(event) {
  // Assuming the event data is a JSON string
  try {
    gyroData = JSON.parse(event.data);
    console.log("Received Gyroscope Data:", gyroData);
  } catch (error) {
    console.error("Error parsing gyroscope data:", error);
  }
};

function setup() {
  createCanvas(screenWidth, screenHeight);
  playerX = (screenWidth - playerWidth) / 2;
  playerY = screenHeight - playerHeight - 10;
  textSize(20);
}

function draw() {
  background(0);

  if (!gameOver) {
    // Handle player movement using the gyroscope data
    handleGyroscopeData(gyroData); // Assuming 'gyroData' is already populated from WebSocket

    // Check if triple-shot duration has expired
    if (tripleShot && (millis() - tripleShotStartTime) > tripleShotDuration) {
      tripleShot = false;
    }

    // Spawn obstacles, hearts, and triple-shot power-ups
    if (random(1) < 0.02) {
      let obstacleWidth = int(random(20, 70));
      let obstacleHeight = obstacleWidth / 2;
      let obstacleX = int(random(0, screenWidth - obstacleWidth));
      let speed = max(1, 8 - int(obstacleWidth / 10));
      obstacles.push({ x: obstacleX, y: 0, width: obstacleWidth, height: obstacleHeight, speed: speed });
    }
    if (random(1) < 0.005) {
      let heartX = int(random(0, screenWidth - 20));
      hearts.push({ x: heartX, y: 0, speed: 2 });
    }
    if (random(1) < 0.0033) {
      let tripleShotX = int(random(0, screenWidth - 20));
      tripleShots.push({ x: tripleShotX, y: 0, speed: 2 });
    }

    // Update obstacles, hearts, and triple-shots
    for (let obs of obstacles) {
      obs.y += obs.speed;

      // Check for collision between player and obstacles
      if (!invincible && playerX < obs.x + obs.width && playerX + playerWidth > obs.x &&
          playerY < obs.y + obs.height && playerY + playerHeight > obs.y) {
        lives--;
        invincible = true;
        invincibleStartTime = millis();
        obstacles = obstacles.filter((o) => o !== obs); // Remove the collided obstacle

        // Check if game over
        if (lives <= 0) {
          gameOver = true;
        }
      }
    }

    for (let heart of hearts) {
      heart.y += heart.speed;

      // Player collects heart power-up by touching it
      if (playerX < heart.x + 20 && playerX + playerWidth > heart.x &&
          playerY < heart.y + 20 && playerY + playerHeight > heart.y) {
        if (lives < 3) lives++;
        hearts = hearts.filter((h) => h !== heart); // Remove the collected heart
      }
    }

    for (let ts of tripleShots) {
      ts.y += ts.speed;

      // Player collects triple-shot power-up by touching it
      if (playerX < ts.x + 20 && playerX + playerWidth > ts.x &&
          playerY < ts.y + 20 && playerY + playerHeight > ts.y) {
        tripleShot = true;
        tripleShotStartTime = millis();
        tripleShots = tripleShots.filter((t) => t !== ts); // Remove the collected triple-shot
      }
    }

    // Invincibility timer
    if (invincible && (millis() - invincibleStartTime) > invincibleDuration) {
      invincible = false;
    }

    // Bullet movement and collision with obstacles and power-ups
    for (let i = bullets.length - 1; i >= 0; i--) {
      let bullet = bullets[i];
      bullet.x += bulletSpeed * sin(bullet.angle);
      bullet.y -= bulletSpeed * cos(bullet.angle);

      // Remove off-screen bullets
      if (bullet.y < 0) bullets.splice(i, 1);

      // Collision with obstacles
      for (let j = obstacles.length - 1; j >= 0; j--) {
        let obs = obstacles[j];
        if (bullet.x > obs.x && bullet.x < obs.x + obs.width &&
            bullet.y > obs.y && bullet.y < obs.y + obs.height) {
          obstacles.splice(j, 1);
          bullets.splice(i, 1);
          score++;
          break;
        }
      }

      // Collision with hearts
      for (let k = hearts.length - 1; k >= 0; k--) {
        let heart = hearts[k];
        if (bullet.x > heart.x && bullet.x < heart.x + 20 &&
            bullet.y > heart.y && bullet.y < heart.y + 20) {
          hearts.splice(k, 1);
          bullets.splice(i, 1);
          break;
        }
      }

      // Collision with triple-shots
      for (let l = tripleShots.length - 1; l >= 0; l--) {
        let ts = tripleShots[l];
        if (bullet.x > ts.x && bullet.x < ts.x + 20 &&
            bullet.y > ts.y && bullet.y < ts.y + 20) {
          tripleShots.splice(l, 1);
          bullets.splice(i, 1);
          break;
        }
      }
    }

    // Draw player with invincibility blink effect
    if (!invincible || (millis() - invincibleStartTime) % 400 < 200) {
      fill(255);
      rect(playerX, playerY, playerWidth, playerHeight);
    }

    // Draw obstacles
    fill(255, 0, 0);
    for (let obs of obstacles) {
      rect(obs.x, obs.y, obs.width, obs.height);
    }

    // Draw hearts
    fill(255, 100, 100);
    for (let heart of hearts) {
      ellipse(heart.x + 10, heart.y + 10, 14, 14);
      ellipse(heart.x + 20, heart.y + 10, 14, 14);
      triangle(heart.x + 5, heart.y + 10, heart.x + 25, heart.y + 10, heart.x + 15, heart.y + 25);
    }

    // Draw triple-shot power-ups
    fill(100, 255, 100);
    for (let ts of tripleShots) {
      rect(ts.x, ts.y, 20, 20);
    }

    // Draw bullets
    fill(200, 200, 255);
    for (let bullet of bullets) {
      rect(bullet.x, bullet.y, bulletWidth, bulletHeight);
    }

    // Display lives and score
    fill(255);
    text(`Lives: ${lives}`, 10, 20);
    text(`Score: ${score}`, screenWidth - 100, 20);

  } else {
    // Game Over Screen
    textSize(50);
    fill(255, 0, 0);
    text("Game Over, WOMP WOMP!", screenWidth / 2 - 150, screenHeight / 2);
  }
}

// Function to handle gyroscope data and apply movement based on threshold system
function handleGyroscopeData(data) {
  let pitch = data.pitch || 0; // Pitch (up/down movement)
  let yaw = data.yaw || 0;   // yaw (left/right movement)

  // Debugging
  console.log("Pitch:", pitch, "yaw:", yaw);

  // Apply the threshold system for vertical (pitch) movement
  if (pitch > pitchThreshold) {
    playerY -= playerSpeed;
  } else if (pitch < -pitchThreshold) {
    playerY += playerSpeed;
  }

  // Apply the threshold system for horizontal (yaw) movement
  if (yaw > yawThreshold) {
    playerX -= playerSpeed;
  } else if (yaw < -yawThreshold) {
    playerX += playerSpeed;
  }
}
