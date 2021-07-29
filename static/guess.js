const form = document.querySelector('#guess-form');

async function formHandler(e){
    e.preventDefault();
    console.log(form.guess.value);
    response = await axios.get('/guess', {
        params: {guess: form.guess.value}
    })
    console.log(response.data.response)
}

form.addEventListener('submit', formHandler)