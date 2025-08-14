import { Game } from './game.js';

const canvas = document.getElementById("canvas1");
const ctx = canvas.getContext("2d");
const gameSize = 600;
canvas.width = gameSize;
canvas.height =  gameSize;


let gameActive = true; //flaga do kontrolowania funkcji
let gameStarted = false;

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

//Funkcje pomocnicze
function handleCanvasClick(event) {
    gameStarted = true;
    const { row, col } = getClickedCell(event);
    console.log("Kliknięto:", { row, col});

    switch(game.mode){
      case "PvP":
        makePlayerMove(row, col);
        break;
      case "PvE":
        //implementacja ruchu AI
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
    if (!gameStarted) { //w warunku będzie wartość gameOver z sesji
        game.mode = game.mode === "PvP" ? "PvE" : "PvP";
        modeToggleBtn.textContent = `Zmień tryb (obecnie: ${game.mode})`;
    } else {
        console.warn("Nie można zmienić trybu gry podczas trwania rozgrywki!");
    }
}

function makePlayerMove(row, col) {
    if (!gameActive) return;

    fetch("/player-move", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ row: row, col: col })
    })
    .then(res => {
    return res.json().then(data => {
            if (!res.ok) {
                // Obsługa błędu z backendu
                console.warn("Błąd ruchu gracza:", data.error);
                alert(data.error || "Wystąpił błąd przy ruchu");
                throw new Error(data.error); // zatrzymuje dalsze then()
            }
            return data;
        });
    })
    .then(data => {
        // Wykonaj ruch
    game.drawSymbol(row, col, data.current_player);
    console.log("ruch wykonał gracz:", data.current_player);

    if (data.winner) {
    gameActive = false;
    game.animateWinningLine(data.winning_line);
        setTimeout(() => {
                alert(`Wygrał gracz: ${data.current_player}`)
                game.clearBoard();
                gameActive = true;
                gameStarted = false;
            }, 1000); // 1000 ms = 1 sekunda
    } else if (data.draw){
    gameActive = false;
        setTimeout(() => {
                alert("Remis!")
                game.clearBoard();
                gameActive = true;
                gameStarted = false;
        }, 1000);
    }
    })
    .catch(err => console.error("Błąd:", err));
}