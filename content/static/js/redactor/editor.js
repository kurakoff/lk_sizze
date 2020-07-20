/**
 * Скрипт для редактирования изображения
 */
let draggable;

/**
 * Атрибут редактируемого элемента
 */
const CURRENT_EDIT = 'currentEditable';

/**
 * Атрибут для получения текущего редактируемого элемента
 */
const CURRENT_EDIT_ELEMENT = `[${CURRENT_EDIT}="true"]`;

const EMPTY = '';

const updateCurrentFont = () => {
    $('.current-font').html($(CURRENT_EDIT_ELEMENT).css('font-family').split(',')[0])
};


const updateCurrentFontSize = () => {
    $('.current-font-size').val($(CURRENT_EDIT_ELEMENT).css('font-size').replace('px', ''));
};

const updateCurrentBorderSize = () => {
    $('.current-border-size').val($(CURRENT_EDIT_ELEMENT).find('rect.rect_stroke').attr('stroke-width'));
};

const updateCurrentBorderRadius = () => {
    $('.current-radius-size').val($(CURRENT_EDIT_ELEMENT).find('rect.rect_radius').attr('rx'));
};


const divToBr = () => {
    let content = $(CURRENT_EDIT_ELEMENT).html();

    if (!content) return;

    while (content.match('div')) {
        content = content.replace('<div>', '<br>');
        content = content.replace('</div>', '');
    }
    $(CURRENT_EDIT_ELEMENT).html(content);
}

const textRect = () => {
    $('[data-direction="w"]').hide();
    $('[data-direction="e"]').hide();
    $('[data-direction="s"]').hide();
    $('[data-direction="n"]').hide();
}

const defaultRect = () => {
    $('[data-direction="w"]').show();
    $('[data-direction="e"]').show();
    $('[data-direction="s"]').show();
    $('[data-direction="n"]').show();
}

const backgroundRect = () => {
    $('[data-direction="w"]').hide();
    $('[data-direction="e"]').hide();
    $('[data-direction="s"]').hide();
    $('[data-direction="n"]').hide();
    $('[data-direction="nw"]').hide();
    $('[data-direction="ne"]').hide();
    $('[data-direction="sw"]').hide();
    $('[data-direction="se"]').hide();
    $('.moveable-line.moveable-rotation-line').hide();
}

const defaultBackgroundRect = () => {
    $('[data-direction="w"]').show();
    $('[data-direction="e"]').show();
    $('[data-direction="s"]').show();
    $('[data-direction="n"]').show();
    $('[data-direction="nw"]').show();
    $('[data-direction="ne"]').show();
    $('[data-direction="sw"]').show();
    $('[data-direction="se"]').show();
}

/**
 * Обновление панели инструментов
 * @param {object} event
 */
const updateTools = (event) => {
    const attrs = {
        'data-style-italic': '#style',
        'data-style-underline': '#underline',
        'data-style-weight': '#weight'
    };
    let currentEditable = $(CURRENT_EDIT_ELEMENT);

    for (attr in attrs) {
        if (currentEditable.attr(attr)) {
            $(attrs[attr]).addClass('active-style-button');
        } else {
            $(attrs[attr]).removeClass('active-style-button');
        }
    }

    let fontSize = currentEditable.css('font-size').replace('px', '');
    $('.quantity').attr('value', fontSize);
};

const initalTransform = {
    rotate: "0deg",
    scaleX: 1,
    scaleY: 1
};

const frame = new Scene.Frame({
    width: "250px",
    height: "200px",
    left: "0px",
    top: "0px",
    transform: initalTransform
});

function setTransform(target) {
    target.style.transform = frame.toCSS().match(new RegExp(/transform:(.+);/))[1];
    target.style.left = frame.get('left');
    target.style.zIndex = frame.get('z-index');
    target.style.top = frame.get('top');
    target.style.width = frame.get('width');
    target.style.height = frame.get('height');
    //target.style.cssText = frame.toCSS();
}

function setLabel(clientX, clientY, text) {
    let labelElement = $('.label')
    labelElement[0].style.cssText = `display: block; transform: translate(${clientX}px, ${clientY - 10}px) translate(-100%, -100%);`;
    labelElement[0].innerHTML = text;
}

let pickable = true;

function setPickable(bool) {
    setTimeout(() => {
        pickable = bool;
    }, 20);
}

