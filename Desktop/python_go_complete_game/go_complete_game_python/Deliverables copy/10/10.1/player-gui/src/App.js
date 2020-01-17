import React, { Component } from "react";
import socketIOClient from "socket.io-client";
import logo from "./logo.svg";
import tenuki from "tenuki";
import GoControls from "./GoControls";
import classnames from "classnames";
import "./tenuki.css";
import "./App.css";

const colors = {
  black: "B",
  white: "W"
};

class App extends Component {
  constructor(props) {
    super(props);
    this.state = {
      name: "",
      input: "",
      msg: "",
      hist: null,
      stone: null,
      yourTurn: false,
      refused: false,
      game: null,
      ended: false
    };

    this.handleChange = this.handleChange.bind(this);
    this.register = this.register.bind(this);
    this.sendMove = this.sendMove.bind(this);
    this.resetGame = this.resetGame.bind(this);
  }

  componentDidMount() {
    const socket = socketIOClient("10.104.250.82:3000");
    const self = this;

    socket.on("id", data => {
      this.setState({ id: data.id });

      var passButton = document.querySelector(".pass");

      passButton.addEventListener("click", function(e) {
        e.preventDefault();

        fetch(`/api/make_a_move?id=${encodeURIComponent(data.id)}&move=pass`)
          .then(response => response.json())
          .then(state => self.setState(state));
      });
    });

    socket.on("receive-stones", data =>
      this.setState({ stone: data.piece, ended: false })
    );
    socket.on("register", data => this.setState({ msg: "Enter a name." }));

    socket.on("make-a-move", data => {
      this.setState({ yourTurn: true, hist: data.state });
      const recent_move = data.recent_move;
      console.log(recent_move);
      if (recent_move) {
        if (recent_move === "pass") {
          this.state.game.pass();
        } else {
          let x = parseInt(recent_move[0]) - 1;
          let y = parseInt(recent_move[2]) - 1;
          this.state.game.playAt(x, y);
        }
      }
    });

    socket.on("end-game", data => {
      this.setState({ hist: null, stone: null, yourTurn: false, ended: true });
      this.resetGame();
    });

    socket.on("refused", data => this.setState({ refused: true }));

    var boardElement = document.querySelector(".tenuki-board");
    var game = new tenuki.Game({
      element: boardElement,
      boardSize: 9,
      koRule: "positional-superko"
    });

    var controlElement = document.querySelector(".controls");
    var controls = new GoControls(controlElement, game);
    controls.setup();

    game.callbacks.postRender = function(game) {
      controls.updateStats();

      if (game.currentState().pass) {
        console.log(game.currentState().color + " passed");
      }

      if (game.currentState().playedPoint) {
        console.log(
          game.currentState().color +
            " played " +
            game.currentState().playedPoint.y +
            "," +
            game.currentState().playedPoint.x
        );
        let y = game.currentState().playedPoint.y + 1;
        let x = game.currentState().playedPoint.x + 1;

        if (colors[game.currentState().color] === self.state.stone) {
          self.setState({ yourTurn: false });
          self.sendMove(x, y);
        }
      }
    };

    this.setState({ game });
  }

  sendMove(x, y) {
    fetch(
      `/api/make_a_move?id=${encodeURIComponent(this.state.id)}&move=${y}-${x}`
    )
      .then(response => response.json())
      .then(state => this.setState(state));
  }

  resetGame() {
    const { game } = this.state;
    const { moveNumber } = game.currentState();
    for (let i = 0; i < moveNumber; i++) {
      game.undo();
    }
  }

  handleChange(event) {
    this.setState({ input: event.target.value });
  }

  register(event) {
    event.preventDefault();
    this.setState({ name: this.state.input });
    fetch(
      `/api/register?id=${encodeURIComponent(
        this.state.id
      )}&name=${encodeURIComponent(this.state.input)}`
    )
      .then(response => response.json())
      .then(state => this.setState(state));
  }

  render() {
    const {
      name,
      stone,
      hist,
      input,
      refused,
      yourTurn,
      ended,
      msg
    } = this.state;

    console.log(hist);

    return (
      <div className="App">
        <header className="App-header">
          {name ? (
            <div>
              <p>Welcome gui player</p>
              <code>{name}</code>
              <br />
            </div>
          ) : (
            <div>
              <p>{msg}</p>
              <form
                onSubmit={this.register}
                className={refused ? "hide" : null}
              >
                <label htmlFor="name">Enter your name: </label>
                <input
                  id="name"
                  type="text"
                  value={input}
                  onChange={this.handleChange}
                />
                <button type="submit">Submit</button>
              </form>
            </div>
          )}

          {stone ? (
            <p>You have been assigned the stone: {stone}</p>
          ) : (
            <p>
              {refused
                ? "The server does not seem to be running right now!"
                : "Waiting for server..."}
            </p>
          )}

          {ended && (
            <p>
              Game has just ended. Waiting for the next match or tournament is
              over...
            </p>
          )}
        </header>
        <section>
          <div
            className={classnames(
              stone ? null : "hide",
              yourTurn ? null : "no-clicking"
            )}
          >
            <div class="tenuki-board" data-include-coordinates={true}></div>

            <div class="controls">
              <div class="buttons">
                <a class="pass" href="#">
                  Pass
                </a>
              </div>

              <div class="game-info">
                <p>&nbsp;</p>
              </div>
              <div class="text-info">
                <p></p>
              </div>
            </div>
          </div>
        </section>
      </div>
    );
  }
}

export default App;
