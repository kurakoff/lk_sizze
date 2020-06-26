$(document).ready(function () {
    $('.filter-nav__item').click(function () {
        $('.nav_block').each(function () {
            $(this).hide()
        })
        let nav = $(this).data('nav')
        $(`.nav_block[data-nav="${nav}"]`).show()
    })
})