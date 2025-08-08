import { Game } from './game.js';

const canvas = document.getElementById("canvas1");
const ctx = canvas.getContext("2d");
const gameSize = 600;
canvas.width = gameSize;
canvas.height =  gameSize;

    
// Inicjalizacja Gry
const game = new Game(canvas.width, canvas.height, ctx); //utworzenie obiektu gry
game.drawBoard();


// Obsługa kliknięcia na canvas
canvas.addEventListener("click", handleCanvasClick);

// Obsługa zmiany trybu
const modeToggleBtn = document.getElementById("modeToggle");
modeToggleBtn.addEventListener("click", toggleGameMode);


//Funkcje pomocnicze
function handleCanvasClick(event) {
    if (game.gameOver) return;

    const { row, col } = getClickedCell(event);

    if (game.board[row][col] !== null) return;

    console.log("Kliknięto:", { row, col, player: game.currentPlayer });
    game.gameStarted = true;

    game.board[row][col] = game.currentPlayer; // Ruch gracza zapisany do tablicy
    game.drawSymbol(row, col, game.currentPlayer);
    game.saveMoveToLog(row, col);

    if (game.tryEndGame()) return;

    if (game.mode === "PvP") {
        game.switchPlayer();
    } else if (game.mode === "PvE") {
        game.switchPlayer();
        game.makeAIMove();

        if (game.tryEndGame()) return;

        game.switchPlayer();
    } else {
        console.warn("Nieznany tryb gry:", game.mode);
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
    if (!game.gameStarted) {
        game.mode = game.mode === "PvP" ? "PvE" : "PvP";
        modeToggleBtn.textContent = `Zmień tryb (obecnie: ${game.mode})`;
    } else {
        console.warn("Nie można zmienić trybu gry podczas trwania rozgrywki!");
    }
}