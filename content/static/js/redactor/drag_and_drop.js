// $(document).ready(function () {
//     $('.drag_elem').draggable({
//         start: function () {
//             console.log(1)
//         },
//         stop: function () {
//             console.log(2)
//         }
//     })
// })
function close_sidebar_mobile_across_trigger() {
    $(".js-sidebar__close-btn").trigger('click');
}

function open_sidebar_mobile_across_trigger() {
    $(".top-menu button[aria-controls='sidebar']").trigger('click');
}


let counter = 0;

function handleDragStart(e) {
    const element_id = $(e.target).data('element-id')
    e.dataTransfer.setData('element_id', $(e.target).data('element-id'))
    console.log('handleDragStart', element_id)
    close_sidebar_mobile_across_trigger()

}

function handleDragEnter(e) {
    e.preventDefault(); // needed for IE
    counter++;
    $(this).closest('.view-container__wrap').addClass('drag_border');
}

function handleDragLeave(e) {
    counter--;
    if (counter === 0) {
        $(this).closest('.view-container__wrap').removeClass('drag_border');
    }
}

function handleDrop(e) {
    if ($(e.currentTarget).hasClass('canvas-wrap')) {
        const element_id = e.dataTransfer.getData('element_id')
        const csrf_token = $("input[name=csrfmiddlewaretoken]").val();

        let data = {
            element_id: element_id,
            csrfmiddlewaretoken: csrf_token,
        }

        $.post(`/element/get`, data, (response) => {

            if (response.result) {
                let width = (parseInt($('.main-svg').css('width')) / 2) + 'px';
                let height = (parseInt($('.main-svg').css('height')) / 2) + 'px';
                let new_elem = document.createElement("div");
                new_elem.setAttribute('style', `padding: 20px; position: absolute; left: ${width}; top: ${height}; cursor: move; overflow: hidden;`)
                new_elem.classList.add('element_container')
                $(new_elem).css('cursor', 'move');
                $(new_elem).append($(response.layout))

                $(new_elem).on('click', (event) => {
                    editableHandler(event);
                });

                $('.main-svg div').eq(1).prepend(new_elem);
            }

        }, 'json')
    }
}

function handleDragEnd(e) {
    $('.view-container__wrap').removeClass('drag_border');
}

let elem = document.querySelector('.drag_elem')
let destination = document.querySelector('.canvas-wrap')


addDynamicEventListener(document.body, 'dragstart', '.drag_elem', handleDragStart);
addDynamicEventListener(document.body, 'touchstart', '.drag_elem', handleDragStart);


destination.addEventListener('dragenter', handleDragEnter, false);

destination.addEventListener('dragleave', handleDragLeave, false);

destination.addEventListener('drop', handleDrop, false);

addDynamicEventListener(document.body, 'dragend', '.drag_elem', handleDragEnd);

// canvas-wrap

document.addEventListener("dragover", function (event) {
    event.preventDefault();
});

