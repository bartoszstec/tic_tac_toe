export class Game {
        constructor(width, height, ctx){
            this.width = width;
            this.height = height;
            this.ctx = ctx;
            this.cellSize = this.width/3;
            this.mode = "PvP"; // Tryb gry: PvP lub PvE
            this.boardState = [
                [null, null, null], //tablica gry
                [null, null, null],
                [null, null, null]
            ];
        };

        clearBoard(){
            this.ctx.clearRect(0, 0, this.width, this.height);
            this.boardState = [
                [null, null, null], //tablica gry
                [null, null, null],
                [null, null, null]
            ];
            this.drawBoard(this.ctx);
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

        animateWinningLine(winningCells) {
            if (!winningCells || winningCells.length !== 3) return;

            const ctx = this.ctx;

            // Wyznacz punkty start i end linii
            const [startRow, startCol] = winningCells[0];
            const [endRow, endCol] = winningCells[2];

            const startX = startCol * this.cellSize + this.cellSize / 2;
            const startY = startRow * this.cellSize + this.cellSize / 2;
            const endX = endCol * this.cellSize + this.cellSize / 2;
            const endY = endRow * this.cellSize + this.cellSize / 2;

            const steps = 30;
            let progress = 0;

            const draw = () => {
                ctx.clearRect(0, 0, this.width, this.height);
                this.drawBoard();
                this.drawAllSymbols();

                ctx.strokeStyle = "rgba(255,0,0,0.8)";
                ctx.lineWidth = 8;
                ctx.lineCap = "round"; // dla symetrycznych końcówek

                ctx.beginPath();
                ctx.moveTo(startX, startY);

                const currentX = startX + (endX - startX) * (progress / steps);
                const currentY = startY + (endY - startY) * (progress / steps);

                ctx.lineTo(currentX, currentY);
                ctx.stroke();

                progress++;
                if (progress <= steps) {
                    requestAnimationFrame(draw);
                }
            };

            draw();
        }

        drawSymbol(row, col, symbol) {
        this.boardState[row][col] = symbol;
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

        drawAllSymbols() {
            for (let row = 0; row < 3; row++) {
                for (let col = 0; col < 3; col++) {
                    const symbol = this.boardState[row][col];
                    if (symbol) {
                        this.drawSymbol(row, col, symbol);
                    }
                }
            }
        }

    }