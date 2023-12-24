// Get audio and canvas elements by class name
const audioEl = document.querySelector(".audio");
const canvasEl = document.querySelector(".animation-canvas");

// Set initial style for the canvas
canvasEl.style.zIndex = "-10";

// Constants for width and height factors
const wFactor = 1.9;
const hFactor = 1.75;

// Create a Wave instance with audio and canvas elements
const wave = new Wave(audioEl, canvasEl);

// Set canvas width and height based on the content card dimensions
canvasEl.width = document.querySelector(".content-card").clientWidth * wFactor;
canvasEl.height = document.querySelector(".content-card").clientHeight * hFactor;

// Add a square animation to the wave
wave.addAnimation(new wave.animations.Square({
    count: 160,
    lineColor: { gradient: ["#21D4FD", "#B721FF"] },
    diameter: 225,
    rounded: true
}));

// Resize event handler to update canvas dimensions on window resize
window.onresize = () => {
    canvasEl.width = document.querySelector(".content-card").clientWidth * wFactor;
    canvasEl.height = document.querySelector(".content-card").clientHeight * hFactor;
};