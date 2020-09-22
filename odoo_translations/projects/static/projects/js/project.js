$(document).ready(function(){
    //we wait until the page is fully loaded
    //we add an event listener 'hover' wich takes two functions
    //the first one is when we 'enter' into the element
    //the second-one is when we leave the element
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
})