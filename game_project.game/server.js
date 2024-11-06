// server.js
const express = require("express");
const http = require("http");
const { Server } = require("socket.io");

const app = express();
const server = http.createServer(app);
const io = new Server(server);

app.use(express.static("public"));

let players = {};

io.on("connection", (socket) => {
  console.log("A user connected:", socket.id);

  // Handle player role setup
  socket.on("setRole", (role) => {
    players[socket.id] = {
      id: socket.id,
      shape: role === "client1" ? "circle" : "square", // Circle for Client 1, Square for Client 2
      x: 50,
      y: 50,
    };
    io.emit("updatePlayers", players);
  });

  socket.on("move", (data) => {
    const player = players[socket.id];
    if (player) {
      if (data.direction === "left") player.x -= 10;
      if (data.direction === "right") player.x += 10;
      if (data.direction === "up") player.y -= 10;
      if (data.direction === "down") player.y += 10;
      io.emit("updatePlayers", players);
    }
  });

  socket.on("disconnect", () => {
    delete players[socket.id];
    io.emit("updatePlayers", players);
  });
});

server.listen(3000, '0.0.0.0', () => {
  console.log("Server listening on http://0.0.0.0:3000");
});

