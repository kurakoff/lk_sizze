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
    $('#dialog_delete_project').hide()
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
                if (after_save) after_save($form)
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
    $('.preparation_delete_project').click(function (e) {
        e.preventDefault()
        let $form = $('#delete_project_form');
        $form.find('#id_project').val($(this).data('id'))
    })
    $('.submit_delete_project').click(function () {
        $('#delete_project_form').submit()
    })
});