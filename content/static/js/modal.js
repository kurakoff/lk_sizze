// File#: _1_dialog
// Usage: codyhouse.co/license
(function () {
    var Dialog = function (element) {
        this.element = element;
        this.triggers = document.querySelectorAll('[aria-controls="' + this.element.getAttribute('id') + '"]');
        this.firstFocusable = null;
        this.lastFocusable = null;
        this.selectedTrigger = null;
        this.showClass = "dialog--is-visible";
        initDialog(this);
    };

    function initDialog(dialog) {
        if (dialog.triggers) {
            for (var i = 0; i < dialog.triggers.length; i++) {
                dialog.triggers[i].addEventListener('click', function (event) {
                    event.preventDefault();
                    dialog.selectedTrigger = event.target;
                    showDialog(dialog);
                    initDialogEvents(dialog);
                });
            }
        }

        // listen to the openDialog event -> open dialog without a trigger button
        dialog.element.addEventListener('openDialog', function (event) {
            if (event.detail) self.selectedTrigger = event.detail;
            showDialog(dialog);
            initDialogEvents(dialog);
        });
    };

    function showDialog(dialog) {
        Util.addClass(dialog.element, dialog.showClass);
        getFocusableElements(dialog);
        // dialog.firstFocusable.focus();
        // wait for the end of transitions before moving focus
        dialog.element.addEventListener("transitionend", function cb(event) {
            dialog.firstFocusable.focus();
            dialog.element.removeEventListener("transitionend", cb);
        });
        emitDialogEvents(dialog, 'dialogIsOpen');
    };

    function closeDialog(dialog) {
        Util.removeClass(dialog.element, dialog.showClass);
        dialog.firstFocusable = null;
        dialog.lastFocusable = null;
        if (dialog.selectedTrigger) dialog.selectedTrigger.focus();
        //remove listeners
        cancelDialogEvents(dialog);
        emitDialogEvents(dialog, 'dialogIsClose');
    };

    function initDialogEvents(dialog) {
        //add event listeners
        dialog.element.addEventListener('keydown', handleEvent.bind(dialog));
        dialog.element.addEventListener('click', handleEvent.bind(dialog));
    };

    function cancelDialogEvents(dialog) {
        //remove event listeners
        dialog.element.removeEventListener('keydown', handleEvent.bind(dialog));
        dialog.element.removeEventListener('click', handleEvent.bind(dialog));
    };

    function handleEvent(event) {
        // handle events
        switch (event.type) {
            case 'click': {
                initClick(this, event);
            }
            case 'keydown': {
                initKeyDown(this, event);
            }
        }
    };

    function initKeyDown(dialog, event) {
        if (event.keyCode && event.keyCode == 27 || event.key && event.key == 'Escape') {
            //close dialog on esc
            closeDialog(dialog);
        } else if (event.keyCode && event.keyCode == 9 || event.key && event.key == 'Tab') {
            //trap focus inside dialog
            trapFocus(dialog, event);
        }
    };

    function initClick(dialog, event) {
        //close dialog when clicking on close button
        if (!event.target.closest('.js-dialog__close')) return;
        event.preventDefault();
        closeDialog(dialog);
    };

    function trapFocus(dialog, event) {
        if (dialog.firstFocusable == document.activeElement && event.shiftKey) {
            //on Shift+Tab -> focus last focusable element when focus moves out of dialog
            event.preventDefault();
            dialog.lastFocusable.focus();
        }
        if (dialog.lastFocusable == document.activeElement && !event.shiftKey) {
            //on Tab -> focus first focusable element when focus moves out of dialog
            event.preventDefault();
            dialog.firstFocusable.focus();
        }
    };

    function getFocusableElements(dialog) {
        //get all focusable elements inside the dialog
        var allFocusable = dialog.element.querySelectorAll('[href], input:not([disabled]), select:not([disabled]), textarea:not([disabled]), button:not([disabled]), iframe, object, embed, [tabindex]:not([tabindex="-1"]), [contenteditable], audio[controls], video[controls], summary');
        getFirstVisible(dialog, allFocusable);
        getLastVisible(dialog, allFocusable);
    };

    function getFirstVisible(dialog, elements) {
        //get first visible focusable element inside the dialog
        for (var i = 0; i < elements.length; i++) {
            if (elements[i].offsetWidth || elements[i].offsetHeight || elements[i].getClientRects().length) {
                dialog.firstFocusable = elements[i];
                return true;
            }
        }
    };

    function getLastVisible(dialog, elements) {
        //get last visible focusable element inside the dialog
        for (var i = elements.length - 1; i >= 0; i--) {
            if (elements[i].offsetWidth || elements[i].offsetHeight || elements[i].getClientRects().length) {
                dialog.lastFocusable = elements[i];
                return true;
            }
        }
    };

    function emitDialogEvents(dialog, eventName) {
        var event = new CustomEvent(eventName, {detail: dialog.selectedTrigger});
        dialog.element.dispatchEvent(event);
    };

    //initialize the Dialog objects
    var dialogs = document.getElementsByClassName('js-dialog');
    if (dialogs.length > 0) {
        for (var i = 0; i < dialogs.length; i++) {
            (function (i) {
                new Dialog(dialogs[i]);
            })(i);
        }
    }
}());