/**
 * События начала редактирования текста
 */
const editableHandler = (event) => {
    event.stopPropagation();
    if (!pickable) return;

    let target = $(event.target);
    let svg = ['path', 'g', 'svg', 'rect', 'polygon'];

    for (let i = 0; i < svg.length; i++) {
        if (target.prop('tagName') == svg[i]) {
            while (target.prop('tagName') != 'svg') {
                target = target.parent();
            }
            continue;
        }
    }

    frame.set('transform', 'rotate', $(target[0]).data('rotate') + 'deg' || 0);

    if (draggable) draggable.destroy();

    draggable = new Moveable($('.canvas-wrap')[0], {
        draggable: true,
        throttleDrag: 0,
        resizable: true,
        throttleResize: 0,
        scalable: true,
        throttleScale: 0,
        keepRatio: false,
        snappable: true,
        snapThreshold: 5,
        snapCenter: true,
        verticalGuidelines: [100, 200, 300],
        horizontalGuidelines: [0, 100, 200],
        elementGuidelines: document.querySelectorAll('[data-set="true"]'),
        rotatable: true,
        throttleRotate: 0,
        rotationPosition: "top",
        scrollable: true,
        scrollContainer: $('.main-svg-container').get(0),
        scrollThreshold: 0,
    })
        .on("pinch", ({clientX, clientY}) => {
            // setTimeout(() => {
            //     setLabel(clientX, clientY, `X: ${frame.get("left")}
            //     <br/>Y: ${frame.get("top")}
            //     <br/>W: ${frame.get("width")}
            //     <br/>H: ${frame.get("height")}
            //     <br/>S: ${frame.get("transform", "scaleX").toFixed(2)}, ${frame.get("transform", "scaleY").toFixed(2)}
            //     <br/>R: ${parseFloat(frame.get("transform", "rotate")).toFixed(1)}deg
            //     `);
            // });
        })
        .on("drag", ({target, left, top, clientX, clientY, isPinch}) => {
            pickable = false;
            frame.set("left", `${left}px`);
            frame.set("top", `${top}px`);

            const deg = $(target).data('rotate') || 0;
            frame.set("transform", "rotate", `${deg}deg`);

            setTransform(target);
            // !isPinch && setLabel(clientX, clientY, `X: ${left}px<br/>Y: ${top}px`);

        })
        .on("scale", ({target, delta, clientX, clientY, isPinch}) => {
            pickable = false;
            const scaleX = frame.get("transform", "scaleX") * delta[0];
            const scaleY = frame.get("transform", "scaleY") * delta[1];
            frame.set("transform", "scaleX", scaleX);
            frame.set("transform", "scaleY", scaleY);
            setTransform(target);
            // !isPinch && setLabel(clientX, clientY, `S: ${scaleX.toFixed(2)}, ${scaleY.toFixed(2)}`);

        })
        .on("rotateStart", ({target, beforeDelta, clientX, clientY, isPinch}) => {
            pickable = false;
            const currentDeg = $(target).data('rotate') || 0;
            frame.set("transform", "rotate", `${currentDeg}deg`);
        })
        .on("rotate", ({target, beforeDelta, clientX, clientY, isPinch}) => {
            pickable = false;
            let deg = parseFloat(frame.get("transform", "rotate")) + beforeDelta;
            deg = Math.round(deg)
            // const rotateDeg = $(target).data('rotate', deg) || 0;
            frame.set("transform", "rotate", `${deg}deg`);
            $(target).data('rotate', deg);

            setTransform(target);
            !isPinch && setLabel(clientX, clientY, `${deg.toFixed(1)}°`);

        })
        .on("resize", ({target, width, height, clientX, clientY, isPinch}) => {
            pickable = false;
            frame.set("width", `${width}px`);
            frame.set("height", `${height}px`);
            setTransform(target);
            // !isPinch &&  setLabel(clientX, clientY, `W: ${width}px<br/>H: ${height}px`);

        }).on("warp", ({target, multiply, delta, clientX, clientY}) => {
            pickable = false;
            frame.set("transform", "matrix3d", multiply(frame.get("transform", "matrix3d"), delta));
            setTransform(target);
            // setLabel(clientX, clientY, `X: ${clientX}px<br/>Y: ${clientY}px`);
        })
        .on("dragEnd", () => {
            setPickable(true);
        }).on("scaleEnd", () => {
            setPickable(true);
        })
        .on("rotateEnd", () => {
            let labelElement = $('.label')
            labelElement[0].style.cssText = `display: none;`
            setPickable(true);
        }).on("resizeEnd", () => {

            setPickable(true);
        })
        .on("warpEnd", () => {
            setPickable(true);
        });

    frame.set('top', target.css('top'));
    frame.set('z-index', target.css('z-index'));
    frame.set('width', target.css('width'));
    frame.set('height', target.css('height'));

    draggable.scrollable = true;

    if ($(CURRENT_EDIT_ELEMENT).attr('data-type') == 'text') {
        divToBr();
    }

    //Убираем атрибут редактирования с прошлого редактируемого элемента
    $(CURRENT_EDIT_ELEMENT).attr(CURRENT_EDIT, 'false');
    //Указываем, что данный элемент редактируется
    target.attr(CURRENT_EDIT, 'true');
    draggable.target = $(CURRENT_EDIT_ELEMENT).get(0);

    updateTools();

    draggable.draggable = true;
    draggable.resizable = true;
    draggable.snappable = true;
    draggable.keepRatio = false;

    if ($(CURRENT_EDIT_ELEMENT).attr('data-type') == 'img') {
        draggable.keepRatio = true;
    }
    
    if ($(CURRENT_EDIT_ELEMENT).attr('data-type') == 'multicolored-element') {
        updateCurrentBorderSize();
        updateCurrentBorderRadius();
    }

    if ($(CURRENT_EDIT_ELEMENT).attr('data-type') == 'text') {
        updateCurrentFont();
        updateCurrentFontSize();
        textRect();
    } else {
        defaultRect();
    }

    if ($(CURRENT_EDIT_ELEMENT).attr('data-type') == 'background-color') {
        draggable.draggable = false;
        draggable.resizable = false;
        backgroundRect();
    }

    $(CURRENT_EDIT_ELEMENT).keyup((event) => {
        draggable.updateRect();
    });

};

