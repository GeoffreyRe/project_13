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


    // we will send modifications when saving
    $('#btn-save').click(function(){
        // we will collect data
        let datas = {
            'project': {

            },
            'users':{

            }
        }

        // TO MODIFY DOESNT WORK CORRECTLY
        let project_id = $('.block-details-project')[0].id.split('_')[2]
        let new_name = $('#project_'+project_id+'_name').children()[1].value
        let new_description = $('#project_'+project_id+'_description').children()[0].value
        if (new_name.length === 0)
        {
            console.log('Le nom du projet ne peut pas être vide !')
            return false
        }

        datas['project'][project_id] = {
            'name': new_name,
            'description': new_description
        }

        let user_infos = $('.user_infos')

        for (let i=0; i < user_infos.length; i++){
            let user_id = user_infos[i].children[0].id.split('_')[3]
            let new_role_id = user_infos[i].children[0].children[1].value
            if (new_role_id === ''){
                console.log('Un role ne peut pas être vide')
                return false
            }
            datas['users'][user_id] = new_role_id
        } 
        console.log(datas)

        $.ajax({
            url : '/project/' + project_id + '/modify_project',
            type :"post",
            data : {
                'datas' : datas
            },
            success : function(response){
                console.log(response);
                if (response.success == true)
                {
                   console.log('success') 
                }
                else if (response.success == false)
                {
                    console.log('erreur')
                }
            },
            error : function(response){
                console.log("error requête ajax")
            },
        })
    })
    

}) //fin fonction ready