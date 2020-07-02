class SaverUserProgressScreen {
    constructor(appendTemplate, timeout = 15) {
        // Аргумент appendTemplate конструктура - функция вставки html скрина на сцену
        this.timeout = timeout;
        this.allowed_save = true;
        this.appendTemplate = appendTemplate;
        this.getTemplate('init_screen');
        $('.get_original_screen').on('click', () => this.getTemplate('original_screen'));
        $('.get_screen').on('click', (e) => this.getTemplate('get_screen', $(e.target).data('screen-id')));
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
                $.ajax({
                    type: 'GET',
                    url: `/screen/save`,
                    data: {
                        layout: active_template,
                    },
                    success: (data) => {
                        if (data.success) {
                            console.log('Шаблон успешно сохранен')
                        } else {
                            console.error('ОШИБКА! Срин не сохранен!')

                        }
                    }
                });
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


    getTemplate(action, screen_id) {
        this.allowed_save = false;
        const self = this;
        const project_id = this.getProjectId()
        $.ajax({
            type: 'GET',
            url: `/screen/${action}`,
            data: {
                id: id,
                project_id: project_id,
                action: action,
            },
            success: (data) => {
                self.appendTemplate(data['screen_html']);
                this.allowed_save = true;
                this.clearDragControlBox();
            }
        });
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



