class SaverProgress {
    constructor(appendTemplate, timeout = 15) {
        // Аргумент конструктура - функция,
        // которая принимает шаблон и производит его вставку в редактор appendTemplate(html)
        this.timeout = timeout;
        this.tt_db = new Dexie("tt_db");
        this.tt_db.version(14).stores({
            templates: 'id, template'
        }).upgrade(function (db) {
            db.templates.clear();
        });
        this.allowed_save = true;
        this.appendTemplate = appendTemplate;
        $('.db_get_original').on('click', () => this.getOriginalBackendTemplate());
    }

    getActiveHtml() {
        let content = $('.main-svg').html()
            .replace(/currenteditable="true"/g, 'currenteditable="false"')
            .replace(/currentEditable="true"/g, '');
        return content;
    }

    saveTemplate() {
        if (this.allowed_save) {
            const id = this.getActiveId();
            const active_template = this.getActiveHtml();
            if (id) {
                this.tt_db.templates.put({
                    id: id,
                    template: active_template,
                }).then(() => {
                    // console.log('Cохранен, id: ', id, 'Длинна: ', active_template.length)
                }).catch((error) => {
                    console.error('Произошла ошибка при сохранении', error);
                });
            }
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
            }
        });
    }

    clearDragControlBox() {
        $('.moveable-control-box').empty()
    }

    getActiveId() {
        if ($('div.content-block.active').data('list') === 1) {
            return $('img.node.active').data('node') || $('div.content-block.active').data('id');
        } else {
            return $('div.content-block.active').data('id');
        }
    }

    appendTemplateIfExist(id) {
        const self = this;
        this.tt_db.templates.get({id: id}).then(function (result) {
            if (result) {
                self.appendTemplate(result.template);
                // console.error('appendTemplateIfExist IF', true);
            } else {
                // console.error('appendTemplateIfExist ELSE', false);
                self.getOriginalBackendTemplate(id);
            }
        }).catch(function (error) {
            // console.error('appendTemplateIfExist ERROR', error);
        });
        this.clearDragControlBox();

    }

    runAutoSave() {
        setInterval(() => {
            this.saveTemplate();
        }, this.timeout * 1000);
    }
}



