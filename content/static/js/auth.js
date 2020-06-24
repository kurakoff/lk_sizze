function init_ajax_form($form) {
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
                clear_form($form);
            }
        }, 'json');
    });
}

function clear_form($form) {
    $form.find('input[type=text], textarea').each(function () {
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
    init_ajax_form($('.change-password-form'))
    // CHANGE account profile
    init_ajax_form($('.login-account-profile'))
    //
});