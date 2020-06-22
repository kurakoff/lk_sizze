function init_ajax_form($form) {
    console.log($form)
    $form.submit(function (e) {
        e.preventDefault();
        // e.stopPropagation();
        $form = $(this);
        var url = this.action;
        data = $(this).serialize();

        $.post(url, data, function (data) {

            $form.find('.warn').removeClass('warn');
            if (!data.result) {
                keys = Object.keys(data.errors);
                for (let i in keys) {
                    $form.find('#id_' + keys[i]).parent().addClass('warn');
                    $form.removeClass('success');
                }
            } else {
                if (data.form_url) {
                    window.location.replace(data.form_url);
                }
                clear_form($form);
                $('.open-popup-link').click();
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