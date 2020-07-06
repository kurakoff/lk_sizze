class SaverUserProgressScreen {
    constructor(appendTemplate, timeout = 15) {
        // Аргумент appendTemplate конструктура - функция вставки html скрина на сцену
        this.timeout = timeout;
        this.allowed_save = true;
        this.appendTemplate = appendTemplate;
        this.csrf_token = $("input[name=csrfmiddlewaretoken]").val();


        this.getTemplate(undefined, 'init_screen');
        $('.get_original_screen').on('click', (e) => this.getTemplate(e, 'original_screen'));
        $('.get_screen').on('click', (e) => this.getTemplate(e, 'get_screen', $(e.target).data('screen-id')));
    }

    getHtml() {
        let content = $('.main-svg').html()
            .replace(/currenteditable="true"/g, 'currenteditable="false"')
            .replace(/currentEditable="true"/g, '');
        return content;
    }

    saveTemplate() {
        if (this.allowed_save) {
            const id = this.getActiveScreen();
            const active_template = this.getHtml();
            if (id) {
                const data = {
                    csrfmiddlewaretoken: this.csrf_token,
                    id_screen: id,
                    layout: active_template,
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

    getActiveScreen() {
        //ПОЛУЧТЬ ID
        return 1
    }

    getProjectId() {
        //ПОЛУЧТЬ ID
        return 1
    }

    getTemplate(e, action, screen_id) {
        if (e) e.preventDefault()
        if (e) e.stopPropagation()
        this.allowed_save = false;
        const project_id = this.getProjectId()
        const data = {
            csrfmiddlewaretoken: this.csrf_token,
            screen_id: screen_id,
            project_id: project_id,
        }
        $.post(`/screen/${action}`, data, (response) => {
            this.appendTemplate(response['screen_html']);
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



