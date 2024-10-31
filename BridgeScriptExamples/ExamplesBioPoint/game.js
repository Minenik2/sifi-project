let screen_width = 800, screen_height = 600;

let playerWidth = 50, playerHeight = 30;
let playerX, playerY, playerSpeed = 10;

let bulletWidth = 5, bulletHeight = 10, bulletSpeed = 7;
let bullets = [];

let obstacles = [];
let lives = 3;
let invincible = false;
let invincibleStartTime = 0;
let invincibleDuration = 5000; // 5 seconds in milliseconds
let gameOver = false;

function setup() {
  createCanvas(screen_width, screen_height);
  playerX = (screen_width - playerWidth) / 2;
  playerY = screen_height - playerHeight - 10;
}

function draw() {
  background(0);

  if (!gameOver) {
    // Player movement
    if (keyIsDown(LEFT_ARROW) && playerX > 0) {
      playerX -= playerSpeed;
    }
    if (keyIsDown(RIGHT_ARROW) && playerX < screen_width - playerWidth) {
      playerX += playerSpeed;
    }
    if (keyIsDown(UP_ARROW) && playerY > 0) {
      playerY -= playerSpeed;
    }
    if (keyIsDown(DOWN_ARROW) && playerY < screen_height - playerHeight) {
      playerY += playerSpeed;
    }

    // Obstacle spawning
    if (random(1) < 0.02) { // 2% chance per frame
      let obstacleWidth = int(random(20, 70));
      let obstacleHeight = obstacleWidth / 2;
      let obstacleX = int(random(0, screen_width - obstacleWidth));
      let speed = max(1, 12 - int(obstacleWidth / 10));
      obstacles.push({ x: obstacleX, y: 0, width: obstacleWidth, height: obstacleHeight, speed: speed });
    }

    // Update obstacles
    for (let i = obstacles.length - 1; i >= 0; i--) {
      obstacles[i].y += obstacles[i].speed;

      // Check collision with player if not invincible
      if (!invincible && 
          playerX < obstacles[i].x + obstacles[i].width && 
          playerX + playerWidth > obstacles[i].x && 
          playerY < obstacles[i].y + obstacles[i].height && 
          playerY + playerHeight > obstacles[i].y) {
        lives--;
        invincible = true;
        invincibleStartTime = millis();
        obstacles.splice(i, 1);

        if (lives <= 0) {
          gameOver = true;
        }
        continue;
      }

      // Remove obstacles that move off-screen
      if (obstacles[i].y > screen_height) {
        obstacles.splice(i, 1);
      }
    }

    // Invincibility timer
    if (invincible && millis() - invincibleStartTime > invincibleDuration) {
      invincible = false;
    }

    // Update bullets
    for (let i = bullets.length - 1; i >= 0; i--) {
      bullets[i].y -= bulletSpeed;

      // Check bullet collisions with obstacles
      for (let j = obstacles.length - 1; j >= 0; j--) {
        if (bullets[i].x < obstacles[j].x + obstacles[j].width &&
            bullets[i].x + bulletWidth > obstacles[j].x &&
            bullets[i].y < obstacles[j].y + obstacles[j].height &&
            bullets[i].y + bulletHeight > obstacles[j].y) {
          bullets.splice(i, 1);
          obstacles.splice(j, 1);
          break;
        }
      }

      // Remove bullets that move off-screen
      if (bullets[i] && bullets[i].y < 0) {
        bullets.splice(i, 1);
      }
    }

    // Draw player
    fill(255);
    rect(playerX, playerY, playerWidth, playerHeight);

    // Draw obstacles
    fill(255, 0, 0);
    for (let obs of obstacles) {
      rect(obs.x, obs.y, obs.width, obs.height);
    }

    // Draw bullets
    fill(200, 200, 255);
    for (let bullet of bullets) {
      rect(bullet.x, bullet.y, bulletWidth, bulletHeight);
    }

    // Draw lives
    fill(255);
    textSize(20);
    text("Lives: " + lives, 10, 20);
  } else {
    // Game Over Screen
    textSize(50);
    fill(255, 0, 0);
    text("Game Over", screen_width / 2 - 100, screen_height / 2);
  }
}

// Shoot bullet when space is pressed
function keyPressed() {
  if (key === ' ' && !gameOver) {
    let bulletX = playerX + playerWidth / 2 - bulletWidth / 2;
    let bulletY = playerY;
    bullets.push({ x: bulletX, y: bulletY });
  }
}
