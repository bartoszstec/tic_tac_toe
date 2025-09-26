import { Game } from './game.js';

const canvas = document.getElementById("canvas1");
const ctx = canvas.getContext("2d");
const gameSize = 600;
canvas.width = gameSize;
canvas.height =  gameSize;


let gameActive = true; //flaga do kontrolowania funkcji
let gameStarted = false;
let aiFirstMoveFlag = false;

// Inicjalizacja Gry
const game = new Game(canvas.width, canvas.height, ctx); //utworzenie obiektu gry
game.drawBoard();

fetch("/start-game") //poinformowanie backendu o starcie gry
  .then(res => res.json())
  .then(data => {
    console.log("Gra rozpoczęta:", data);
  })
  .catch(err => console.error("Błąd przy starcie gry:", err));


// Obsługa kliknięcia na canvas
    canvas.addEventListener("click", handleCanvasClick);

    // Obsługa zmiany trybu
    const modeToggleBtn = document.getElementById("modeToggle");
    modeToggleBtn.addEventListener("click", toggleGameMode);

    const startBtn = document.getElementById("startButton");
    startBtn.addEventListener('click', firstAiMove);

//Funkcje pomocnicze
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
            console.warn("Kliknij przycisk start, aby rozpocząć grę z AI");
            alert("Kliknij przycisk start, aby rozpocząć grę z AI");
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
        console.warn("Nie można zmienić trybu gry podczas trwania rozgrywki!");
    }
}

function makePlayerMove(row, col) {
    if (!gameActive) return Promise.resolve(null);

    //  Ruch Gracza
    return fetch("/player-move", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ row: row, col: col })
    })
    .then(res => res.json())
    .then(data => {
        if (data.error) {
            console.warn("Błąd ruchu gracza:", data.error);
            alert(data.error || "Wystąpił błąd przy ruchu");
            throw new Error(data.error);
        }

    // Wykonanie ruchu
    game.drawSymbol(row, col, data.current_player);
    console.log("ruch wykonał gracz:", data.current_player);
    tryEndGame(data);

    return data; // <- ważne, żeby PvE mogło sprawdzić winner/draw
    })
}

function performAiGame(row, col) {
    makePlayerMove(row, col)
    .then(data => {
        if (!data || !gameActive) return;

        return fetch("/AI-move", { method: "POST" })
            .then(res => res.json())
            .then(aiData => {
                console.log("ruch wykonał gracz:", aiData.current_player);
                game.drawSymbol(aiData.aiRow, aiData.aiCol, aiData.current_player);
                tryEndGame(aiData);
            });
    })
    .catch(err => console.error("Błąd PvE:", err));
}

function firstAiMove() {
    if (!aiFirstMoveFlag) {
        startBtn.classList.remove('blink');
        fetch("/AI-move", { method: "POST" })
            .then(res => res.json())
            .then(aiData => {
                console.log("ruch wykonał gracz:", aiData.current_player);
                game.drawSymbol(aiData.aiRow, aiData.aiCol, aiData.current_player);

                // set all flags after move is done
                aiFirstMoveFlag = true;
                gameActive = true;
                gameStarted = true;
            })
            .catch(err => console.error("Błąd pierwszego ruchu AI:", err));
    }
}

function tryEndGame(data) {
    if (data.winner) {
        gameActive = false;
        game.animateWinningLine(data.winning_line);
        setTimeout(() => {
            alert(`Wygrał gracz: ${data.current_player}`);
            resetGame();
        }, 1000);
    } else if (data.draw) {
        gameActive = false;
        setTimeout(() => {
            alert("Remis!");
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