/**
 * Получение выделенного текста
 */
const getSelection = () => {
    return window.getSelection().toString();
};

/**
 * Обернуть текст в span
 * TODO: доработать
 */
const wrapText = () => {
    if (getSelection() == EMPTY) return false;


    let range = window.getSelection().getRangeAt(0);
    let selectionContents = range.extractContents();
    let span = document.createElement('span');
    span.appendChild(selectionContents);

    //Убираем атрибут редактирования с прошлого редактируемого элемента
    $(CURRENT_EDIT_ELEMENT).attr(CURRENT_EDIT, 'false');
    //Указываем, что данный элемент редактируется
    $(span).attr(CURRENT_EDIT, 'true');

    range.insertNode(span);
};

const toggleCss = (attrPointer, cssProperty, cssValueOn, cssValueOff, item = null) => {
    let editableElement = $(CURRENT_EDIT_ELEMENT);

    if (editableElement.attr(attrPointer)) {
        editableElement.css(cssProperty, cssValueOff);
        // updateOwnStyle($(editableElement), cssProperty, cssValueOff);
        editableElement.removeAttr(attrPointer);
        $(item).removeClass('active-style-button');
        return;
    }

    editableElement.attr(attrPointer, 'true');
    editableElement.css(cssProperty, cssValueOn);
    // updateOwnStyle($(editableElement), cssProperty, cssValueOn);
    $(item).addClass('active-style-button');
}

/**
 * Добавления к тексту жирного
 * @param {object} event
 */
const editWeightText = (event) => {
    wrapText();
    toggleCss('data-style-weight', 'font-weight', 'bold', 'normal', '#weight');
}

/**
 * Курсив для текста
 * @param {object} event
 */
const editItalicText = (event) => {
    toggleCss('data-style-italic', 'font-style', 'italic', 'normal', '#style');
    draggable.updateRect();
    draggable.updateTarget();
}

const editUnderlineText = (event) => {
    toggleCss('data-style-underline', 'text-decoration', 'underline', 'none', '#underline');
    draggable.updateRect();
    draggable.updateTarget();
}

const editSizeText = (event) => {
    $(CURRENT_EDIT_ELEMENT).css('font-size', $('.quantity').val() + 'px');
    if (!draggable) return;
    draggable.updateRect();
    draggable.updateTarget();
}

