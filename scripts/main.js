

    const canvas = document.getElementById("canvas1");
    const ctx = canvas.getContext("2d");
    canvas.width = 600;
    canvas.height = 600;

    class Game {
        constructor(width, height){
            this.width = width;
            this.height = height;
            this.cellSize = this.width/3;
            this.board = [
            [null, null, null], //tablica gry
            [null, null, null],
            [null, null, null]
            ];
            this.currentPlayer = "X"; // Zaczyna X
        };

        switchPlayer() {
        this.currentPlayer = this.currentPlayer === "X" ? "O" : "X";
        console.log("switched player to:", this.currentPlayer); // print o zmianie gracza
        }

        checkIfWin() {
        const b = this.board;

        //check row
        for (let row = 0; row < 3; row++ ){
            if (b[row][0] && b[row][0] === b[row][1] && b[row][1] === b[row][2]) {
                console.log("koniec gry wygrał:", this.currentPlayer);
            }
        }

        //check col
        for (let col = 0; col < 3; col++ ){
            if (b[0][col] && b[0][col] === b[1][col] && b[1][col] === b[2][col]) {
                console.log("koniec gry wygrał:", this.currentPlayer);
            }
        }

        //check diagonal from [0][0]
            if (b[0][0] && b[0][0] === b[1][1] && b[1][1] === b[2][2]) {
                console.log("koniec gry wygrał:", this.currentPlayer);
            }

        //check diagonal from [0][3]
            if (b[0][2] && b[0][2] === b[1][1] && b[1][1] === b[2][0]) {
                    console.log("koniec gry wygrał:", this.currentPlayer);
            }
        }

        drawBoard(ctx) {
        ctx.strokeStyle = "black";
        ctx.lineWidth = 5;

        // Pionowe linie
        ctx.beginPath();
        ctx.moveTo(this.cellSize, 0);
        ctx.lineTo(this.cellSize, this.height);
        ctx.stroke();

        ctx.beginPath();
        ctx.moveTo(this.cellSize * 2, 0);
        ctx.lineTo(this.cellSize * 2, this.height);
        ctx.stroke();

        // Poziome linie
        ctx.beginPath();
        ctx.moveTo(0, this.cellSize);
        ctx.lineTo(this.width, this.cellSize);
        ctx.stroke();

        ctx.beginPath();
        ctx.moveTo(0, this.cellSize * 2);
        ctx.lineTo(this.width, this.cellSize * 2);
        ctx.stroke();
        }

        drawSymbol(ctx, row, col, symbol) {
        const x = col * this.cellSize;
        const y = row * this.cellSize;

        ctx.strokeStyle = "black";
        ctx.lineWidth = 10;

        if (symbol === "X") {
            ctx.beginPath();
            ctx.moveTo(x + 20, y + 20);
            ctx.lineTo(x + this.cellSize - 20, y + this.cellSize - 20);
            ctx.moveTo(x + this.cellSize - 20, y + 20);
            ctx.lineTo(x + 20, y + this.cellSize - 20);
            ctx.stroke();
        }

        if (symbol === "O") {
            ctx.beginPath();
            ctx.arc(x + this.cellSize / 2, y + this.cellSize / 2, this.cellSize / 2 - 30, 0, Math.PI * 2);
            ctx.stroke();
        }
        }

    }


    //Start Rozgrywki
    const game = new Game(canvas.width, canvas.height);
    game.drawBoard(ctx);

    canvas.addEventListener("click", function(event) {
    const rect = canvas.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;

    const col = Math.floor(x / game.cellSize);
    const row = Math.floor(y / game.cellSize);

    console.log("Kliknięto:", { row, col, player: game.currentPlayer });

    // Warunek sprawdzający czy pole jest puste i wstawiający odpowiedni symbol
    if (game.board[row][col] === null) {
        game.board[row][col] = game.currentPlayer;
        game.drawSymbol(ctx, row, col, game.currentPlayer);
        game.checkIfWin();
        game.switchPlayer();
    }

});

