export class Game {
        constructor(size, ctx){
            this.width = size;
            this.height = size;
            this.ctx = ctx;
            this.cellSize = this.width/3;
            this.mode = "PvP"; // Game mode: "PvP" or "Player vs AI" or "AI vs Player"
            this.boardState = [
                [null, null, null], //game board
                [null, null, null],
                [null, null, null]
            ];
        };

        clearBoard(){
            this.ctx.clearRect(0, 0, this.width, this.height);
            this.boardState = [
                [null, null, null],
                [null, null, null],
                [null, null, null]
            ];
            this.drawBoard(this.ctx);
        }

        drawBoard() {
            const ctx = this.ctx;
            ctx.strokeStyle = "black";
            ctx.lineWidth = 5;

            // Border
            ctx.beginPath();
            ctx.rect(ctx.lineWidth/2, ctx.lineWidth/2,
                     this.width - ctx.lineWidth, this.height - ctx.lineWidth);
            ctx.stroke();

            //Internal lines
            ctx.beginPath();

            // Vertical
            for (let i = 1; i <= 2; i++) {
                const x = this.cellSize * i + ctx.lineWidth / 2;
                ctx.moveTo(x, 0);
                ctx.lineTo(x, this.height);
            }

            // Horizontal
            for (let i = 1; i <= 2; i++) {
                const y = this.cellSize * i + ctx.lineWidth / 2;
                ctx.moveTo(0, y);
                ctx.lineTo(this.width, y);
            }

            ctx.stroke();
        }

        animateWinningLine(winningCells) {
            if (!winningCells || winningCells.length !== 3) return;

            const ctx = this.ctx;

            // Mark the start and end points of the line
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
                ctx.lineWidth = Math.max(6, this.width * 0.01);
                ctx.lineCap = "round"; // for symmetrical ends

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
        ctx.lineWidth = Math.max(8, this.width * 0.013);

        const padding = this.cellSize * 0.1; // 10% padding - responsive

        if (symbol === "X") {
            ctx.beginPath();
            ctx.moveTo(x + padding, y + padding);
            ctx.lineTo(x + this.cellSize - padding, y + this.cellSize - padding);
            ctx.moveTo(x + this.cellSize - padding, y + padding);
            ctx.lineTo(x + padding, y + this.cellSize - padding);
            ctx.stroke();
        }

        if (symbol === "O") {
            ctx.beginPath();
            const radius = this.cellSize / 2 - padding;
            ctx.arc(x + this.cellSize / 2, y + this.cellSize / 2, radius, 0, Math.PI * 2);
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