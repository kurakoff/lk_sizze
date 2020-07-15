// ВСТАВКА TEMPLATE В КОНТЕЙНЕР MAIN SVG
function open_sidebar_mobile_across_trigger() {
    $(".top-menu button[aria-controls='sidebar']").trigger('click');
}

function close_sidebar_mobile_across_trigger() {
    $(".js-sidebar__close-btn").trigger('click');
}

const fonts_origin = 'http://sizze.io'

$(document).ready(function () {
    // Модалка для back to original, yes_or_no

    $('.show_yes_or_no').click(function () {
        $('._fade_yes_or_no').css('display', 'block');
        $('.dropdown-menu-keep').removeClass('keep-menu');

    });

    $('.yes_or_no_button_no').click(function () {
        $('._fade_yes_or_no').css('display', 'none');
        $('.dropdown-menu-keep').removeClass('keep-menu');

    });

    $('.yes_or_no_button_yes').click(function () {
        $('._fade_yes_or_no').css('display', 'none');
    });


    const appendTemplate = (html, screen_id) => {
        $('.main-svg').empty();
        $('.main-svg').append(html);
        $('.main-svg').data('screen_id', screen_id)

        if (draggable) draggable.target = ""

        let imgWidth = parseInt($('.main-svg').css('width'));
        let canvasWidth = parseInt($('.container .h-100').css('width'));
        let bottomMenuHeight = parseInt($('.menu-bottom').css('height'));

        if (imgWidth < canvasWidth) {
            let scale = Math.round(canvasWidth * 90 / imgWidth);
            $('.scale').val(scale);
            $('.main-svg').css('transform', `scale(${scale / 100})`);
        } else {
            $('.scale').val(50);
            $('.main-svg').css('transform', `scale(0.5)`);
        }

        $(document).on('click', '[data-set="true"]', function (event) {
            // console.log('on [data-set="true"]', $(event.target))
            let clickCounter = +$(event.target).attr('clickCounter');
            if (clickCounter == 1) return;
            editableHandler(event);
        })

        $(document).on('click', '[data-set="true"]', getToolsPanel)


        $('.draggable').css('cursor', 'move');

        $('[data-type="text"]').css('line-height', 'normal');
        $('[data-type="text"]').attr('clickCounter', 0);

        $(document).on('click', '[data-type="text"]', function (event) {
            // console.log('on click [data-type="text"]', $(event.target))

            let clickCounter = +$(event.target).attr('clickCounter');
            if (clickCounter === 1) {
                draggable.draggable = false;
                draggable.snappable = false;
                $(event.target).css('cursor', 'text');
            } else {
                clickCounter++;
                $(event.target).attr('clickCounter', clickCounter);
            }
        })


        $('[data-type="text"]').blur((event) => {
            console.log('on click blur  [data-type="text"]', $(event.target))

            let clickCounter = +$(event.target).attr('clickCounter');

            if (clickCounter == 1) {
                draggable.draggable = true;
                draggable.snappable = true;
                $(event.target).css('cursor', 'move');
                $(event.target).attr('clickCounter', 0);
            }
        });

        $('.main-svg').contextmenu((event) => {
            $('.contextmenu').css('display', 'inline-block');
            $('.contextmenu').css('left', event.pageX);
            $('.contextmenu').css('top', event.pageY);
            return false;
        });

        $(window).click((event) => {
            $('.contextmenu').hide();
        });

        const mainSVG = document.querySelector('.main-svg');
        const sizer = $('.main-svg > div');

        $(mainSVG).css({
            width: sizer.css('width'),
            height: sizer.css('height')
        });

        const newWidth = mainSVG.getBoundingClientRect().width;
        const newHeight = mainSVG.getBoundingClientRect().height;


        $('.canvas-wrap').css({
            width: `${newWidth}px`,
            height: `${newHeight}px`,
        })
    };

    saver_user_progress = new SaverUserProgressScreen(appendTemplate);
    $(document).on('click', 'a[aria-controls="modal-select1"]', function (e) {
        $('.data_data').data('changed_screen_id', $(e.target).closest('a.menu__content').data('screen-id'))
    })
    slider_preview = new SliderPreview()
    saver_user_progress.runAutoSave()

    $('.fonts-style').click((event) => {
        $(".top-menu button[aria-controls='sidebar']").trigger('click');

        if ($('.font-style-section:visible').get(0) && $('aside.sidebar').attr('role') !== 'alertdialog') {
            $('.font-style-section').hide();
            return;
        }

        $('.font-section').hide();
        $('.category-section').show();
        $('.html-list-section').hide();
        $('.fonts-style-list').empty();
        $('.font-style-section').show();

        $.ajax({
            type: 'GET',
            url: 'http://sizze.io/img/font-face',
            data: {
                font: $('.current-font').html()
            },
            success: (html) => {
                html.faces.filter(face => {
                    $('.fonts-style-list').append(`
                    <button data-src="${face.src}" type="button" 
                    class="list-group-item list-group-item-action"
                    style="font-family: ${html.title}; font-style: ${face.title}"
                    >${face.title}</button>
                    
                    `);
                    $('.all_fonts').append(
                        `
                            <style>
                                @font-face {
                                    font-family: ${html.title};
                                    src: url('${fonts_origin}/${face.src}') format('truetype');
                                    font-style: ${face.title};
                                }
                            </style>
                         `)
                })

                $('.fonts-style-list').click((event) => {
                    if (event.target.tagName != 'BUTTON') return;

                    close_sidebar_mobile_across_trigger()

                    let pathToFont = $(event.target).attr('data-src');
                    let face = $(event.target).html();
                    let title = $('.current-font').html() + '-' + face;

                    $('.main-svg').children().first().prepend(`
                        <style class="fonts-style">
                            @font-face {
                                font-family: ${title};
                                src: url('${fonts_origin}/${pathToFont}') format('truetype');
                                font-style: ${face};
                                font-weight: 400;
                            }
                            @font-face {
                                font-family: ${title};
                                src: url('${fonts_origin}/${pathToFont}') format('truetype');
                                font-style: ${face};
                                font-weight: 700;
                            }
                        </style>
                    `);

                    $('.current-font-style').html(face);
                    $(CURRENT_EDIT_ELEMENT).css('font-family', title);
                    $(CURRENT_EDIT_ELEMENT).data('font-family', $('.current-font').html());
                    $(CURRENT_EDIT_ELEMENT).data('font-style', face);
                    draggable.updateRect();
                    draggable.updateTarget();
                });
            }
        });

    });
    $('.font-select-button').click(() => {
        $('.fonts-style-list').empty();

        if ($('.font-style-section:visible').get(0) && oldSection == '.html-list-section') {
            $('.font-style-section').hide();
            $('.html-list-section').show();
            return;
        }

        $('.font-style-section').hide();
        $('.font-section').hide();
        $('.category-section').show();
    });

    $('.format-button').click((event) => {
        $('.font-container').addClass('collapse');
        $('.font-container').removeClass('show');
    });

    $('.fonts').click((event) => {
        open_sidebar_mobile_across_trigger()

        if ($('.category-section:visible').get(0)) {
            oldSection = '.category-section';
        }
        if ($('.html-list-section:visible').get(0)) {
            oldSection = '.html-list-section';
        }

        if ($('.font-section:visible').get(0) && $('aside.sidebar').attr('role') !== 'alertdialog') {
            $('.font-section').hide();
            $(oldSection).show();
            return;
        } else {
        }

        $('.category-section').hide();
        $('.html-list-section').hide();
        $('.font-style-section').hide();
        $('.font-section').show();

        $.ajax({
            type: 'GET',
            url: 'http://sizze.io/img/font',
            data: {
                pivot: 0
            },
            success: (html) => {
                html.filter((font) => {
                    let font_src = `${font.src}`
                    $('.fonts-list').append(
                        `<button data-src="${font_src}" data-weight="regular" 
                                 type="button" class="list-group-item list-group-item-action"
                                 style="font-family: ${font.title}">
                                    ${font.title}
                          </button>`);
                    $('.all_fonts').append(
                        `
                            <style>
                                @font-face {
                                    font-family: ${font.title};
                                    src: url('${fonts_origin}/${font_src}') format('truetype');
                                }
                            </style>
                            `
                    )
                })
                // font.faces[0].title
                $('.fonts-list').click((event) => {

                    close_sidebar_mobile_across_trigger()

                    if (event.target.tagName != 'BUTTON') return;


                    let pathToFont = $(event.target).attr('data-src');
                    let title = $(event.target).html();
                    let font_weight = event.target.dataset.weight

                    if ($('.main-svg').find(`.fonts-style-${title}`).length === 0) {
                        $('.main-svg').children().first().prepend(`
                        <style class="fonts-style fonts-style-${title}">
                            @font-face {
                                font-family: ${title};
                                src: url('${fonts_origin}/${pathToFont}') format('truetype');
                                font-weight: ${font_weight};
                            }
                        </style>
                    `);
                    }

                    $(CURRENT_EDIT_ELEMENT).css('font-family', title);
                    $(CURRENT_EDIT_ELEMENT).css('font-weight', "");
                    $(CURRENT_EDIT_ELEMENT).data('font-family', title);
                    updateCurrentFont();
                    draggable.updateRect();
                    draggable.updateTarget();
                });
            }
        });

    });

    $('.format-button').click((event) => {
        $('.font-container').addClass('collapse');
        $('.font-container').removeClass('show');
    });

})

