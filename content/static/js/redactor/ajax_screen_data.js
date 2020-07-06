class SaverUserProgressScreen {
    constructor(appendTemplate, timeout = 15) {
        // Аргумент appendTemplate конструктура - функция вставки html скрина на сцену
        this.timeout = timeout;
        this.allowed_save = true;
        this.appendTemplate = appendTemplate;
        this.csrf_token = $("input[name=csrfmiddlewaretoken]").val();


        this.getTemplate(undefined, 'init_screen');
        $('.get_original_screen').on('click', (e) => this.getTemplate(e, 'original_screen'));
        $(document).on('click', '.get_screen', (e) => this.getTemplate(e, 'get_screen', $(e.target).data('screen-id')))
    }

    getHtml() {
        let content = $('.main-svg').html()
            .replace(/currenteditable="true"/g, 'currenteditable="false"')
            .replace(/currentEditable="true"/g, '');
        return content;
    }

    saveTemplate() {
        if (this.allowed_save) {
            const id = this.getActiveScreenID();
            const active_template = this.getHtml();
            const project_id = this.getProjectId()

            if (id) {
                const data = {
                    csrfmiddlewaretoken: this.csrf_token,
                    screen_id: id,
                    layout: active_template,
                    project_id: project_id,
                }
                $.post("/screen/save_screen", data, (response) => {
                    if (response.success) {
                        console.log('Шаблон успешно сохранен')
                    } else {
                        console.error('ОШИБКА! Срин не сохранен!')

                    }
                }, 'json')
            }
        }
    }

    getActiveScreenID() {
        return $('.main-svg').data('screen_id')
    }

    getProjectId() {
        return $('.data_data').data('project-id')
    }

    getTemplate(e, action) {
        let screen_id;
        if (e) {
            e.stopPropagation()
            e.preventDefault()
            screen_id = ($(e.target).closest('.get_screen').data('screen-id'))
        }


        this.allowed_save = false;
        const project_id = this.getProjectId()
        const data = {
            csrfmiddlewaretoken: this.csrf_token,
            screen_id: screen_id,
            project_id: project_id,
        }
        $.post(`/screen/${action}`, data, (response) => {
            this.appendTemplate(response['screen_html'], response.screen_id);
            this.allowed_save = true;
            this.clearDragControlBox();
        }, 'json')
    }

    clearDragControlBox() {
        $('.moveable-control-box').empty()
    }

    runAutoSave() {
        setInterval(() => {
            this.saveTemplate();
        }, this.timeout * 1000);
    }
}



