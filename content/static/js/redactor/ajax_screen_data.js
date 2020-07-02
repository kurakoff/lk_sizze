class SaverProgress {
    constructor(appendTemplate, timeout = 15) {
        // Аргумент appendTemplate конструктура - функция вставки html скрина на сцену
        this.timeout = timeout;
        this.allowed_save = true;
        this.appendTemplate = appendTemplate;
        $('.get_original').on('click', () => this.getBackendTemplate());
    }

    getHtml() {
        let content = $('.main-svg').html()
            .replace(/currenteditable="true"/g, 'currenteditable="false"')
            .replace(/currentEditable="true"/g, '');
        return content;
    }

    saveTemplate() {
        if (this.allowed_save) {
            const id = this.getActiveId();
            const active_template = this.getHtml();
            if (id) {
                //    Отправка на сервер
            }
        }
    }

    getActiveId() {
        //ПОЛУЧТЬ ID 
        return 1
    }

    getBackendTemplate(id) {
        this.allowed_save = false;
        const self = this;
        $.ajax({
            type: 'GET',
            url: 'img/html',
            data: {
                id: id
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



