function init_ajax_form($form) {
    $form.submit(function (e) {
        e.preventDefault();

        $form = $(this);
        let url = this.action;
        let data = $(this).serialize();

        $.post(url, data, function (data) {
            $form.find('.warn').removeClass('warn');
            if (!data.result) {
                const keys = Object.keys(data.errors);
                for (let i in keys) {
                    $form.find('#id_' + keys[i]).parent().addClass('warn');
                    $form.removeClass('success');
                }
            } else {
                if (data.form_url) window.location.replace(data.form_url);
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

$(document).ready(function () {
    $('form').each(function () {
        $(this).find('input').prop('required', false);
        $(this).find('textarea').prop('required', false);
    });

    init_ajax_form($('.sign-up-form'))
});