const editBorderElement = (event) => {
    $(CURRENT_EDIT_ELEMENT).find('rect.rect_stroke').attr('stroke-width', $('.quantity-border').val());
    if (!draggable) return;
    draggable.updateRect();
    draggable.updateTarget();
}

const editBorderRadiusElement = (event) => {
    $(CURRENT_EDIT_ELEMENT).find('rect.rect_radius').attr('rx', $('.quantity-radius').val());
    if (!draggable) return;
    draggable.updateRect();
    draggable.updateTarget();
}

/**
 * Масштаба
 * @param {object} event
 */
const scaleCanvas = (event) => {
    let scale = +$('.scale').val();
    $('.main-svg').css('transform', `scale(${scale / 100})`);
}

function create_palet(index) {
    return Pickr.create({
        el: `.color-picker-${index}`,
        theme: 'monolith', // or 'monolith', or 'nano'
        comparison: false,
        swatches: [
            'rgba(244, 67, 54, 1)',
            'rgba(233, 30, 99, 1)',
            'rgba(156, 39, 176, 1)',
            'rgba(103, 58, 183, 1)',
            'rgba(63, 81, 181, 1)',
            'rgba(33, 150, 243, 1)',
            'rgba(3, 169, 244,1)',
            'rgba(0, 188, 212, 1)',
            'rgba(0, 150, 136, 1)',
            'rgba(76, 175, 80, 1)',
            'rgba(139, 195, 74, 1)',
            'rgba(205, 220, 57, 1)',
            'rgba(255, 235, 59, 1)',
            'rgba(255, 193, 7, 1)'
        ],

        components: {

            // Main components
            preview: true,
            opacity: false,
            hue: true,
            // Input / output Options
            interaction: {
                input: true,
            }
        }
    });
}

/**
 *
 *
 * @param {object} event
 */
pickr
    .on('change', (color, instance) => {
        const type_edit_elem = $(CURRENT_EDIT_ELEMENT).attr('data-type')
        if (type_edit_elem === 'background-color' || type_edit_elem === 'background-element') {
            $(CURRENT_EDIT_ELEMENT).css('background', color.toRGBA())
        }
        if (type_edit_elem === 'element') {
            $(CURRENT_EDIT_ELEMENT).find('g[data-edit-item=true]').css('fill', color.toRGBA())
        }
        $(CURRENT_EDIT_ELEMENT).css('color', color.toRGBA())
    })
    .on('changestop', instance => {
        // console.log('changestop', instance);
    });

