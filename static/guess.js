const form = document.querySelector('#guess-form');
const result = document.querySelector('#guess-result');
const scoreDisplay = document.querySelector('#score');

async function formHandler(e){
    e.preventDefault();
    console.log(form.guess.value);
    response = await axios.get('/guess', {
        params: {guess: form.guess.value}
    });

    showGuessResult(response.data.response);
    updateScore(response.data.score)
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