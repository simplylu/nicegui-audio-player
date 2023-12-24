// Get the audio element and play/pause button by class name
const audio = document.querySelector(".audio");
const playPauseBtn = document.querySelector(".play-pause");

// Function to play audio
function playAudio() {
    audio.play();
    // Update play/pause button text content to "pause"
    playPauseBtn.querySelector(".material-icons").textContent = "pause";
}

// Function to pause audio
function pauseAudio() {
    audio.pause();
    // Update play/pause button text content to "play_arrow"
    playPauseBtn.querySelector(".material-icons").textContent = "play_arrow";
}

// Function to set audio current time to the beginning
function beginAudio() {
    audio.currentTime = 0;
}

// Function to set audio current time to the end (simulating next track)
function nextAudio() {
    audio.currentTime = audio.duration;
}

// Check if mediaSession is supported in the browser
if ('mediaSession' in navigator) {
    // Set media session action handlers
    navigator.mediaSession.setActionHandler('play', playAudio);
    navigator.mediaSession.setActionHandler('pause', pauseAudio);
    navigator.mediaSession.setActionHandler('previoustrack', beginAudio);
    navigator.mediaSession.setActionHandler('nexttrack', nextAudio);
}