$(document).ready(function(){
    console.log('code après')
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

    let usersToDelete = []
    $('.fa-minus-circle').click(function(){
        let userId = this.dataset.userDeleted
        if (userId == 'new')
        {
            let newUserId = this.dataset.newUserId
            console.log(newUserId)
            let DivToRemove = $(".user_infos[data-user-id='new_" + newUserId + "']")
            console.log(DivToRemove)
            DivToRemove.removeClass('d-flex')
            DivToRemove.removeClass('user_infos')
            DivToRemove.remove()

        }
        else{
            usersToDelete.push(userId)
            let DivToRemove = $(".user_infos[data-user-id='" + userId + "']")
            DivToRemove.removeClass('d-flex')
            DivToRemove.removeClass('user_infos')
            DivToRemove.remove()
            console.log(usersToDelete)
        }
        
    })



    let numberNewUser = 0
    $('.btn-append').click(function(){
        // ajouter du code permettant d'ajouter de nouveaux utilisateurs
        let newUserInfosElt = $(".user_infos.d-none")[0]
        let copyNewUser = $(newUserInfosElt).clone()[0]
        
        numberNewUser = numberNewUser + 1

        console.log(copyNewUser)
        copyNewUser.dataset.userId = "new_" + numberNewUser
        $(copyNewUser).find('.fa-minus-circle')[0].dataset.newUserId = numberNewUser
        $($(copyNewUser).find('.fa-minus-circle')[0]).click(function(){
            let userId = this.dataset.userDeleted
            if (userId == 'new')
            {
                let newUserId = this.dataset.newUserId
                console.log(newUserId)
                let DivToRemove = $(".user_infos[data-user-id='new_" + newUserId + "']")
                console.log(DivToRemove)
                DivToRemove.removeClass('d-flex')
                DivToRemove.removeClass('user_infos')
                DivToRemove.remove()
    
            }
            else{
                usersToDelete.push(userId)
                let DivToRemove = $(".user_infos[data-user-id='" + userId + "']")
                DivToRemove.removeClass('d-flex')
                DivToRemove.removeClass('user_infos')
                DivToRemove.remove()
                console.log(usersToDelete)
            }
        })
        $(newUserInfosElt).removeClass('d-none')
        console.log(copyNewUser)
        $('.block-users-project').append(copyNewUser)

        
    })



    // we will add a event to add and remove translations file
    $(".btn-append-file").click(function(){
        let newFormFile = $('#form_file_template').clone()[0]
        $(newFormFile).removeClass('d-none')
        newFormFile.dataset.fileId = "new"
        $(newFormFile).removeAttr('id')
        $('.block-files-project').append(newFormFile)
        $('.fa-trash-alt').off('click')
        $('.fa-trash-alt').click(function(){
            if (this.dataset.fileId !== 'new'){
                filesToDelete.push(this.dataset.fileId)
            }
            $(this).closest('.file_infos').remove()
            console.log(filesToDelete)
        })

    })

    let filesToDelete = []
    $('.fa-trash-alt').click(function(){
        if (this.dataset.fileId !== 'new'){
            filesToDelete.push(this.dataset.fileId)
        }
        $(this).closest('.file_infos').remove()
        console.log(filesToDelete)
    })



    // we will send modifications when saving
    $('#btn-save').click(function(){
        infosToSend = {}
        // ajouter du code permettant d'envoyer des données par rapport au projet, utilisateurs et nouveaux utilisateurs
        let projectDiv = $('#project_detail_content')[0] // we retrieve element that contains project id
        let projectId = projectDiv.dataset.projectId // we get project id
        let projectName = $('#id_name').val() // we get new project name
        let projectDescription = $('#id_description').val() // we get new project description
        infosToSend['project'] = {
            'id': projectId,
            'name': projectName,
            'description': projectDescription
        }

        // now we will retrieve users modifications
        
        let userInfosElts = $('.user_infos')
        infosToSend['users'] = []

        for (let i = 0; i < userInfosElts.length; i++){
            

            let userId = userInfosElts[i].dataset.userId
            if (userId.includes('new') == true)
            {
                if ($(userInfosElts[i]).hasClass('d-none') == false) {
                    let email = $(userInfosElts[i]).find('.new_user').val()
                    let role = $(userInfosElts[i]).find('#id_name').val()
                    let user = {
                        'id' : 'new',
                        'email' : email,
                        'role': role
                    }
                    infosToSend['users'].push(user)
                }
            }
            else{
                let userRole = $('#role_user_' + userId).children()[0]
                let roleId = $(userRole).val()
                
                let user = {
                    'id': userId,
                    'role': roleId
                }
                infosToSend['users'].push(user)
            }
        }

        // now we will add relations between user and project to delete if there is any
        infosToSend['users_to_delete'] = usersToDelete
        
        // now we will add files to append and files to delete 
        console.log(infosToSend)

        // we will send infosToSend to an url with post values
        $.ajax({
            url: '/project/'+ infosToSend['project']['id'] + '/modify_project',

            type: 'POST',

            data: {'datas': JSON.stringify(infosToSend)},

            success: function(results, status){
                if (results.success ==true){
                    window.location.replace("/project/" + projectId +"/details");
                }
            },

            error: function(results, status, error){
                console.log('erreur requête AJAX')
            }
        })
        
        
    })
    

}) //fin fonction ready