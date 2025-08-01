export class Game {
        constructor(width, height, ctx){
            this.width = width;
            this.height = height;
            this.ctx = ctx;
            this.cellSize = this.width/3;
            this.gameOver = false;
            this.board = [
            [null, null, null], //tablica gry
            [null, null, null],
            [null, null, null]
            ];
            this.currentPlayer = "X"; // Zaczyna X
            this.mode = "PvP"; // Tryb gry: PvP lub PvE
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
                return [[row, 0], [row, 1], [row, 2]];
            }
        }

        //check col
        for (let col = 0; col < 3; col++ ){
            if (b[0][col] && b[0][col] === b[1][col] && b[1][col] === b[2][col]) {
                return [[0, col], [1, col], [2, col]];
            }
        }

        //check diagonal from [0][0]
            if (b[0][0] && b[0][0] === b[1][1] && b[1][1] === b[2][2]) {
                return [[0, 0], [1, 1], [2, 2]];
            }

        //check diagonal from [0][3]
            if (b[0][2] && b[0][2] === b[1][1] && b[1][1] === b[2][0]) {
                return [[0, 2], [1, 1], [2, 0]];
            }

        return null;
        }

        checkIfDraw() {
        return this.board.flat().every(cell => cell !== null);
        }

        results(winner){
            this.gameOver = true;
            if (winner){
                alert(`Koniec gry wygrał: ${this.currentPlayer}`);
            } else {alert("Remis!")}

            this.resetGame(); 
        }

        resetGame(){
            this.board = [
            [null, null, null],
            [null, null, null],
            [null, null, null]
            ];

            this.currentPlayer = "X";
            this.ctx.clearRect(0, 0, this.width, this.height);
            this.drawBoard(this.ctx);
            this.gameOver = false;
        }

        drawBoard() {
            const ctx = this.ctx;
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

        animateWinningLine(winningCells, callback) {
            const ctx = this.ctx;
            const [startRow, startCol] = winningCells[0];
            const [endRow, endCol] = winningCells[2];

            const startX = startCol * this.cellSize + this.cellSize / 2;
            const startY = startRow * this.cellSize + this.cellSize / 2;
            const endX = endCol * this.cellSize + this.cellSize / 2;
            const endY = endRow * this.cellSize + this.cellSize / 2;

            let progress = 0;
            const steps = 30;
            const delay = 15; // ms między krokami

            const drawStep = () => {
                ctx.clearRect(0, 0, this.width, this.height);
                this.drawBoard();

                // Rysuj ponownie wszystkie symbole
                for (let row = 0; row < 3; row++) {
                    for (let col = 0; col < 3; col++) {
                        if (this.board[row][col]) {
                            this.drawSymbol(row, col, this.board[row][col]);
                        }
                    }
                }

                // Styl linii
                ctx.strokeStyle = "rgba(255, 0, 0, 0.8)";
                ctx.lineWidth = 8;
                ctx.lineCap = "round";

                ctx.beginPath();
                ctx.moveTo(startX, startY);

                const currentX = startX + (endX - startX) * (progress / steps);
                const currentY = startY + (endY - startY) * (progress / steps);

                ctx.lineTo(currentX, currentY);
                ctx.stroke();

                if (progress < steps) {
                    progress++;
                    requestAnimationFrame(drawStep);
                } else if (callback) {
                    setTimeout(callback, 800); // chwila pauzy po zakończeniu animacji
                }
            };

            drawStep();
        }

        drawSymbol(row, col, symbol) {
        const x = col * this.cellSize;
        const y = row * this.cellSize;
        const ctx = this.ctx;
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