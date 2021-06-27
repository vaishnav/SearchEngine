function message() {
    alert('Functionality yet to be implemented!')
}

document.addEventListener('DOMContentLoaded', function(){
    console.log("hello")
    document.querySelector('form').onsubmit = message;
});

