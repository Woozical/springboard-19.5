const form = document.querySelector('#guess-form');
const result = document.querySelector('#guess-result');
const scoreDisplay = document.querySelector('#score');
const timerDisplay = document.querySelector('#timer');
let started = false;
let globalTimer;

async function formHandler(e){
    e.preventDefault();
    console.log(form.guess.value);
    response = await axios.post('/guess', {
        data: {guess: form.guess.value}
    });

    showGuessResult(response.data.response);
    updateScore(response.data.score)

    if (!started){
        globalTimer = setInterval(timeoutHandler, 1000);
        started = true;
    }

}

function timeoutHandler(){
    time = +timerDisplay.innerText.split(" ")[1];
    time -= 1;
    timerDisplay.innerText = "Time: " + time;
    if (time <= 0){
        clearInterval(globalTimer);
        const btn = document.querySelector('#guess-btn');
        btn.setAttribute('disabled', '');
    }
}

function showGuessResult(text){
    result.innerText = text;
}

function updateScore(num){
    score = +scoreDisplay.innerText.split(" ")[1];
    score += num;
    scoreDisplay.innerText = "Score: " + score;
}

form.addEventListener('submit', formHandler)