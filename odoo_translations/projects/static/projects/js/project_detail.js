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

    // function that will checks user input before send with ajax
    let timeOutId = undefined
    let transitionTimeOutId = undefined


    function displayErrorPopup(errorMsg){
        if (timeOutId != undefined){
            clearTimeout(timeOutId)
        }
        if (transitionTimeOutId != undefined){
            clearTimeout(transitionTimeOutId)
        }
        $('#error-message-popup').css({
            transition:'opacity 0s',
            opacity:1
        })
        transitionTimeOutId = setTimeout(function(){
            $('#error-message-popup').css({
                transition:'opacity 1s',
                opacity:0
            })
        }, 3000)
        $('#error-message').empty()
        $('#error-message').append(errorMsg)
        $('#error-message-popup').removeClass('d-none')
        timeOutId = setTimeout(function(){
            $('#error-message-popup').addClass('d-none')
        }, 4000)

    }


    function checkBeforeSend(){
        let errorMsg = ""
        // check of project name
        let projectNameVal = $('#id_name').val()
        if (projectNameVal == ''){
            errorMsg = 'Le nom de projet ne peut pas être vide'
            $('#id_name').css('border', 'solid 1px rgb(255,33,25)')

            displayErrorPopup(errorMsg)

            throw errorMsg
            
        }

        // check of users
        let users = $('.user_infos:not(.d-none)')
        if (users.length == 0){
            errorMsg = "Aucun utilisateur n'est présent sur le projet"
            displayErrorPopup(errorMsg)

            throw errorMsg
        }
        for (let i=0; i < users.length; i++){
            if ($(users[i]).find('select').val() == ""){
                let errorMsg = "Le rôle de l'utilisateur ne peut pas être vide"
                $(users[i]).find('select').css('border', 'solid 1px rgb(255,33,25)')
                displayErrorPopup(errorMsg)

                throw errorMsg
            }
            if ($(users[i]).find('.new_user').length == 1){
                if ($(users[i]).find('.new_user').val() == ""){
                    errorMsg = "L'email de l'utilisateur ne peut pas être nul !"
                    $(users[i]).find('.new_user').css('border', 'solid 1px rgb(255,33,25)')
                    displayErrorPopup(errorMsg)
                    throw errorMsg
                    
                }
            }
        }

        // check of templates
        let files = $('.block-files-project .file_infos')
        
        for (let i=0; i < files.length; i++){
            let file = files[i]
            if (file.dataset.fileId =="new"){
                let errorMsg = "Il n'y a aucun fichier de traduction"
                let inputFile = $(file).find("input[type=file]")
                if ($(inputFile).prop('files').length == 0){
                    $(inputFile).css('color', 'rgb(255,33,25)')
                    displayErrorPopup(errorMsg)

                    throw errorMsg
                }
                if (($(file).find('#id_translated_language').val() == "") && ($(file).find('#id_is_template').prop('checked') == false)){

                    $(file).find('#id_translated_language').css('border', 'solid 1px rgb(255,33,25)')
                    errorMsg = "Un fichier de traduction doit avoir un langue !"
                    displayErrorPopup(errorMsg)
                    $(file).find('#id_translated_language').focus(function(){
                        $(this).css('border', '')
                    })
                    throw errorMsg

                }
            }
        }

        let configFiles = $('.block-files-config-project .file_infos:not(#form-config-file)')
        errorMsg = "Il n'y a aucun fichier de traduction"
        for (let i=0; i < configFiles.length; i++){
            let configFile = configFiles[i]
            if (configFile.dataset.fileId == 'new'){
                let inputFile = $(configFile).find('input[type=file]')
                if ($(inputFile).prop('files').length == 0){
                    $(inputFile).css('color', 'rgb(255,33,25)')
                    displayErrorPopup(errorMsg)

                    throw errorMsg
                }
            }
        }
    }

    $('#id_name').focus(function(){
        $(this).css('border', '')
    })

    $('.user_infos:not(.d-none) select').focus(function(){
        $(this).css('border', '')
    })

    $('.user_infos:not(.d-none) .new_user').focus(function(){
        $(this).css('border', '')
    })

    $('input[type=file]').focus(function(){
        $(this).css('color', '')
    })



    let usersToDelete = []
    $('.btn-delete-user').click(function(){
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
        $(copyNewUser).find('.btn-delete-user')[0].dataset.newUserId = numberNewUser
        $($(copyNewUser).find('.btn-delete-user')[0]).click(function(){
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

        $('.user_infos:not(.d-none) select').focus(function(){
            $(this).css('border', '')
        })
    
        $('.user_infos:not(.d-none) .new_user').focus(function(){
            $(this).css('border', '')
        })

        
    })



    // we will add a event to add and remove translations file
    $(".btn-append-file").click(function(){
        let newFormFile = $('#form_file_template').clone()[0]
        $(newFormFile).removeClass('d-none')
        newFormFile.dataset.fileId = "new"
        $(newFormFile).removeAttr('id')
        $('.block-files-project').append(newFormFile)
        $('.btn-delete-file').off('click')
        $('.btn-delete-file').click(function(){
            if (this.dataset.fileId !== 'new'){
                filesToDelete.push(this.dataset.fileId)
            }
            $(this).closest('.file_infos').remove()
            console.log(filesToDelete)
        })
        $('input[type=file]').focus(function(){
            $(this).css('color', '')
        })

    })

    $(".btn-append-config-file").click(function(){
        if ($(".block-files-config-project .file_infos:not(#form-config-file)").length < 1){
            let newConfig = $('#form-config-file').clone()[0]
            $(newConfig).removeClass('d-none')
            newConfig.id = null
            $('.block-files-config-project').append(newConfig)
            $('.btn-delete-config-file').click(function(){
                if (this.dataset.fileId !== 'new'){
                    configFilesToDelete.push(this.dataset.fileId)
                }
                $(this).closest('.file_infos').remove()
                console.log(configFilesToDelete)
            })
        }
    })

    let filesToDelete = []
    $('.btn-delete-file').click(function(){
        if (this.dataset.fileId !== 'new'){
            filesToDelete.push(this.dataset.fileId)
        }
        $(this).closest('.file_infos').remove()
        console.log(filesToDelete)
    })

    let configFilesToDelete = []
    $('.btn-delete-config-file').click(function(){
        if (this.dataset.fileId !== 'new'){
            configFilesToDelete.push(this.dataset.fileId)
        }
        $(this).closest('.file_infos').remove()
        console.log(configFilesToDelete)
    })



    // we will send modifications when saving
    $('#btn-save').click(function(){
        checkBeforeSend()
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

        // now we will check if there is new files to add 

        let newFiles = $(".block-files-project .file_infos[data-file-id='new']")
        let formDataFiles = new FormData()
        let totalFiles = 0
        for (let k=0;k < newFiles.length; k++) {
            totalFiles += 1
            let formDataFile = new FormData()
            let newFile = newFiles[k]
            let fileData = $(newFile).find("input[type='file']").prop('files')[0]
            let fileLanguage = $(newFile).find("select[name='translated_language']").val()
            let isTemplate = $(newFile).find("#id_is_template").prop("checked")
            console.log(fileData, fileLanguage, isTemplate)
            formDataFiles.append('file_' + k, fileData)
            formDataFiles.append('lang_' + k, fileLanguage)
            formDataFiles.append('template_' + k, isTemplate)


        }

        // now, we check for config files
        let newConfigFiles = $('.block-files-config-project .file_infos[data-file-id="new"]:not(#form-config-file)')

        for (let k=0;k < newConfigFiles.length; k++) {
            let newConfigFile = newConfigFiles[k]
            let configData = $(newConfigFile).find("input[type='file']").prop('files')[0]
            formDataFiles.append('config_file', configData)
            console.log('test')
        }

        formDataFiles.append('config_files_to_delete', JSON.stringify(configFilesToDelete))
        formDataFiles.append('files_to_delete', JSON.stringify(filesToDelete))
        formDataFiles.append('files_total', totalFiles)
        // now we will add relations between user and project to delete if there is any
        infosToSend['users_to_delete'] = usersToDelete
        
        // now we will add files to append and files to delete 
        formDataFiles.append('infos_user',JSON.stringify(infosToSend))
        console.log(infosToSend)

        // we will send infosToSend to an url with post values
        console.log(formDataFiles.get('config_files_to_delete'))
        $.ajax({
            url: '/project/'+ infosToSend['project']['id'] + '/modify_project',

            type: 'POST',
            processData: false,
            contentType: false,
            data: formDataFiles,// {'datas': JSON.stringify(infosToSend)},


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

    // this part adds event wich opens the sub menu
    $('#sub-menu-tab').click(function(){
        let time = 400;
        $('#sub-menu-translations').addClass('sub-menu-full-display')
        $('#sub-menu-translations').animate({width: "100%", opacity:"1"}, time)
        $('.sub-menu-text').css('opacity', '0')
        setTimeout(function(){
            $('.sub-menu-text').css('opacity', '1')
        }, Math.trunc(time/1.5))
    })

    // this part adds event wich removes the sub menu
    $('#close-sub-menu-tab').click(function(){
        let time = 400;
        $('#sub-menu-translations').animate({width: "1%", opacity:'0.1'}, time)
        $('.sub-menu-text').css('opacity', '0')
        setTimeout(function(){
        $('#sub-menu-translations').removeClass('sub-menu-full-display')
        }, time
    )})

    $('#launch_analysis').click(function(){
        console.log(window.location.href.replace('/details', ''))
        $.ajax({
            url: window.location.href.replace('/details', '') + '/launch_analysis',

            type: 'get',
            
            success: function(results, status){
                if (results.success ==true){
                    console.log('success')
                }
            },

            error: function(results, status, error){
                console.log('erreur requête AJAX')
            }
        })

    })
    

}) //fin fonction ready