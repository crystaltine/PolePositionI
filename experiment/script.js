const canvas = document.getElementById("cw");
const context = canvas.getContext("2d");
context.globalAlpha = 0.5;

let car;

let moveDirection = 1;
// on arrow key press
window.addEventListener("keydown", (e) => {
    if (e.key === "ArrowRight") {
        moveDirection = 1;
    }
    else if (e.key === "ArrowLeft") {
        moveDirection = -1;
    }
})

car = new Particle(
    innerWidth / 2,
    innerHeight / 2,
    "#FF0000",
);

setSize();
anim();


function setSize() {
  canvas.height = innerHeight;
  canvas.width = innerWidth;
}

// Particle should be a 100x100 rectangle that just moves
function Particle(x, y, color) {
  this.x = x;
  this.y = y;
  this.color = color;

  // draw the particle
    context.beginPath();
    context.lineWidth = 100;
    context.strokeStyle = this.color;


  this.move = (direction) => {
    const ls = {
      x: this.x,
      y: this.y,
    };

    if (direction === -1) { this.x = this.x - 5}
    else if (direction === 1) { this.x = this.x + 5}

    context.beginPath();
    context.lineWidth = 200;
    context.strokeStyle = this.color;
    context.moveTo(ls.x, ls.y);
    context.lineTo(this.x, this.y);
    context.stroke();
  };
}

function anim() {
  requestAnimationFrame(() => {anim(moveDirection)});

  context.fillStyle = "rgba(0,0,40,0.05)";
  context.fillRect(0, 0, canvas.width, canvas.height);

  car.move(moveDirection);
}