const getToolsPanel = (event) => {
    $('.color-swatches').empty();
    let type = $(CURRENT_EDIT_ELEMENT).attr('data-type');
    $('.tools-panel-default').hide();
    $('.tools-panel-text').show();
    $('.tool-item').hide();

    if (type == 'text') {
        pickr.setColor($(CURRENT_EDIT_ELEMENT).css('color'))
        $('.font-tool').show();
        $('.multicolored-tool').hide();
        $('.color-tool').show();
        $('.size-tool').show();
        $('.style-tool').show();
        $('.delete-tool').show();
        $('.rotate-input').show();
        $('.c').css('min-width', '950px');
        return;
    }
    if (type == 'element') {
        pickr.setColor($(CURRENT_EDIT_ELEMENT).find('g[data-edit-item=true]').css('fill'))
        $('.multicolored-tool').hide();
        $('.color-tool').show();
        $('.delete-tool').show();
        $('.rotate-input').show();
        $('.c').css('min-width', '100%');
        return;
    }
    if (type == 'multicolored-element') {
        let g_svg_changed_color = $(CURRENT_EDIT_ELEMENT).find('g.color_polete');
        let g_path_changed_color = $(CURRENT_EDIT_ELEMENT).find('path.color_polete');
        let g_line_changed_color = $(CURRENT_EDIT_ELEMENT).find('line.color_polete');
        let g_rect_changed_color = $(CURRENT_EDIT_ELEMENT).find('rect.color_polete');
        let svg_pickers = [];
        
        

        g_svg_changed_color.each(function (index) {
            const source = $(this)
            let button = $('<button>', {class: `color-picker-${index}`})
            let color = source.attr('fill')
            button.appendTo($('.color-swatches'));
            const pic = create_palet(index)
                .on('init', instance => {
                    const is_set = instance.setColor(color);
                })
                .on('change', (color, instance) => {
                    source.attr('fill', color.toHEXA())
                });

            svg_pickers.push(pic)
        })
        
        g_rect_changed_color.each(function (index) {
            const source = $(this)
            let button = $('<button>', {class: `color-picker-${index}`})
            let color = source.attr('stroke')
            button.appendTo($('.color-swatches'));
            const pic = create_palet(index)
                .on('init', instance => {
                    const is_set = instance.setColor(color);
                })
                .on('change', (color, instance) => {
                    source.attr('stroke', color.toHEXA())
                });

            svg_pickers.push(pic)
        })
        
        g_line_changed_color.each(function (index) {
            const source = $(this)
            let button = $('<button>', {class: `color-picker-${index}`})
            let color = source.attr('stroke')
            button.appendTo($('.color-swatches'));
            const pic = create_palet(index)
                .on('init', instance => {
                    const is_set = instance.setColor(color);
                })
                .on('change', (color, instance) => {
                    source.attr('stroke', color.toHEXA())
                });

            svg_pickers.push(pic)
        })

        g_path_changed_color.each(function (index) {
            const source = $(this)
            let button = $('<button>', {class: `color-picker-${index}`})
            let color = source.attr('fill')

            button.appendTo($('.color-swatches'));
            const pic = create_palet(index)
                .on('init', instance => {
                    const is_set = instance.setColor(color);
                })
                .on('change', (color, instance) => {
                    source.attr('fill', color.toHEXA())
                })
            svg_pickers.push(pic)
        });
        
        
        updateCurrentBorderSize();
        updateCurrentBorderRadius();
        $('.multicolored-tool').show();
        $('.color-tool').hide();
        $('.delete-tool').show();
        $('.rotate-input').show();
        $('.border-size-tool').show();
        $('.border-radius-tool').show();
        $('.c').css('min-width', '100%');
        return;
    }

    if (type == 'img') {
        $('.multicolored-tool').hide();
        $('.file-tool').show();
        $('.delete-tool').show();
        $('.rotate-input').show();
        $('.c').css('min-width', '100%');
        return;
    }
    if (type == 'background-color') {
        pickr.setColor($(CURRENT_EDIT_ELEMENT).css('background-color'))
        $('.multicolored-tool').hide();
        $('.color-tool').show();
        $('.rotate-input').show();
        $('.c').css('min-width', '100%');
        return;
    }
    if (type == 'background-element') {
        pickr.setColor($(CURRENT_EDIT_ELEMENT).css('background'))
        $('.multicolored-tool').hide();
        $('.color-tool').show();
        $('.rotate-input').show();
        $('.c').css('min-width', '100%');
        return;

    }
    draggable.target = '';
    $('.tools-panel-text').hide();
    $('.tool-item').hide();
    $('.tools-panel-default').show();
}

const removeNode = (event) => {
    $(CURRENT_EDIT_ELEMENT).remove();
}

const addTextNode = (event) => {
    // Создание элемента через js
    // Установка обработчиков с img-events.renderHtml()

    let width = (parseInt($('.main-svg').css('width')) / 2) + 'px';
    let height = (parseInt($('.main-svg').css('height')) / 2) + 'px';
    const defaultText = 'Ваш текст';
    //Вставка идем в элемент который уже содержит текст если таковой есть
    let new_row = document.createElement("div");
    new_row.setAttribute('data-set', 'true');
    new_row.setAttribute('data-type', 'text');
    new_row.setAttribute('clickCounter', '0');
    new_row.setAttribute('contenteditable', true);
    new_row.setAttribute('style', `position: absolute; left: ${width}; top: ${height}; font-size: 50px;  color: #000; cursor: move; line-height: normal;`);
    new_row.classList.add('draggable');
    new_row.innerHTML = defaultText;
    $('.main-svg div').eq(1).prepend(new_row);

    $(new_row).on('click', (event) => {
        let clickCounter = +$(event.target).attr('clickCounter');
        if (clickCounter == 1) return;

        editableHandler(event);
    });
    $(new_row).on('click', getToolsPanel);
    $(new_row).css('cursor', 'move');
   
}

//    Загрузка файлов
let _elem = document.querySelector('.__crop_instance')

