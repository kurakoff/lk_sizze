$(document).ready(function () {
    // init
    let id = $('.prototype.active').data('prototype-id')
    $('option').each(function () {
        $(this).removeAttr('selected')
    })
    $('select').val(id)
    //

    $('.prototype').click(function () {
        $('.prototype').each(function () {
            $(this).removeClass('active')
        })
        $(this).addClass('active')
        $('option').each(function () {
            $(this).removeAttr('selected')
        })
        let id = $(this).data('prototype-id')
        $('select').val(id)
    })
    $('.create_next').click(function () {
        $('.step_1').hide()
        $('.step_2').show()
    })
})