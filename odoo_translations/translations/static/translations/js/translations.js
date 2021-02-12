$(document).ready(function(){


    // defines action to be executed when we click on reset button
    $('.reset-translation').click(function(){
        // we retrieve block_id we set in dataset attribute
        let blockId = $(this)[0].dataset.blockId;

        // then, we send via get request the block id and server give us translation of the block
        $.ajax({
            url: '/translations/get_translations',

            type: 'GET',
            data: {'block': blockId},


            success: function(results, status){
                if (results.success ==true){
                    // we change the value to cancel changes
                    $('#translated_block_' + blockId).val(results.translation)
                }
            },

            error: function(results, status, error){
                console.log('erreur requête AJAX')
            }
        })
    })
})