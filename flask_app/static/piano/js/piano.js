// global bool to determine whether the piano can be played
var isSummoned = false;

/* Queue from  https://www.geeksforgeeks.org/implementation-queue-javascript/ 
 I use it for the "weeseeyou" sequence. I modified this queue to only contain 8 items at a time.*/
class Queue {
  constructor() {
      this.items = {}
      this.frontIndex = 0
      this.backIndex = 0
      this.length = 0
  }
  enqueue(item) {
      this.items[this.backIndex] = item
      this.backIndex++

      // this is where I modified it to only contain 8 items at a time
      if (this.length < 8) {
        this.length++
      } 
      else {
        delete this.items[this.frontIndex]
        this.frontIndex++
      }

      return item + ' inserted'
  }
  dequeue() {
      const item = this.items[this.frontIndex]
      delete this.items[this.frontIndex]
      this.frontIndex++
      return item
  }
  peek() {
      return this.items[this.frontIndex]
  }
  get printQueue() {
      return this.items;
  }
  // added to simplify getting the string of the queue
  get toString() {
      let str = ''
      for (let i = this.frontIndex; i < this.backIndex; i++) {
          str += this.items[i]
      }
      return str
  }

}

const pianoKey = document.querySelector('.piano-keys');
// Make letters appear when hovering over piano keys
pianoKey.addEventListener('mouseover', function(event) {
  const pianoKeysLetters = document.querySelectorAll('.piano-keys p'); 

  // Loop through letter in pianoKeysLetters and set display to block

  if (!isSummoned) {
    pianoKeysLetters.forEach(function(letter) {
      letter.style.display = 'block'; 
    });
  }
  else (pianoKeysLetters.forEach(function(letter) {
    letter.style.display = 'none'; 
  }));
});

  pianoKey.addEventListener('mouseout', function(event) {
    const pianoKeysLetters = document.querySelectorAll('.piano-keys p'); 
    // Loop through letter in pianoKeysLetters and set display to none
    pianoKeysLetters.forEach(function(letter) {
      letter.style.display = 'none'; 
    });
  });



// Mapping of keys to piano key selectors and their active colors
// This method allowed me to condense from a mountain of if statements to a function
// See previous commit to see what I had before
const keyMappings = {
  'a': {selector: '.white-key1', activeColor: 'green'},
  's': {selector: '.white-key2', activeColor: 'green'},
  'd': {selector: '.white-key3', activeColor: 'green'},
  'f': {selector: '.white-key4', activeColor: 'green'},
  'g': {selector: '.white-key5', activeColor: 'green'},
  'h': {selector: '.white-key6', activeColor: 'green'},
  'j': {selector: '.white-key7', activeColor: 'green'},
  'k': {selector: '.white-key8', activeColor: 'green'},
  'l': {selector: '.white-key9', activeColor: 'green'},
  ';': {selector: '.white-key10', activeColor: 'green'},
  'w': {selector: '.black-key1', activeColor: '#003300'},
  'e': {selector: '.black-key2', activeColor: '#003300'},
  't': {selector: '.black-key3', activeColor: '#003300'},
  'y': {selector: '.black-key4', activeColor: '#003300'},
  'u': {selector: '.black-key5', activeColor: '#003300'},
  'o': {selector: '.black-key6', activeColor: '#003300'},
  'p': {selector: '.black-key7', activeColor: '#003300'}
};


document.addEventListener('keydown', handleKeyPress);

// Function to handle key press action
function handleKeyPress(event) {
  if (isSummoned) {
    return; // Don't play sounds or change colors if image is displayed
  }
  const key = event.key.toLowerCase();
  const mapping = keyMappings[key];
  
  if (mapping) {
      const pianoKey = document.querySelector(mapping.selector);
      pianoKey.style.backgroundColor = mapping.activeColor;
      playSound(event, pianoKey); 
  }
}


// json object containing urls to the sound files
const sound = {65:"http://carolinegabriel.com/demo/js-keyboard/sounds/040.wav",
                87:"http://carolinegabriel.com/demo/js-keyboard/sounds/041.wav",
                83:"http://carolinegabriel.com/demo/js-keyboard/sounds/042.wav",
                69:"http://carolinegabriel.com/demo/js-keyboard/sounds/043.wav",
                68:"http://carolinegabriel.com/demo/js-keyboard/sounds/044.wav",
                70:"http://carolinegabriel.com/demo/js-keyboard/sounds/045.wav",
                84:"http://carolinegabriel.com/demo/js-keyboard/sounds/046.wav",
                71:"http://carolinegabriel.com/demo/js-keyboard/sounds/047.wav",
                89:"http://carolinegabriel.com/demo/js-keyboard/sounds/048.wav",
                72:"http://carolinegabriel.com/demo/js-keyboard/sounds/049.wav",
                85:"http://carolinegabriel.com/demo/js-keyboard/sounds/050.wav",
                74:"http://carolinegabriel.com/demo/js-keyboard/sounds/051.wav",
                75:"http://carolinegabriel.com/demo/js-keyboard/sounds/052.wav",
                79:"http://carolinegabriel.com/demo/js-keyboard/sounds/053.wav",
                76:"http://carolinegabriel.com/demo/js-keyboard/sounds/054.wav",
                80:"http://carolinegabriel.com/demo/js-keyboard/sounds/055.wav",
                186:"http://carolinegabriel.com/demo/js-keyboard/sounds/056.wav"};


// Queue to hold the last 8 keys pressed
const keyPressQueue = new Queue();

function playSound(e, pianoKey) {
  if (sound[e.keyCode]) {
    const audio = new Audio(sound[e.keyCode]);
    audio.play();
  }
  keyPressQueue.enqueue(e.key);

  if (keyPressQueue.toString === "weseeyou") {
    summonCthulhu();
  } else {
    // Revert the key's color after a delay, but only if isSummoned is false
    setTimeout(function() {
      if (!isSummoned) {
        pianoKey.style.backgroundColor = '';
      }
    }, 300);
  }
}

/* Summons Cthulhu (and plays the audio :D ) */
function summonCthulhu() {

  const cthulhu = new Audio("https://orangefreesounds.com/wp-content/uploads/2020/09/Creepy-piano-sound-effect.mp3");
  cthulhu.play();

  var piano = document.querySelector(".piano");
  var cthulu = document.querySelector(".cthulu");
  var whiteKeys = document.querySelectorAll(".white-keys");
  var blackKeys = document.querySelectorAll(".black-keys");
  var awokenMessage = document.querySelector(".cthulu-message");

  piano.style.background = "#fff"; // display cant be none since parent of image

  // Iterate over whiteKeys and set border for each
  whiteKeys.forEach(function(key) 
  {
      key.style.border = "none";
  });  

  // Iterate over blackKeys and set background & border for each
  blackKeys.forEach(function(key) 
  {
      key.style.background = "#fff";
      key.style.border = "none";
  });  
  

  setTimeout(function() {
    cthulu.style.display = "block";
    awokenMessage.style.display = "block";
  }, 400);

  isSummoned = true;
}