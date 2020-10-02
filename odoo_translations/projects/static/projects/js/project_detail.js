$(document).ready(function(){

    let vertical_menu_open = false
    $('.li-to-extend').click(function(){
        if (vertical_menu_open === false)
        {
            $(this).children().css('transform', 'rotate(0.25turn)')
            $(this).next("ul").css('visibility', 'visible')
            $(this).next("ul").css('opacity', '1')
            vertical_menu_open = true
        }
        else
        {
            $(this).children().css('transform', 'rotate(0turn)')
            $(this).next("ul").css('opacity', '0')
            setTimeout(function(){
                $('.li-to-extend').next("ul").css('visibility', 'hidden')
              }, 500)
            vertical_menu_open = false 
        }
    })



}) //fin fonction ready