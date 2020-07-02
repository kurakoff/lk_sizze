function reload_js(src) {
    $('script[src="' + src + '"]').remove();
    $('<script>').attr('src', src).appendTo('head');
}

function create_screens_success($form, data) {
    $('.close_create_screen').trigger('click')
    $(data['html_screen']).appendTo('.screens_container')
    reload_js('/static/js/menu_project.js');
    reload_js('/static/js/modal.js');
}

function blinking_success($form) {
    let blink_success = $form.find('.blinking_success');
    blink_success.css('display', 'block');
    setTimeout(() => {
        blink_success.css('display', 'none')
    }, 3000)
}

function delete_project_success() {
    let id = $('#delete_project_form').find('input#id_project').attr('value')
    $(`.project_${id}`).remove()
    $('#dialog_delete_project .js-dialog__close').trigger('click')
}


function delete_screen_success($form, data) {
    let id = data.id
    $(`.screen_${id}`).remove()
    $('#dialog_delete_screen .js-dialog__close').trigger('click')
}

function copy_project_success($form, data) {
    let id = $('#delete_project_form').find('input#id_project').attr('value')
    $(data['html_project']).appendTo('.projects_container')
    $('#dialog_copy_project .js-dialog__close').trigger('click')
    reload_js('/static/js/menu_project.js');
    reload_js('/static/js/modal.js');
}

function rename_project_success($form, data) {
    let id = data['id']
    let name = data['new_name']
    $(`.project_${id}`).find('h4').text(name)
    $('.close_modal_rename').trigger('click')
}

function init_ajax_form($form, clean = true, after_save) {
    $form.submit(function (e) {
        e.preventDefault();
        form_clear_error($form)
        $form = $(this);
        let url = this.action;
        let data = $(this).serialize();

        $.post(url, data, function (data) {
            $form.find('.warn').removeClass('warn');
            if (!data.result) {
                const keys = Object.keys(data.errors);
                for (let i in keys) {
                    $form.find('#id_' + keys[i]).siblings('.error_style').addClass('show').text(data.errors[keys[i]])
                }
            } else {
                if (data.redirect_url) window.location.replace(data.redirect_url);
                if (clean) clear_form($form);
                if (after_save) after_save($form, data)
            }
        }, 'json');
    });
}

function clear_form($form) {
    $form.find('input, textarea').each(function () {
        $(this).val('');
    });
}

function form_clear_error($form) {
    $form.find('.error_style').removeClass('show')
}

$(document).ready(function () {
    $('form').each(function () {
        $(this).find('input').prop('required', false);
        $(this).find('textarea').prop('required', false);
    });
    //CREATE USER
    init_ajax_form($('.sign-up-form'))
    // LOGIN USER
    init_ajax_form($('.login-form'))
    // Change password details account
    init_ajax_form($('.change-password-form'), true, blinking_success)
    // CHANGE account profile
    init_ajax_form($('.login-account-profile'), false, blinking_success)
    //
    init_ajax_form($('.form_create_project'), true, blinking_success)
    //
    init_ajax_form($('#delete_project_form'), false, delete_project_success)
    //DELETE
    $(document).on('click', '.preparation_delete_project', function (e) {
        e.preventDefault()
        let $form = $('#delete_project_form');
        $form.find('#id_project').val($(this).data('id'))
    })

    $('.submit_delete_project').click(function () {
        $('#delete_project_form').submit()
    })
    //
    init_ajax_form($('#copy_project_form'), false, copy_project_success)
    $(document).on('click', '.preparation_copy_project', function (e) {
        e.preventDefault()
        let $form = $('#copy_project_form');
        $form.find('#id_project').val($(this).data('id'))
    })

    $('.submit_copy_project').click(function () {
        $('#copy_project_form').submit()
    })
    // EDIT
    init_ajax_form($('#rename_project_form'), false, rename_project_success)
    $(document).on('click', '.preparation_edit_project', function (e) {
        e.preventDefault()
        let $form = $('#rename_project_form');
        $form.find('#id_id').val($(this).data('id'))
    })

    //    SCREENS
    init_ajax_form($('.form_create_screen'), true, create_screens_success)

    $(document).on('click', '.preparation_delete_screen', function (e) {
        e.preventDefault()
        let $form = $('#delete_screen_form');
        $form.find('#id_screen').val($(this).data('id'))
    })

    init_ajax_form($('#delete_screen_form'), true, delete_screen_success)
    $('.submit_delete_screen').click(() => $('#delete_screen_form').submit())

    init_ajax_form($('#rename_screen_form'), true, create_screens_success)
    init_ajax_form($('#copy_screen_form'), true, create_screens_success)
})