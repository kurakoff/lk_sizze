class SaverUserProgressScreen {
    constructor(appendTemplate, timeout = 15) {
        // Аргумент конструктура - функция,
        // которая принимает шаблон и производит его вставку в редактор appendTemplate(html)
        this.timeout = timeout;
        this.allowed_save = true;
        this.appendTemplate = appendTemplate;
        $('.db_get_original').on('click', () => this.getOriginalBackendTemplate());
    }

    getActiveScreenHtml() {
        let content = $('.main-svg').html()
            .replace(/currenteditable="true"/g, 'currenteditable="false"')
            .replace(/currentEditable="true"/g, '');
        return content;
    }

    saveTemplate() {
        if (this.allowed_save) {
            const id = this.getActiveId();
            const active_template = this.getActiveScreenHtml();
            //     AJAX SAVE SCREEN
        }
    }

    getOriginalBackendTemplate(id) {
        this.allowed_save = false;
        const node_id = this.getActiveId() || id;
        const self = this;
        $.ajax({
            type: 'GET',
            url: 'img/html',
            data: {
                id: node_id
            },
            success: (html) => {
                self.appendTemplate(html);
                this.allowed_save = true;
                this.clearDragControlBox()
            }
        });
    }

    clearDragControlBox() {
        $('.moveable-control-box').empty()
    }

    getActiveId() {
        // Вернуть активный ID установленного в редактор screen    
    }

    runAutoSave() {
        setInterval(() => {
            this.saveTemplate();
            console.log('save!')
        }, this.timeout * 1000);
    }
}



