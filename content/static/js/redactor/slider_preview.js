class SliderPreview {
    // Сладер, динамический
    // updateInit Запускается каждый раз когда нажимается кнопка просмотра

    constructor() {
        this.container = '.owl-carousel'
        this.items = []
        this.current_root = 0
        this.ids_nodes = []
        $('#show_preview').click(() => {
            this.updateInit()
        })
        $('.close_slider').click(() => {
            this.hideSlider()
        })
        this.owl = '';
    }

    init() {
        this.owl = $(this.container).owlCarousel({
            items: 1,
            nav: true,
            responsive: {
                0: {
                    touchDrag: false
                },
                1000: {
                    touchDrag: true
                }
            }
            // autoWidth: true,
            // center: true,
        });
        this.showSlider()
    }


    hideSlider() {
        $('.slider_popup').hide();
    }

    showSlider() {
        $('.slider_popup').show();
    }

    getTemplate(id, is_last) {
        $.post(`/screen/${action}`, data, (response) => {
            $(this.container).append(`<div class="slide_container">${response['screen_html']}</div>`)
            if (is_last) {
                setTimeout(() => {
                    this.init()
                }, 500)
            }
        }, 'json')

    }


    destroy() {
        if (this.owl) {
            // destroy
            this.owl.trigger('destroy.owl.carousel')
            $(this.container).empty()
            $(this.container).removeClass('owl-loaded')
        }
    }

    getItems(ids) {
        ids.forEach((id, index, array) => {
            this.getTemplate(id, index === array.length - 1)
        })
    }

    updateInit() {
        if (true) {
            this.destroy()
            this.items = []
            this.ids_nodes = $('.data_data').data('ids_project_screens')
            this.getItems(this.ids_nodes)
        } else if (this.owl) {
            this.showSlider()
        }
    }
}