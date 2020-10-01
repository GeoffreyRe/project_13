$(document).ready(function(){
    //we wait until the page is fully loaded
    //we add an event listener 'hover' wich takes two functions
    //the first one is when we 'enter' into the element
    //the second-one is when we leave the element

// we add a function to get csrftoken to allow post request to django
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    const csrftoken = getCookie('csrftoken');

    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    // we add the csrftoken to header of requests
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    })


    $('.project-div').hover(function(){
        // we add a bootstrap class wich adds a shadow
        $(this).addClass('shadow')
    },
    function(){
        //we remove the bootstrap class previously added
        $(this).removeClass('shadow')
    })

    // we create a click event to open a popup with a form for creating new project
    $('.button-create-project').click(function(){
        $('.shadow-popup').show();
        $('.body-content').css('filter', 'blur(1px)')
        $('.popup-creation-project').removeClass('d-none');
    })

    //we create a click event to close popup form
    $('.button-close-popup').click(function(){
        $('.popup-creation-project').addClass('d-none');
        $('.body-content').css('filter', 'blur(0px)')
        $('.shadow-popup').hide();
    })

    $('form').submit(function(event){
        event.preventDefault();
        $.post('project_exists',{project_name : $('#id_name').val()},
            function(data, status, xhr){
                if (status=="success"){
                    project_exists = data["project_exists"]
                    if (project_exists === false)
                    {
                        // we unbind submit event we just created (we are inside) and we call the normal submit method
                        console.log("we unbind")
                        $('form').unbind('submit').submit()
                    }
                    else {
                        // we inform user that a project where he is the creator already exists
                        if ($('#text_project_exists').length === 0)
                        {
                        let pEl = document.createElement("p")
                        pEl.innerHTML = "Vous êtes déjà le créateur d'un projet avec le même nom !"
                        pEl.id = "text_project_exists"
                        pEl.style.color = 'red'
                        $('.popup-creation-project').append(pEl)
                        }
                    }
                }
                else {
                    console.log("problème envoi requête AJAX")
                }
            }
        )
    })

    // we add an event listener on button to accept invitations
    $('.btn-accepted').click(function(){
        // we will try to convert an invitation to a projet if the user click on the button
            console.log("Nous allons accepter l'invitation", this.id.split("_")[1]);
            let button_elt = this
            // we send an ajax request with data = id of invitation to validate
            // if response.success = true, it means that the invitation has been converted
            // and user can now see project in project list
            // if response.success = false, it means that there was a problem during validation
            // (integrity Error, the id was not a number etc...) and then we inform user
            $.ajax({
                url : 'invitation/to-project',
                type :"post",
                data : {
                    'invitation_id' : this.id.split("_")[1]
                },
                success : function(response){
                    console.log(response);
                    if (response.success == true)
                    {
                        let errorMessageElt = $('#error-message-invitation-' + button_elt.id.split("_")[1])
                        if (errorMessageElt.length !== 0){
                            errorMessageElt.hide();
                        }
                        $(button_elt).parent().hide();
                        $(button_elt).parent().parent().css('background-color', 'rgba(0,124,45,0.3)');
                        $(button_elt).parent().parent().removeClass('justify-content-between');
                        $(button_elt).parent().parent().addClass('justify-content-center');
                    }
                    else if (response.success == false)
                    {
                        if ($('#error-message-invitation-' + button_elt.id.split("_")[1]).length === 0)
                        {
                        let pErrorElt = document.createElement('p');
                        pErrorElt.id = "error-message-invitation-" + button_elt.id.split("_")[1]
                        pErrorElt.innerText = "un problème est survenu lors de la validation de l'invitation";
                        $(pErrorElt).css('color', 'red');
                        $(button_elt).parent().parent().before(pErrorElt);
                        }
                        else
                        {
                            $('#error-message-invitation-' + button_elt.id.split("_")[1]).text("un problème est survenu lors de la validation de l'invitation");
                        }
                    }
                },
                error : function(response){
                    console.log("error requête ajax")
                },
            })

    })


    // we will add event listener to btn-refused buttons
    $('.btn-refused').click(function(){
        let button_elt = this
        // we will send an ajax request with values of if of invitation
        // if request.success == true, it means that the invitation has been correctly refused,
        // we change the layout of the page
        // else, we inform user that there was a problem during the process
        $.ajax({
            url : 'invitation/refused',
            type :"post",
            data : {
                'invitation_id' : this.id.split("_")[1]
            },
            success : function(response){
                console.log(response);
                if (response.success == true)
                {
                    let errorMessageElt = $('#error-message-invitation-' + button_elt.id.split("_")[1])
                    if (errorMessageElt.length !== 0){
                        errorMessageElt.hide();
                    }
                    $(button_elt).parent().hide();
                    $(button_elt).parent().parent().css('background-color', 'rgba(202,88,88,0.3)');
                    $(button_elt).parent().parent().removeClass('justify-content-between');
                    $(button_elt).parent().parent().addClass('justify-content-center');
                }
                else if (response.success == false)
                {
                    if ($('#error-message-invitation-' + button_elt.id.split("_")[1]).length === 0)
                    {
                    let pErrorElt = document.createElement('p');
                    pErrorElt.id = "error-message-invitation-" + button_elt.id.split("_")[1];
                    pErrorElt.innerText = "un problème est survenu lors du refus de l'invitation";
                    $(pErrorElt).css('color', 'red');
                    $(button_elt).parent().parent().before(pErrorElt);
                    }
                    else
                    {
                        $('#error-message-invitation-' + button_elt.id.split("_")[1]).text("un problème est survenu lors du refus de l'invitation");
                    }
                }
            },
            error : function(response){
                console.log("error requête ajax")
            },
        })
    })


})