$('.add-item').click((event) => {
    if ($(event.target).attr('value') === 'text') {
        addTextNode();
    }
    if ($(event.target).attr('value') === 'img') {
        addImgNode();
    }
});

$('.on_close_crop').click(function () {
    crop.destroy();
    $('.__crop_container').hide();
    $('.temporary').remove();
    $('#input1').removeClass('__panel_button');
    $('#input2').removeClass('__panel_select');
});

const addImgNode = () => {
    const file_input = $('#upload2')
    file_input.trigger('click');

    $('[data-set="true"]').click(editableHandler);
    $('[data-set="true"]').click(getToolsPanel);
}

$('#upload1').change((event) => {
    // __panel_button replace image

    if ($('#upload1')[0].files.length < 1) {
        $('.__crop_container').hide();
        $('#input1').removeClass('__panel_select');
        return
    }

    $('.__crop_container').show();
    $('.on_crop').addClass('__panel_button')
    const width = $(CURRENT_EDIT_ELEMENT).width()
    const height = $(CURRENT_EDIT_ELEMENT).height()
    crop = new Croppie(_elem, {
        viewport: {
            width: width,
            height: height,
        },
        // enableResize: true,
        mouseWheelZoom: 'ctrl'
    });
    let img = $('#upload1')[0].files[0];
    let reader = new FileReader();
    reader.readAsDataURL(img);
    reader.onload = () => {
        crop.bind({url: reader.result});
        $('#upload1').value = "";

    }
});


$('#upload2').change((event) => {
    let width = (parseInt($('.main-svg').css('width')) / 2) + 'px';
    let height = (parseInt($('.main-svg').css('height')) / 2) + 'px';
    $('.main-svg div').eq(1).prepend(`
    <img style="
            position: absolute;
            left: ${width};
            top: ${height};
            z-index: 10;
        "
         src="#"
         class="draggable temporary" 
         data-set="true" 
         data-type="img"
         >
    `);

    if ($('#upload2')[0].files.length < 1) {
        $('.temporary').remove();
        $('.__crop_container').hide();
        $('.temporary').removeClass('temporary');
        $('#input2').removeClass('__panel_select');
        return
    }

    $('.__crop_container').show();
    $('.on_crop').addClass('__panel_select')

    crop = new Croppie(_elem, {
        viewport: {
            width: 320,
            height: 320,
        },
        enableResize: true,
        mouseWheelZoom: 'ctrl'
    });

    let img = $('#upload2')[0].files[0];
    let reader = new FileReader();
    reader.readAsDataURL(img);
    reader.onload = () => {
        crop.bind({url: reader.result});
        $('#upload2').value = "";
    };
});


$('.on_crop').click(function () {
    const self = this;
    crop.result('base64').then(function (data) {
        if ($(self).hasClass('__panel_button')) {
            console.log('__panel_button')
            $(CURRENT_EDIT_ELEMENT).attr('src', data);
        }
        if ($(self).hasClass('__panel_select')) {
            $('.temporary').attr('src', data)
        }
        // Зачистка после добавления картинки
        crop.destroy();
        $('.__crop_container').hide();
        $('.temporary').removeClass('temporary');
        $(self).removeClass('__panel_select');
        $(self).removeClass('__panel_button');
    });
});

// Конец загрузки файлов


$('#weight').click(editWeightText);
$('#style').click(editItalicText);
$('#underline').click(editUnderlineText);
$('.quantity').keyup(editSizeText);
$('.size-tool').click(editSizeText);
$('.quantity-border').keyup(editBorderElement);
$('.border-size-tool').click(editBorderElement);
$('.quantity-radius').keyup(editBorderRadiusElement);
$('.border-radius-tool').click(editBorderRadiusElement);
$('.scale').keyup(scaleCanvas);
$('.delete-button').click(removeNode);

