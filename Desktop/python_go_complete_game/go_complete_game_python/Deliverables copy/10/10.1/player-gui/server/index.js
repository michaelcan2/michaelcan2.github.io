const express = require("express");
const bodyParser = require("body-parser");
const pino = require("express-pino-logger")();
const socketIo = require("socket.io");
var net = require("net");

const app = express();
app.use(bodyParser.urlencoded({ extended: false }));
app.use(pino);

app.get("/api/make_a_move", (req, res) => {
  const id = req.query.id;
  const move = req.query.move;
  const client = tcp_players[id];
  client.write(JSON.stringify(move));
  res.setHeader("Content-Type", "application/json");
  res.send(JSON.stringify({ msg: `move has been made!` }));
});

app.get("/api/register", (req, res) => {
  const id = req.query.id;
  const name = req.query.name;
  const client = tcp_players[id];
  client.write(JSON.stringify(name));
  res.setHeader("Content-Type", "application/json");
  res.send(JSON.stringify({ msg: `name has been registered!` }));
  console.log("register as " + name);
});

server = app.listen(3001, () =>
  console.log("Express server is running on localhost:3001")
);

io = socketIo(server);

tcp_players = {};
tcp_stones = {};

create_new_client = id => {
  var client = new net.createConnection(8080, "localhost");

  client.on("data", function(data) {
    const command = JSON.parse(data);
    console.log("Received: " + data, command[0]);

    if (command[0] == "register") {
      io.to(id).emit("register", "give a name!");
    } else if (command[0] == "receive-stones") {
      io.to(id).emit("receive-stones", { piece: command[1] });
      tcp_stones[id] = command[1];
    } else if (command[0] == "make-a-move") {
      const recent_move = get_previous_player_move(command[1], tcp_stones[id]);
      console.log(recent_move);
      io.to(id).emit("make-a-move", { state: command[1], recent_move });
    } else if (command[0] == "end-game") {
      io.to(id).emit("end-game", "game ends!");
      client.write(JSON.stringify("OK"));
    }
  });

  client.on("close", function() {
    console.log("Connection closed");
  });

  client.on("error", function(ex) {
    console.log("handled error");
    console.log(ex);
    io.to(id).emit("refused", "ECONNREFUSED");
  });

  return client;
};

server_send = (client, msg) => {
  client.write(msg);
};

io.on("connection", socket => {
  console.log("New client connected");
  socket.emit("id", { id: socket.id });

  // create a tcp client for that player to play the game

  tcp_players[socket.id] = create_new_client(socket.id);

  socket.on("disconnect", () => console.log("Client disconnected"));
});

const board_height = 9;
const board_width = 9;

function get_opponent(s) {
  if (s === "B") {
    return "W";
  } else {
    return "B";
  }
}

function get_points(board, s) {
  let results = [];
  for (let i = 0; i < board_height; i++) {
    for (let j = 0; j < board_width; j++) {
      if (board[i][j] === s) {
        results.push(`${j + 1}-${i + 1}`);
      }
    }
  }

  return results;
}

function get_previous_player_move(hist, s) {
  if (hist.length > 1) {
    const prev_board = hist[1];
    const next_board = hist[0];
    console.log(prev_board, next_board);
    // get stone counts of {B: int, W: int}
    const other_player = get_opponent(s);
    const prev_stone_places = get_points(prev_board, other_player);
    const next_stone_places = get_points(next_board, other_player);
    console.log(prev_stone_places, next_stone_places);
    // check if its a pass
    for (let pp of next_stone_places) {
      if (!prev_stone_places.includes(pp)) {
        return pp;
      }
    }

    return "pass";
  } else {
    return false;
  }
}