// File#: _1_modal-window
// Usage: codyhouse.co/license
(function () {
    var Modal = function (element) {
        this.element = element;
        this.triggers = document.querySelectorAll('[aria-controls="' + this.element.getAttribute('id') + '"]');
        this.firstFocusable = null;
        this.lastFocusable = null;
        this.moveFocusEl = null; // focus will be moved to this element when modal is open
        this.modalFocus = this.element.getAttribute('data-modal-first-focus') ? this.element.querySelector(this.element.getAttribute('data-modal-first-focus')) : null;
        this.selectedTrigger = null;
        this.showClass = "modal--is-visible";
        this.initModal();
    };

    Modal.prototype.initModal = function () {
        var self = this;
        //open modal when clicking on trigger buttons
        if (this.triggers) {
            for (var i = 0; i < this.triggers.length; i++) {
                //
                //Ограничение повторной инициализации на динамически загружаемый элемент
                //
                if (!$(this.triggers[i]).hasClass('was_init')) {
                    this.triggers[i].addEventListener('click', function (event) {
                        event.preventDefault();
                        if (Util.hasClass(self.element, self.showClass)) {
                            self.closeModal();
                            return;
                        }
                        self.selectedTrigger = event.target;
                        self.showModal();
                        self.initModalEvents();
                    });
                    $(this.triggers[i]).addClass('was_init')
                }

            }
        }

        // listen to the openModal event -> open modal without a trigger button
        this.element.addEventListener('openModal', function (event) {
            if (event.detail) self.selectedTrigger = event.detail;
            self.showModal();
            self.initModalEvents();
        });

        // listen to the closeModal event -> close modal without a trigger button
        this.element.addEventListener('closeModal', function (event) {
            if (event.detail) self.selectedTrigger = event.detail;
            self.closeModal();
        });

        // if modal is open by default -> initialise modal events
        if (Util.hasClass(this.element, this.showClass)) this.initModalEvents();
    };

    Modal.prototype.showModal = function () {
        var self = this;
        Util.addClass(this.element, this.showClass);
        this.getFocusableElements();
        this.moveFocusEl.focus();
        // wait for the end of transitions before moving focus
        this.element.addEventListener("transitionend", function cb(event) {
            self.moveFocusEl.focus();
            self.element.removeEventListener("transitionend", cb);
        });
        this.emitModalEvents('modalIsOpen');
    };

    Modal.prototype.closeModal = function () {
        if (!Util.hasClass(this.element, this.showClass)) return;
        Util.removeClass(this.element, this.showClass);
        this.firstFocusable = null;
        this.lastFocusable = null;
        this.moveFocusEl = null;
        if (this.selectedTrigger) this.selectedTrigger.focus();
        //remove listeners
        this.cancelModalEvents();
        this.emitModalEvents('modalIsClose');
    };

    Modal.prototype.initModalEvents = function () {
        //add event listeners
        this.element.addEventListener('keydown', this);
        this.element.addEventListener('click', this);
    };

    Modal.prototype.cancelModalEvents = function () {
        //remove event listeners
        this.element.removeEventListener('keydown', this);
        this.element.removeEventListener('click', this);
    };

    Modal.prototype.handleEvent = function (event) {
        switch (event.type) {
            case 'click': {
                this.initClick(event);
            }
            case 'keydown': {
                this.initKeyDown(event);
            }
        }
    };

    Modal.prototype.initKeyDown = function (event) {
        if (event.keyCode && event.keyCode == 9 || event.key && event.key == 'Tab') {
            //trap focus inside modal
            this.trapFocus(event);
        } else if ((event.keyCode && event.keyCode == 13 || event.key && event.key == 'Enter') && event.target.closest('.js-modal__close')) {
            event.preventDefault();
            this.closeModal(); // close modal when pressing Enter on close button
        }
    };

    Modal.prototype.initClick = function (event) {
        //close modal when clicking on close button or modal bg layer
        if (!event.target.closest('.js-modal__close') && !Util.hasClass(event.target, 'js-modal')) return;
        event.preventDefault();
        this.closeModal();
    };

    Modal.prototype.trapFocus = function (event) {
        if (this.firstFocusable == document.activeElement && event.shiftKey) {
            //on Shift+Tab -> focus last focusable element when focus moves out of modal
            event.preventDefault();
            this.lastFocusable.focus();
        }
        if (this.lastFocusable == document.activeElement && !event.shiftKey) {
            //on Tab -> focus first focusable element when focus moves out of modal
            event.preventDefault();
            this.firstFocusable.focus();
        }
    }

    Modal.prototype.getFocusableElements = function () {
        //get all focusable elements inside the modal
        var allFocusable = this.element.querySelectorAll(focusableElString);
        this.getFirstVisible(allFocusable);
        this.getLastVisible(allFocusable);
        this.getFirstFocusable();
    };

    Modal.prototype.getFirstVisible = function (elements) {
        //get first visible focusable element inside the modal
        for (var i = 0; i < elements.length; i++) {
            if (isVisible(elements[i])) {
                this.firstFocusable = elements[i];
                break;
            }
        }
    };

    Modal.prototype.getLastVisible = function (elements) {
        //get last visible focusable element inside the modal
        for (var i = elements.length - 1; i >= 0; i--) {
            if (isVisible(elements[i])) {
                this.lastFocusable = elements[i];
                break;
            }
        }
    };

    Modal.prototype.getFirstFocusable = function () {
        if (!this.modalFocus || !Element.prototype.matches) {
            this.moveFocusEl = this.firstFocusable;
            return;
        }
        var containerIsFocusable = this.modalFocus.matches(focusableElString);
        if (containerIsFocusable) {
            this.moveFocusEl = this.modalFocus;
        } else {
            this.moveFocusEl = false;
            var elements = this.modalFocus.querySelectorAll(focusableElString);
            for (var i = 0; i < elements.length; i++) {
                if (isVisible(elements[i])) {
                    this.moveFocusEl = elements[i];
                    break;
                }
            }
            if (!this.moveFocusEl) this.moveFocusEl = this.firstFocusable;
        }
    };

    Modal.prototype.emitModalEvents = function (eventName) {
        var event = new CustomEvent(eventName, {detail: this.selectedTrigger});
        this.element.dispatchEvent(event);
    };

    function isVisible(element) {
        return element.offsetWidth || element.offsetHeight || element.getClientRects().length;
    };

    //initialize the Modal objects
    var modals = document.getElementsByClassName('js-modal');
    // generic focusable elements string selector
    var focusableElString = '[href], input:not([disabled]), select:not([disabled]), textarea:not([disabled]), button:not([disabled]), iframe, object, embed, [tabindex]:not([tabindex="-1"]), [contenteditable], audio[controls], video[controls], summary';
    if (modals.length > 0) {
        var modalArrays = [];
        for (var i = 0; i < modals.length; i++) {
            (function (i) {
                modalArrays.push(new Modal(modals[i]));
            })(i);
        }

        window.addEventListener('keydown', function (event) { //close modal window on esc
            if (event.keyCode && event.keyCode == 27 || event.key && event.key.toLowerCase() == 'escape') {
                for (var i = 0; i < modalArrays.length; i++) {
                    (function (i) {
                        modalArrays[i].closeModal();
                    })(i);
                }
                ;
            }
        });
    }
}());