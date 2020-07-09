class SliderPreview {
    // Сладер, динамический
    // updateInit запустить при изменении kit screen

    constructor() {
        this.container = '.owl-carousel'
        this.items = []
        this.ids_nodes = []
        $('#show_preview').click(() => {
            this.updateInit(true)
        })
        $('.close_slider').click(() => {
            this.hideSlider()
        })
        this.owl = '';
        this.show_now = true
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
        const csrf_token = $("input[name=csrfmiddlewaretoken]").val();
        let data = {
            csrfmiddlewaretoken: csrf_token,
            screen_id: id,
        }
        $.post(`/screen/get_screen`, data, (response) => {
            $(this.container).append(`<div class="slide_container">${response['screen_html']}</div>`)
            console.log(this.show_now, is_last, this.show_now && is_last)
            if (this.show_now && is_last) {
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
        // TODO: Зачем делать каждый request отдельно на id??? ->>> []ids
        ids.forEach((id, index, array) => {
            this.getTemplate(id, index === array.length - 1)
        })
    }

    updateInit(show_now) {
        this.destroy()
        this.items = []
        this.ids_nodes = $('.data_data').data('ids_project_screens')
        this.getItems(this.ids_nodes)
        this.show_now = show_now
    }
}