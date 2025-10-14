import { Game } from './game.js';

const canvas = document.getElementById("canvas1");
const ctx = canvas.getContext("2d");

// Ustawienie początkowej wartości gameSize
//let gameSize = 600;
//canvas.width = gameSize;
//canvas.height =  gameSize;

// flags used to control functions
let gameActive = true;
let gameStarted = false;
let aiFirstMoveFlag = false;

// Inicjalizacja gry z dynamicznym rozmiarem
let gameSize = getCanvasSize();
canvas.width = gameSize;
canvas.height = gameSize;

// Game Initialization
const game = new Game(gameSize, ctx); // creating a game object
game.drawBoard();

fetch("/start-game") // informing the backend about the game start
  .then(res => res.json())
  .then(data => {
    console.log("The game has started:", data);
  })
  .catch(err => console.error("Error when starting the game:", err));

    window.addEventListener('resize', handleResize);

// Canvas click handling
    canvas.addEventListener("click", handleCanvasClick);

    // Mode change handling
    const modeToggleBtn = document.getElementById("modeToggle");
    modeToggleBtn.addEventListener("click", toggleGameMode);

    const startBtn = document.getElementById("startButton");
    startBtn.addEventListener('click', firstAiMove);

// Funkcja do pobierania aktualnego rozmiaru canvas z CSS
function getCanvasSize() {
    const computedStyle = getComputedStyle(canvas);
    const width = parseInt(computedStyle.width);
    const height = parseInt(computedStyle.height);

    // Zwróć mniejszą wartość, aby zachować kwadratowy kształt
    return Math.min(width, height);
}

// Funkcja obsługująca zmianę rozmiaru okna
function handleResize() {
        const newSize = getCanvasSize();

        // Aktualizuj rozmiar tylko jeśli się zmienił
        if (newSize !== gameSize) {
            gameSize = newSize;
            canvas.width = gameSize;
            canvas.height = gameSize;

            // Aktualizuj rozmiar w obiekcie gry
            game.width = gameSize;
            game.height = gameSize;
            game.cellSize = gameSize / 3;

            // Przerysuj planszę
            game.drawBoard();
            game.drawAllSymbols();
        }
}

// Helper functions
function handleCanvasClick(event) {
    gameStarted = true;
    const { row, col } = getClickedCell(event);

    switch(game.mode){
      case "PvP":
        makePlayerMove(row, col);
        break;
      case "Player vs AI":
        performAiGame(row, col);
        break;
      case "AI vs Player":
        if (!aiFirstMoveFlag) {
            gameActive = false;
            gameStarted = false;
            console.warn("Click the start button to start playing with AI");
            alert("Click the start button to start playing with AI");
            return;
        }

        performAiGame(row, col);
        break;
    default:
    }
}

function getClickedCell(event) {
    const rect = canvas.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;

    return {
        col: Math.floor(x / game.cellSize),
        row: Math.floor(y / game.cellSize),
    };
}

function toggleGameMode() {
    if (!gameStarted) {
        if (game.mode === "PvP"){
            game.mode = "Player vs AI"
            startBtn.style.display = 'none';
            fetch("/change-strategy", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ strategy: "defence" })
            });
            }
            else if (game.mode === "Player vs AI"){
                game.mode = "AI vs Player"
                startBtn.style.display = 'block';
                fetch("/change-strategy", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ strategy: "attack" })
                });
                }
                else if (game.mode === "AI vs Player") {
                game.mode = "PvP"
                startBtn.style.display = 'none';
                }
        modeToggleBtn.textContent = `Game Mode: ${game.mode}`;
    } else {
        console.warn("You cannot change the game mode during the game!");
        alert("You cannot change the game mode during the game!");
    }
}

function makePlayerMove(row, col) {
    if (!gameActive) return Promise.resolve(null);

    //  Player's move
    return fetch("/player-move", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ row: row, col: col })
    })
    .then(res => res.json())
    .then(data => {
        if (data.error) {
            console.warn("Player's move error:", data.error);
            alert(data.error || "An error occurred while moving");
            throw new Error(data.error);
        }

    // Making a move
    game.drawSymbol(row, col, data.current_player);
    console.log("move made by:", data.current_player);
    tryEndGame(data);

    return data; // <- it is important that PvE can check winner/draw
    })
}

function performAiGame(row, col) {
    makePlayerMove(row, col)
    .then(data => {
        if (!data || !gameActive) return;

        return fetch("/AI-move", { method: "POST" })
            .then(res => res.json())
            .then(aiData => {
                console.log("move made by:", aiData.current_player);
                game.drawSymbol(aiData.aiRow, aiData.aiCol, aiData.current_player);
                tryEndGame(aiData);
            });
    })
    .catch(err => console.error("PvE error:", err));
}

function firstAiMove() {
    if (!aiFirstMoveFlag) {
        startBtn.classList.remove('blink');
        fetch("/AI-move", { method: "POST" })
            .then(res => res.json())
            .then(aiData => {
                console.log("move made by:", aiData.current_player);
                game.drawSymbol(aiData.aiRow, aiData.aiCol, aiData.current_player);

                // set all flags after move is done
                aiFirstMoveFlag = true;
                gameActive = true;
                gameStarted = true;
            })
            .catch(err => console.error("AI's First Move Error:", err));
    }
}

function tryEndGame(data) {
    if (data.winner) {
        gameActive = false;
        game.animateWinningLine(data.winning_line);
        setTimeout(() => {
            alert(`VICTORY: ${data.current_player}`);
            resetGame();
        }, 1000);
    } else if (data.draw) {
        gameActive = false;
        setTimeout(() => {
            alert("Draw!");
            resetGame();
        }, 1000);
    }
}

function resetGame() {
    game.clearBoard();
    gameActive = true;
    gameStarted = false;
    aiFirstMoveFlag = false;
    startBtn.classList.add('blink');
}