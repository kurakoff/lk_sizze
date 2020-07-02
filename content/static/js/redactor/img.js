// ВСТАВКА TEMPLATE В КОНТЕЙНЕР MAIN SVG
const appendTemplate = (html) => {
    $('.main-svg').empty();
    $('.main-svg').append(html);
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

    $('[data-set="true"]').on('click', (event) => {
        let clickCounter = +$(event.target).attr('clickCounter');
        if (clickCounter == 1) return;

        editableHandler(event);
    });
    $('[data-set="true"]').on('click', getToolsPanel);
    $('.draggable').css('cursor', 'move');

    $('[data-type="text"]').css('line-height', 'normal');
    $('[data-type="text"]').attr('clickCounter', 0);

    $('[data-type="text"]').on('click', (event) => {
        let clickCounter = +$(event.target).attr('clickCounter');
        if (clickCounter === 1) {
            draggable.draggable = false;
            draggable.snappable = false;
            $(event.target).css('cursor', 'text');
        } else {
            clickCounter++;
            $(event.target).attr('clickCounter', clickCounter);
        }
    });

    $('[data-type="text"]').blur((event) => {
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

//Класс управления CRUD шаблонов INDEXDB
_db = new SaverProgress(appendTemplate);
//

const main = () => {

};

main();