$('.size-tool-button').click((event) => {
    let isPlus = $(event.target).hasClass('plus');
    let currentScale = +$('.scale').val();
    let imgWidth = parseInt($('.main-svg').css('width'));
    let imgHeight = parseInt($('.canvas1').css('height'));
    let canvasWidth = parseInt($('.container .h-100').css('width'));
    /*  let topMenuHeight = parseInt($('.top-menu').css('height'));
      let bottomMenuHeight = parseInt($('.menu-bottom').css('height'));
      let canvasHeight = parseInt($('.container .h-100').css('height'));
      let mainHeight = canvasHeight - bottomMenuHeight - topMenuHeight;
      console.log('topMenuHeight');*/


    if (currentScale < 200) {

        if (isPlus) {
            currentScale += 10;
        } else if (currentScale > 10) {
            currentScale -= 10;
        }
    } else {
        if (isPlus) {
            currentScale += 0;
        } else if (currentScale > 10) {
            currentScale -= 10;
        }
    }

    /*   if (isPlus) {
          currentScale += 10;
      } else if (currentScale > 10) {
          currentScale -= 10;
      }
  */


    $('.scale').val(currentScale);
    $('.main-svg').css('transform', `scale(${currentScale / 100})`);
    updateView();
    if (!draggable) return;
    draggable.updateRect();
    draggable.updateTarget();
});

function updateView() {
    const mainSVG = document.querySelector('.canvas-wrap .main-svg');
    const newWidth = mainSVG.getBoundingClientRect().width;
    const newHeight = mainSVG.getBoundingClientRect().height;

    $('.canvas-wrap').css({
        width: `${newWidth}px`,
        height: `${newHeight}px`,
    })
}


$('.main-svg').click((event) => {
    let element = $(event.target);

    if (element.attr('data-set')) return;
    $('.tools-panel-text').hide();
    $('.tool-item').hide();
    $('.tools-panel-default').show();
    $('.font-section').hide();
    $('.category-section').show();
    $('.fonts-list').empty();


    draggable.target = '';
})

$('.rotate-input').keyup((event) => {
    let rotate = $('.rotate-input').val();
    $(CURRENT_EDIT_ELEMENT).css('transform', `rotate(${rotate}deg)`);
    draggable.updateRect();
})

$(window).click((event) => {

    if ($(event.target).hasClass('window-menu')) return;
    //  if ($(event.target).hasClass('window-menu-share')) return;

    if ($(event.target).hasClass('no-main-svg')) {
        $('.tools-panel-text').hide();
        $('.tools-panel-default').show();
        if (draggable) draggable.target = '';
    }

    $('.dropdown-menu-save').removeClass('show-block');
    //  $('.dropdown-menu-share').removeClass('show-block');

});

$('#style-block').click((event) => {
    $('.style-block-container').toggleClass('hide');
});

$('#style-text').click((event) => {
    $('.style-text-container').toggleClass('hide');
});


$('.share-button-menu').click((event) => {
    $('.dropdown-menu-share').toggleClass('show-block');
});


$('.keep-button-menu').click((event) => {
    $('.dropdown-menu-keep').toggleClass('keep-menu');
});

$('.main-svg-container').scroll((event) => {
    if (!draggable) return;

    draggable.updateRect();
    draggable.updateTarget();


});

function onSetTextAlign(value) {
    let editableElement = $(CURRENT_EDIT_ELEMENT);
    editableElement.css('text-align', value)
}

$(document).mouseup(function (e) { // событие клика по веб-документу
    let div = $(".style-text-container"); // тут указываем ID элемента
    if (!div.is(e.target) // если клик был не по нашему блоку
        && div.has(e.target).length === 0) { // и не по его дочерним элементам
        div.addClass('hide');
    }
});


$(document).mouseup(function (e) { // событие клика по веб-документу
    let div = $(".dropdown-menu-share"); // тут указываем ID элемента
    if (!div.is(e.target) // если клик был не по нашему блоку
        && div.has(e.target).length === 0) { // и не по его дочерним элементам
        div.removeClass('show-block');
    }
});

$(document).mouseup(function (e) { // событие клика по веб-документу

    let div = $(".dropdown-menu-keep"); // тут указываем ID элемента
    if (!div.is(e.target) // если клик был не по нашему блоку
        && div.has(e.target).length === 0) { // и не по его дочерним элементам
        if ($(e.target).hasClass('yes_or_no_button')) {
            return
        } else {
            div.removeClass('keep-menu');
        }
    }
});

//Скликивание редактирования вне канваса
$(document).mouseup(function (e) {
    if ($(e.target).hasClass('view-container')) {
        if (draggable) {
            $('.tools-panel-text').hide();
            $('.tool-item').hide();
            $('.tools-panel-default').show();
            $('.color-swatches').empty();
            // TODO: убирать палетку
            draggable.target = '';
        }
    }
});

