import { Game } from './game.js';

    const canvas = document.getElementById("canvas1");
    const ctx = canvas.getContext("2d");
    canvas.width = 600;
    canvas.height = 600;

    
    //Start Rozgrywki
    const game = new Game(canvas.width, canvas.height, ctx); //utworzenie obiektu gry
    game.drawBoard();


    //nasłuchiwacz kliknięć
    canvas.addEventListener("click", function(event) {
        if(!game.gameOver) {
        const rect = canvas.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;

        const col = Math.floor(x / game.cellSize);
        const row = Math.floor(y / game.cellSize);

        console.log("Kliknięto:", { row, col, player: game.currentPlayer });

            // Warunek sprawdzający czy pole jest puste i wstawiający odpowiedni symbol
            if (game.board[row][col] === null) {
                game.board[row][col] = game.currentPlayer;
                game.drawSymbol(row, col, game.currentPlayer);
                const winningCells = game.checkIfWin();
                if (winningCells){
                    game.gameOver = true; // ustawienie zmiennej gameOver na false powoduje zatrzymanie nasłuchiwacza kliknięć i musi być wykonana ZARAZ PO zakończeniu rozgrywki
                    game.animateWinningLine(winningCells, () => {
                        game.results(true);
                    });
                } else if (game.checkIfDraw()){
                    setTimeout(() => {
                        game.results(false);
                    }, 500);
                  } else {game.switchPlayer();}
            }

            
        }
    });

