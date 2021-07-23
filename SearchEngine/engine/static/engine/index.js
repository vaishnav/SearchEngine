function message() {
    alert('Functionality yet to be implemented!')
}

document.addEventListener('DOMContentLoaded', function(){
   /**  var form = document.querySelector('#thisform');
    console.log(form);
    document.querySelector('form').onsubmit = function(){
        const query = form.elements[0].value;
        if (query== "") {
            alert("Enter a valid string");
            //return false;
        };
        console.log(query)
            fetch('index/query',{
                method:'POST',
                body: JSON.stringify({
                    query:query,
                })
            })
            //return false;
    }*/
    document.querySelector('#string').onchange = function(){
        var text = document.querySelector('#string').value;
        console.log(text);

    }
});

