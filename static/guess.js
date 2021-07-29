function app(){
    const form = document.querySelector('#guess-form');
    const result = document.querySelector('#guess-result');
    const scoreDisplay = document.querySelector('#score');
    const timerDisplay = document.querySelector('#timer');
    let globalTimer;
    let timeRemain = +timerDisplay.innerText.split(" ")[1];

    async function formHandler(e){
        e.preventDefault();
        console.log(form.guess.value);
        response = await axios.post('/guess', {
            data: {guess: form.guess.value}
        });

        showGuessResult(response.data.response);
        updateScore(response.data.score)
        form.guess.value = '';
    }

    function timeoutHandler(){
        timeRemain -= 1;
        timerDisplay.innerText = "Time: " + timeRemain;
        if (timeRemain <= 0){
            clearInterval(globalTimer);
            const btn = document.querySelector('#guess-btn');
            btn.setAttribute('disabled', '');
            axios.post('/timeout');
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

    form.addEventListener('submit', formHandler);
    if (timeRemain > 0){
        globalTimer = setInterval(timeoutHandler, 1000);
    }
}

app();