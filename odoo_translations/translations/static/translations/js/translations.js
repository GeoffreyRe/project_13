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


    // this part is taking translations changes and send it in ajax to the server to change some blocks
    $("#btn-save-translations").click(function(){
        let textAreaElts = $(".translated_block");
        let data = [];

        for (let i=0; i < textAreaElts.length;i++){
            let blockData = {}
            blockData['id'] = textAreaElts[i].dataset.blockId
            blockData['translated_text'] = $(textAreaElts[i]).val()
            data.push(blockData)
        }

        let formDataBlock = new FormData()

        formDataBlock.append("data", JSON.stringify(data))

        $.ajax({
            url : '/translations/save_translations_changes/',
            type :"post",
            processData: false,
            contentType: false,
            data : formDataBlock,
            success : function(response){
                console.log(response);
                if (response.success == true)
                {
                    console.log('success')
                    location.reload(true)
                }
            },
            error : function(response){
                console.log("error requête ajax")
            },
        })
    })
})