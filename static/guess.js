const form = document.querySelector('#guess-form');
const result = document.querySelector('#guess-result');
let score = 0;

async function formHandler(e){
    e.preventDefault();
    console.log(form.guess.value);
    response = await axios.get('/guess', {
        params: {guess: form.guess.value}
    });

    showGuessResult(response.data.response);
    if (response.data.response === "ok"){
        updateScore(form.guess.value.length)
    }
}

function showGuessResult(text){
    result.innerText = text;
}

function updateScore(num){
    score += num
    console.log(score)
}

form.addEventListener('submit', formHandler)