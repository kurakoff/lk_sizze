// Utility function
function Util() {
};

/* 
	class manipulation functions
*/
Util.hasClass = function (el, className) {
    if (el.classList) return el.classList.contains(className);
    else return !!el.className.match(new RegExp('(\\s|^)' + className + '(\\s|$)'));
};

Util.addClass = function (el, className) {
    var classList = className.split(' ');
    if (el.classList) el.classList.add(classList[0]);
    else if (!Util.hasClass(el, classList[0])) el.className += " " + classList[0];
    if (classList.length > 1) Util.addClass(el, classList.slice(1).join(' '));
};

Util.removeClass = function (el, className) {
    var classList = className.split(' ');
    if (el.classList) el.classList.remove(classList[0]);
    else if (Util.hasClass(el, classList[0])) {
        var reg = new RegExp('(\\s|^)' + classList[0] + '(\\s|$)');
        el.className = el.className.replace(reg, ' ');
    }
    if (classList.length > 1) Util.removeClass(el, classList.slice(1).join(' '));
};

Util.toggleClass = function (el, className, bool) {
    if (bool) Util.addClass(el, className);
    else Util.removeClass(el, className);
};

Util.setAttributes = function (el, attrs) {
    for (var key in attrs) {
        el.setAttribute(key, attrs[key]);
    }
};

/* 
  DOM manipulation
*/
Util.getChildrenByClassName = function (el, className) {
    var children = el.children,
        childrenByClass = [];
    for (var i = 0; i < el.children.length; i++) {
        if (Util.hasClass(el.children[i], className)) childrenByClass.push(el.children[i]);
    }
    return childrenByClass;
};

Util.is = function (elem, selector) {
    if (selector.nodeType) {
        return elem === selector;
    }

    var qa = (typeof (selector) === 'string' ? document.querySelectorAll(selector) : selector),
        length = qa.length,
        returnArr = [];

    while (length--) {
        if (qa[length] === elem) {
            return true;
        }
    }

    return false;
};

/* 
	Animate height of an element
*/
Util.setHeight = function (start, to, element, duration, cb) {
    var change = to - start,
        currentTime = null;

    var animateHeight = function (timestamp) {
        if (!currentTime) currentTime = timestamp;
        var progress = timestamp - currentTime;
        var val = parseInt((progress / duration) * change + start);
        element.style.height = val + "px";
        if (progress < duration) {
            window.requestAnimationFrame(animateHeight);
        } else {
            cb();
        }
    };

    //set the height of the element before starting animation -> fix bug on Safari
    element.style.height = start + "px";
    window.requestAnimationFrame(animateHeight);
};

/* 
	Smooth Scroll
*/

Util.scrollTo = function (final, duration, cb, scrollEl) {
    var element = scrollEl || window;
    var start = element.scrollTop || document.documentElement.scrollTop,
        currentTime = null;

    if (!scrollEl) start = window.scrollY || document.documentElement.scrollTop;

    var animateScroll = function (timestamp) {
        if (!currentTime) currentTime = timestamp;
        var progress = timestamp - currentTime;
        if (progress > duration) progress = duration;
        var val = Math.easeInOutQuad(progress, start, final - start, duration);
        element.scrollTo(0, val);
        if (progress < duration) {
            window.requestAnimationFrame(animateScroll);
        } else {
            cb && cb();
        }
    };

    window.requestAnimationFrame(animateScroll);
};

/* 
  Focus utility classes
*/

//Move focus to an element
Util.moveFocus = function (element) {
    if (!element) element = document.getElementsByTagName("body")[0];
    element.focus();
    if (document.activeElement !== element) {
        element.setAttribute('tabindex', '-1');
        element.focus();
    }
};

/* 
  Misc
*/

Util.getIndexInArray = function (array, el) {
    return Array.prototype.indexOf.call(array, el);
};

Util.cssSupports = function (property, value) {
    if ('CSS' in window) {
        return CSS.supports(property, value);
    } else {
        var jsProperty = property.replace(/-([a-z])/g, function (g) {
            return g[1].toUpperCase();
        });
        return jsProperty in document.body.style;
    }
};

// merge a set of user options into plugin defaults
// https://gomakethings.com/vanilla-javascript-version-of-jquery-extend/
Util.extend = function () {
    // Variables
    var extended = {};
    var deep = false;
    var i = 0;
    var length = arguments.length;

    // Check if a deep merge
    if (Object.prototype.toString.call(arguments[0]) === '[object Boolean]') {
        deep = arguments[0];
        i++;
    }

    // Merge the object into the extended object
    var merge = function (obj) {
        for (var prop in obj) {
            if (Object.prototype.hasOwnProperty.call(obj, prop)) {
                // If deep merge and property is an object, merge properties
                if (deep && Object.prototype.toString.call(obj[prop]) === '[object Object]') {
                    extended[prop] = extend(true, extended[prop], obj[prop]);
                } else {
                    extended[prop] = obj[prop];
                }
            }
        }
    };

    // Loop through each object and conduct a merge
    for (; i < length; i++) {
        var obj = arguments[i];
        merge(obj);
    }

    return extended;
};

// Check if Reduced Motion is enabled
Util.osHasReducedMotion = function () {
    if (!window.matchMedia) return false;
    var matchMediaObj = window.matchMedia('(prefers-reduced-motion: reduce)');
    if (matchMediaObj) return matchMediaObj.matches;
    return false; // return false if not supported
};

/* 
	Polyfills
*/
//Closest() method
if (!Element.prototype.matches) {
    Element.prototype.matches = Element.prototype.msMatchesSelector || Element.prototype.webkitMatchesSelector;
}

if (!Element.prototype.closest) {
    Element.prototype.closest = function (s) {
        var el = this;
        if (!document.documentElement.contains(el)) return null;
        do {
            if (el.matches(s)) return el;
            el = el.parentElement || el.parentNode;
        } while (el !== null && el.nodeType === 1);
        return null;
    };
}

//Custom Event() constructor
if (typeof window.CustomEvent !== "function") {

    function CustomEvent(event, params) {
        params = params || {bubbles: false, cancelable: false, detail: undefined};
        var evt = document.createEvent('CustomEvent');
        evt.initCustomEvent(event, params.bubbles, params.cancelable, params.detail);
        return evt;
    }

    CustomEvent.prototype = window.Event.prototype;

    window.CustomEvent = CustomEvent;
}

/* 
	Animation curves
*/
Math.easeInOutQuad = function (t, b, c, d) {
    t /= d / 2;
    if (t < 1) return c / 2 * t * t + b;
    t--;
    return -c / 2 * (t * (t - 2) - 1) + b;
};

Math.easeInQuart = function (t, b, c, d) {
    t /= d;
    return c * t * t * t * t + b;
};

Math.easeOutQuart = function (t, b, c, d) {
    t /= d;
    t--;
    return -c * (t * t * t * t - 1) + b;
};

Math.easeInOutQuart = function (t, b, c, d) {
    t /= d / 2;
    if (t < 1) return c / 2 * t * t * t * t + b;
    t -= 2;
    return -c / 2 * (t * t * t * t - 2) + b;
};

Math.easeOutElastic = function (t, b, c, d) {
    var s = 1.70158;
    var p = d * 0.7;
    var a = c;
    if (t == 0) return b;
    if ((t /= d) == 1) return b + c;
    if (!p) p = d * .3;
    if (a < Math.abs(c)) {
        a = c;
        var s = p / 4;
    } else var s = p / (2 * Math.PI) * Math.asin(c / a);
    return a * Math.pow(2, -10 * t) * Math.sin((t * d - s) * (2 * Math.PI) / p) + c + b;
};


/* JS Utility Classes */
(function () {
    // make focus ring visible only for keyboard navigation (i.e., tab key)
    var focusTab = document.getElementsByClassName('js-tab-focus');

    function detectClick() {
        if (focusTab.length > 0) {
            resetFocusTabs(false);
            window.addEventListener('keydown', detectTab);
        }
        window.removeEventListener('mousedown', detectClick);
    };

    function detectTab(event) {
        if (event.keyCode !== 9) return;
        resetFocusTabs(true);
        window.removeEventListener('keydown', detectTab);
        window.addEventListener('mousedown', detectClick);
    };

    function resetFocusTabs(bool) {
        var outlineStyle = bool ? '' : 'none';
        for (var i = 0; i < focusTab.length; i++) {
            focusTab[i].style.setProperty('outline', outlineStyle);
        }
    };
    window.addEventListener('mousedown', detectClick);
}());


// File#: _1_off-canvas-content
// Usage: codyhouse.co/license
(function () {
    var OffCanvas = function (element) {
        this.element = element;
        this.wrapper = document.getElementsByClassName('js-off-canvas')[0];
        this.main = document.getElementsByClassName('off-canvas__main')[0];
        this.triggers = document.querySelectorAll('[aria-controls="' + this.element.getAttribute('id') + '"]');
        this.closeBtn = this.element.getElementsByClassName('js-off-canvas__close-btn');
        this.selectedTrigger = false;
        this.firstFocusable = null;
        this.lastFocusable = null;
        this.animating = false;
        initOffCanvas(this);
    };

    function initOffCanvas(panel) {
        panel.element.setAttribute('aria-hidden', 'true');
        for (var i = 0; i < panel.triggers.length; i++) { // lister to the click on off-canvas content triggers
            panel.triggers[i].addEventListener('click', function (event) {
                panel.selectedTrigger = event.currentTarget;
                event.preventDefault();
                togglePanel(panel);
            });
        }
    };

    function togglePanel(panel) {
        var status = (panel.element.getAttribute('aria-hidden') == 'true') ? 'close' : 'open';
        if (status == 'close') openPanel(panel);
        else closePanel(panel);
    };

    function openPanel(panel) {
        if (panel.animating) return; // already animating
        emitPanelEvents(panel, 'openPanel', '');
        panel.animating = true;
        panel.element.setAttribute('aria-hidden', 'false');
        Util.addClass(panel.wrapper, 'off-canvas--visible');
        getFocusableElements(panel);
        var transitionEl = panel.element;
        if (panel.closeBtn.length > 0 && !Util.hasClass(panel.closeBtn[0], 'js-off-canvas__a11y-close-btn')) transitionEl = panel.closeBtn[0];
        transitionEl.addEventListener('transitionend', function cb() {
            // wait for the end of transition to move focus and update the animating property
            panel.animating = false;
            Util.moveFocus(panel.element);
            transitionEl.removeEventListener('transitionend', cb);
        });
        if (!transitionSupported) panel.animating = false;
        initPanelEvents(panel);
    };

    function closePanel(panel, bool) {
        if (panel.animating) return;
        panel.animating = true;
        panel.element.setAttribute('aria-hidden', 'true');
        Util.removeClass(panel.wrapper, 'off-canvas--visible');
        panel.main.addEventListener('transitionend', function cb() {
            panel.animating = false;
            if (panel.selectedTrigger) panel.selectedTrigger.focus();
            setTimeout(function () {
                panel.selectedTrigger = false;
            }, 10);
            panel.main.removeEventListener('transitionend', cb);
        });
        if (!transitionSupported) panel.animating = false;
        cancelPanelEvents(panel);
        emitPanelEvents(panel, 'closePanel', bool);
    };

    function initPanelEvents(panel) { //add event listeners
        panel.element.addEventListener('keydown', handleEvent.bind(panel));
        panel.element.addEventListener('click', handleEvent.bind(panel));
    };

    function cancelPanelEvents(panel) { //remove event listeners
        panel.element.removeEventListener('keydown', handleEvent.bind(panel));
        panel.element.removeEventListener('click', handleEvent.bind(panel));
    };

    function handleEvent(event) {
        switch (event.type) {
            case 'keydown':
                initKeyDown(this, event);
                break;
            case 'click':
                initClick(this, event);
                break;
        }
    };

    function initClick(panel, event) { // close panel when clicking on close button
        if (!event.target.closest('.js-off-canvas__close-btn')) return;
        event.preventDefault();
        closePanel(panel, 'close-btn');
    };

    function initKeyDown(panel, event) {
        if (event.keyCode && event.keyCode == 27 || event.key && event.key == 'Escape') {
            //close off-canvas panel on esc
            closePanel(panel, 'key');
        } else if (event.keyCode && event.keyCode == 9 || event.key && event.key == 'Tab') {
            //trap focus inside panel
            trapFocus(panel, event);
        }
    };

    function trapFocus(panel, event) {
        if (panel.firstFocusable == document.activeElement && event.shiftKey) {
            //on Shift+Tab -> focus last focusable element when focus moves out of panel
            event.preventDefault();
            panel.lastFocusable.focus();
        }
        if (panel.lastFocusable == document.activeElement && !event.shiftKey) {
            //on Tab -> focus first focusable element when focus moves out of panel
            event.preventDefault();
            panel.firstFocusable.focus();
        }
    };

    function getFocusableElements(panel) { //get all focusable elements inside the off-canvas content
        var allFocusable = panel.element.querySelectorAll('[href], input:not([disabled]), select:not([disabled]), textarea:not([disabled]), button:not([disabled]), iframe, object, embed, [tabindex]:not([tabindex="-1"]), [contenteditable], audio[controls], video[controls], summary');
        getFirstVisible(panel, allFocusable);
        getLastVisible(panel, allFocusable);
    };

    function getFirstVisible(panel, elements) { //get first visible focusable element inside the off-canvas content
        for (var i = 0; i < elements.length; i++) {
            if (elements[i].offsetWidth || elements[i].offsetHeight || elements[i].getClientRects().length) {
                panel.firstFocusable = elements[i];
                return true;
            }
        }
    };

    function getLastVisible(panel, elements) { //get last visible focusable element inside the off-canvas content
        for (var i = elements.length - 1; i >= 0; i--) {
            if (elements[i].offsetWidth || elements[i].offsetHeight || elements[i].getClientRects().length) {
                panel.lastFocusable = elements[i];
                return true;
            }
        }
    };

    function emitPanelEvents(panel, eventName, target) { // emit custom event
        var event = new CustomEvent(eventName, {detail: target});
        panel.element.dispatchEvent(event);
    };

    //initialize the OffCanvas objects
    var offCanvas = document.getElementsByClassName('js-off-canvas__panel'),
        transitionSupported = Util.cssSupports('transition');
    if (offCanvas.length > 0) {
        for (var i = 0; i < offCanvas.length; i++) {
            (function (i) {
                new OffCanvas(offCanvas[i]);
            })(i);
        }
    }
}());


// File#: _1_language-picker
// Usage: codyhouse.co/license
(function () {
    var LanguagePicker = function (element) {
        this.element = element;
        this.select = this.element.getElementsByTagName('select')[0];
        this.options = this.select.getElementsByTagName('option');
        this.selectedOption = getSelectedOptionText(this);
        this.pickerId = this.select.getAttribute('id');
        this.trigger = false;
        this.dropdown = false;
        this.firstLanguage = false;
        // dropdown arrow inside the button element
        this.arrowSvgPath = '<svg viewBox="0 0 16 16"><polygon points="3,5 8,11 13,5 "></polygon></svg>';
        this.globeSvgPath = '<svg viewBox="0 0 16 16"><path d="M8,0C3.6,0,0,3.6,0,8s3.6,8,8,8s8-3.6,8-8S12.4,0,8,0z M13.9,7H12c-0.1-1.5-0.4-2.9-0.8-4.1 C12.6,3.8,13.6,5.3,13.9,7z M8,14c-0.6,0-1.8-1.9-2-5H10C9.8,12.1,8.6,14,8,14z M6,7c0.2-3.1,1.3-5,2-5s1.8,1.9,2,5H6z M4.9,2.9 C4.4,4.1,4.1,5.5,4,7H2.1C2.4,5.3,3.4,3.8,4.9,2.9z M2.1,9H4c0.1,1.5,0.4,2.9,0.8,4.1C3.4,12.2,2.4,10.7,2.1,9z M11.1,13.1 c0.5-1.2,0.7-2.6,0.8-4.1h1.9C13.6,10.7,12.6,12.2,11.1,13.1z"></path></svg>';

        initLanguagePicker(this);
        initLanguagePickerEvents(this);
    };

    function initLanguagePicker(picker) {
        // create the HTML for the custom dropdown element
        picker.element.insertAdjacentHTML('beforeend', initButtonPicker(picker) + initListPicker(picker));

        // save picker elements
        picker.dropdown = picker.element.getElementsByClassName('language-picker__dropdown')[0];
        picker.languages = picker.dropdown.getElementsByClassName('language-picker__item');
        picker.firstLanguage = picker.languages[0];
        picker.trigger = picker.element.getElementsByClassName('language-picker__button')[0];
    };

    function initLanguagePickerEvents(picker) {
        // make sure to add the icon class to the arrow dropdown inside the button element
        var svgs = picker.trigger.getElementsByTagName('svg');
        Util.addClass(svgs[0], 'icon');
        Util.addClass(svgs[1], 'icon');
        // language selection in dropdown
        // ⚠️ Important: you need to modify this function in production
        initLanguageSelection(picker);

        // click events
        picker.trigger.addEventListener('click', function () {
            toggleLanguagePicker(picker, false);
        });
        // keyboard navigation
        picker.dropdown.addEventListener('keydown', function (event) {
            if (event.keyCode && event.keyCode == 38 || event.key && event.key.toLowerCase() == 'arrowup') {
                keyboardNavigatePicker(picker, 'prev');
            } else if (event.keyCode && event.keyCode == 40 || event.key && event.key.toLowerCase() == 'arrowdown') {
                keyboardNavigatePicker(picker, 'next');
            }
        });
    };

    function toggleLanguagePicker(picker, bool) {
        var ariaExpanded;
        if (bool) {
            ariaExpanded = bool;
        } else {
            ariaExpanded = picker.trigger.getAttribute('aria-expanded') == 'true' ? 'false' : 'true';
        }
        picker.trigger.setAttribute('aria-expanded', ariaExpanded);
        if (ariaExpanded == 'true') {
            picker.firstLanguage.focus(); // fallback if transition is not supported
            picker.dropdown.addEventListener('transitionend', function cb() {
                picker.firstLanguage.focus();
                picker.dropdown.removeEventListener('transitionend', cb);
            });
            // place dropdown
            placeDropdown(picker);
        }
    };

    function placeDropdown(picker) {
        var triggerBoundingRect = picker.trigger.getBoundingClientRect();
        Util.toggleClass(picker.dropdown, 'language-picker__dropdown--right', (window.innerWidth < triggerBoundingRect.left + picker.dropdown.offsetWidth));
        Util.toggleClass(picker.dropdown, 'language-picker__dropdown--up', (window.innerHeight < triggerBoundingRect.bottom + picker.dropdown.offsetHeight));
    };

    function checkLanguagePickerClick(picker, target) { // if user clicks outside the language picker -> close it
        if (!picker.element.contains(target)) toggleLanguagePicker(picker, 'false');
    };

    function moveFocusToPickerTrigger(picker) {
        if (picker.trigger.getAttribute('aria-expanded') == 'false') return;
        if (document.activeElement.closest('.language-picker__dropdown') == picker.dropdown) picker.trigger.focus();
    };

    function initButtonPicker(picker) { // create the button element -> picker trigger
        // check if we need to add custom classes to the button trigger
        var customClasses = picker.element.getAttribute('data-trigger-class') ? ' ' + picker.element.getAttribute('data-trigger-class') : '';

        var button = '<button class="language-picker__button' + customClasses + '" aria-label="' + picker.select.value + ' ' + picker.element.getElementsByTagName('label')[0].textContent + '" aria-expanded="false" aria-controls="' + picker.pickerId + '-dropdown">';
        button = button + '<span aria-hidden="true" class="language-picker__label language-picker__flag language-picker__flag--' + picker.select.value + '">' + picker.globeSvgPath + '<em>' + picker.selectedOption + '</em>';
        button = button + picker.arrowSvgPath + '</span>';
        return button + '</button>';
    };

    function initListPicker(picker) { // create language picker dropdown
        var list = '<div class="language-picker__dropdown" aria-describedby="' + picker.pickerId + '-description" id="' + picker.pickerId + '-dropdown">';
        list = list + '<p class="sr-only" id="' + picker.pickerId + '-description">' + picker.element.getElementsByTagName('label')[0].textContent + '</p>';
        list = list + '<ul class="language-picker__list" role="listbox">';
        for (var i = 0; i < picker.options.length; i++) {
            var selected = picker.options[i].selected ? ' aria-selected="true"' : '',
                language = picker.options[i].getAttribute('lang');
            list = list + '<li><a lang="' + language + '" hreflang="' + language + '" href="' + getLanguageUrl(picker.options[i]) + '"' + selected + ' role="option" data-value="' + picker.options[i].value + '" class="language-picker__item language-picker__flag language-picker__flag--' + picker.options[i].value + '"><span>' + picker.options[i].text + '</span></a></li>';
        }
        ;
        return list;
    };

    function getSelectedOptionText(picker) { // used to initialize the label of the picker trigger button
        var label = '';
        if ('selectedIndex' in picker.select) {
            label = picker.options[picker.select.selectedIndex].text;
        } else {
            label = picker.select.querySelector('option[selected]').text;
        }
        return label;
    };

    function getLanguageUrl(option) {
        // ⚠️ Important: You should replace this return value with the real link to your website in the selected language
        // option.value gives you the value of the language that you can use to create your real url (e.g, 'english' or 'italiano')
        return '#';
    };

    function initLanguageSelection(picker) {
        picker.element.getElementsByClassName('language-picker__list')[0].addEventListener('click', function (event) {
            var language = event.target.closest('.language-picker__item');
            if (!language) return;

            if (language.hasAttribute('aria-selected') && language.getAttribute('aria-selected') == 'true') {
                // selecting the same language
                event.preventDefault();
                picker.trigger.setAttribute('aria-expanded', 'false'); // hide dropdown
            } else {
                // ⚠️ Important: this 'else' code needs to be removed in production.
                // The user has to be redirected to the new url -> nothing to do here
                event.preventDefault();
                picker.element.getElementsByClassName('language-picker__list')[0].querySelector('[aria-selected="true"]').removeAttribute('aria-selected');
                language.setAttribute('aria-selected', 'true');
                picker.trigger.getElementsByClassName('language-picker__label')[0].setAttribute('class', 'language-picker__label language-picker__flag language-picker__flag--' + language.getAttribute('data-value'));
                picker.trigger.getElementsByClassName('language-picker__label')[0].getElementsByTagName('em')[0].textContent = language.textContent;
                picker.trigger.setAttribute('aria-expanded', 'false');
            }
        });
    };

    function keyboardNavigatePicker(picker, direction) {
        var index = Util.getIndexInArray(picker.languages, document.activeElement);
        index = (direction == 'next') ? index + 1 : index - 1;
        if (index < 0) index = picker.languages.length - 1;
        if (index >= picker.languages.length) index = 0;
        Util.moveFocus(picker.languages[index]);
    };

    //initialize the LanguagePicker objects
    var languagePicker = document.getElementsByClassName('js-language-picker');
    if (languagePicker.length > 0) {
        var pickerArray = [];
        for (var i = 0; i < languagePicker.length; i++) {
            (function (i) {
                pickerArray.push(new LanguagePicker(languagePicker[i]));
            })(i);
        }

        // listen for key events
        window.addEventListener('keyup', function (event) {
            if (event.keyCode && event.keyCode == 27 || event.key && event.key.toLowerCase() == 'escape') {
                // close language picker on 'Esc'
                pickerArray.forEach(function (element) {
                    moveFocusToPickerTrigger(element); // if focus is within dropdown, move it to dropdown trigger
                    toggleLanguagePicker(element, 'false'); // close dropdown
                });
            }
        });
        // close language picker when clicking outside it
        window.addEventListener('click', function (event) {
            pickerArray.forEach(function (element) {
                checkLanguagePickerClick(element, event.target);
            });
        });
    }
}());

//
// // File#: _1_diagonal-movement
// // Usage: codyhouse.co/license
// /*
//   Modified version of the jQuery-menu-aim plugin
//   https://github.com/kamens/jQuery-menu-aim
//   - Replaced jQuery with Vanilla JS
//   - Minor changes
// */
// (function () {
//     var menuAim = function (opts) {
//         init(opts);
//     };
//
//     window.menuAim = menuAim;
//
//     function init(opts) {
//         var activeRow = null,
//             mouseLocs = [],
//             lastDelayLoc = null,
//             timeoutId = null,
//             options = Util.extend({
//                 menu: '',
//                 rows: false, //if false, get direct children - otherwise pass nodes list
//                 submenuSelector: "*",
//                 submenuDirection: "right",
//                 tolerance: 75,  // bigger = more forgivey when entering submenu
//                 enter: function () {
//                 },
//                 exit: function () {
//                 },
//                 activate: function () {
//                 },
//                 deactivate: function () {
//                 },
//                 exitMenu: function () {
//                 }
//             }, opts),
//             menu = options.menu;
//
//         var MOUSE_LOCS_TRACKED = 3,  // number of past mouse locations to track
//             DELAY = 300;  // ms delay when user appears to be entering submenu
//
//         /**
//          * Keep track of the last few locations of the mouse.
//          */
//         var mousemoveDocument = function (e) {
//             mouseLocs.push({x: e.pageX, y: e.pageY});
//
//             if (mouseLocs.length > MOUSE_LOCS_TRACKED) {
//                 mouseLocs.shift();
//             }
//         };
//
//         /**
//          * Cancel possible row activations when leaving the menu entirely
//          */
//         var mouseleaveMenu = function () {
//             if (timeoutId) {
//                 clearTimeout(timeoutId);
//             }
//
//             // If exitMenu is supplied and returns true, deactivate the
//             // currently active row on menu exit.
//             if (options.exitMenu(this)) {
//                 if (activeRow) {
//                     options.deactivate(activeRow);
//                 }
//
//                 activeRow = null;
//             }
//         };
//
//         /**
//          * Trigger a possible row activation whenever entering a new row.
//          */
//         var mouseenterRow = function () {
//                 if (timeoutId) {
//                     // Cancel any previous activation delays
//                     clearTimeout(timeoutId);
//                 }
//
//                 options.enter(this);
//                 possiblyActivate(this);
//             },
//             mouseleaveRow = function () {
//                 options.exit(this);
//             };
//
//         /*
//          * Immediately activate a row if the user clicks on it.
//          */
//         var clickRow = function () {
//             activate(this);
//         };
//
//         /**
//          * Activate a menu row.
//          */
//         var activate = function (row) {
//             if (row == activeRow) {
//                 return;
//             }
//
//             if (activeRow) {
//                 options.deactivate(activeRow);
//             }
//
//             options.activate(row);
//             activeRow = row;
//         };
//
//         /**
//          * Possibly activate a menu row. If mouse movement indicates that we
//          * shouldn't activate yet because user may be trying to enter
//          * a submenu's content, then delay and check again later.
//          */
//         var possiblyActivate = function (row) {
//             var delay = activationDelay();
//
//             if (delay) {
//                 timeoutId = setTimeout(function () {
//                     possiblyActivate(row);
//                 }, delay);
//             } else {
//                 activate(row);
//             }
//         };
//
//         /**
//          * Return the amount of time that should be used as a delay before the
//          * currently hovered row is activated.
//          *
//          * Returns 0 if the activation should happen immediately. Otherwise,
//          * returns the number of milliseconds that should be delayed before
//          * checking again to see if the row should be activated.
//          */
//         var activationDelay = function () {
//             if (!activeRow || !Util.is(activeRow, options.submenuSelector)) {
//                 // If there is no other submenu row already active, then
//                 // go ahead and activate immediately.
//                 return 0;
//             }
//
//             function getOffset(element) {
//                 var rect = element.getBoundingClientRect();
//                 return {top: rect.top + window.pageYOffset, left: rect.left + window.pageXOffset};
//             };
//
//             var offset = getOffset(menu),
//                 upperLeft = {
//                     x: offset.left,
//                     y: offset.top - options.tolerance
//                 },
//                 upperRight = {
//                     x: offset.left + menu.offsetWidth,
//                     y: upperLeft.y
//                 },
//                 lowerLeft = {
//                     x: offset.left,
//                     y: offset.top + menu.offsetHeight + options.tolerance
//                 },
//                 lowerRight = {
//                     x: offset.left + menu.offsetWidth,
//                     y: lowerLeft.y
//                 },
//                 loc = mouseLocs[mouseLocs.length - 1],
//                 prevLoc = mouseLocs[0];
//
//             if (!loc) {
//                 return 0;
//             }
//
//             if (!prevLoc) {
//                 prevLoc = loc;
//             }
//
//             if (prevLoc.x < offset.left || prevLoc.x > lowerRight.x || prevLoc.y < offset.top || prevLoc.y > lowerRight.y) {
//                 // If the previous mouse location was outside of the entire
//                 // menu's bounds, immediately activate.
//                 return 0;
//             }
//
//             if (lastDelayLoc && loc.x == lastDelayLoc.x && loc.y == lastDelayLoc.y) {
//                 // If the mouse hasn't moved since the last time we checked
//                 // for activation status, immediately activate.
//                 return 0;
//             }
//
//             // Detect if the user is moving towards the currently activated
//             // submenu.
//             //
//             // If the mouse is heading relatively clearly towards
//             // the submenu's content, we should wait and give the user more
//             // time before activating a new row. If the mouse is heading
//             // elsewhere, we can immediately activate a new row.
//             //
//             // We detect this by calculating the slope formed between the
//             // current mouse location and the upper/lower right points of
//             // the menu. We do the same for the previous mouse location.
//             // If the current mouse location's slopes are
//             // increasing/decreasing appropriately compared to the
//             // previous's, we know the user is moving toward the submenu.
//             //
//             // Note that since the y-axis increases as the cursor moves
//             // down the screen, we are looking for the slope between the
//             // cursor and the upper right corner to decrease over time, not
//             // increase (somewhat counterintuitively).
//             function slope(a, b) {
//                 return (b.y - a.y) / (b.x - a.x);
//             };
//
//             var decreasingCorner = upperRight,
//                 increasingCorner = lowerRight;
//
//             // Our expectations for decreasing or increasing slope values
//             // depends on which direction the submenu opens relative to the
//             // main menu. By default, if the menu opens on the right, we
//             // expect the slope between the cursor and the upper right
//             // corner to decrease over time, as explained above. If the
//             // submenu opens in a different direction, we change our slope
//             // expectations.
//             if (options.submenuDirection == "left") {
//                 decreasingCorner = lowerLeft;
//                 increasingCorner = upperLeft;
//             } else if (options.submenuDirection == "below") {
//                 decreasingCorner = lowerRight;
//                 increasingCorner = lowerLeft;
//             } else if (options.submenuDirection == "above") {
//                 decreasingCorner = upperLeft;
//                 increasingCorner = upperRight;
//             }
//
//             var decreasingSlope = slope(loc, decreasingCorner),
//                 increasingSlope = slope(loc, increasingCorner),
//                 prevDecreasingSlope = slope(prevLoc, decreasingCorner),
//                 prevIncreasingSlope = slope(prevLoc, increasingCorner);
//
//             if (decreasingSlope < prevDecreasingSlope && increasingSlope > prevIncreasingSlope) {
//                 // Mouse is moving from previous location towards the
//                 // currently activated submenu. Delay before activating a
//                 // new menu row, because user may be moving into submenu.
//                 lastDelayLoc = loc;
//                 return DELAY;
//             }
//
//             lastDelayLoc = null;
//             return 0;
//         };
//
//         /**
//          * Hook up initial menu events
//          */
//         menu.addEventListener('mouseleave', mouseleaveMenu);
//         var rows = (options.rows) ? options.rows : menu.children;
//         if (rows.length > 0) {
//             for (var i = 0; i < rows.length; i++) {
//                 (function (i) {
//                     rows[i].addEventListener('mouseenter', mouseenterRow);
//                     rows[i].addEventListener('mouseleave', mouseleaveRow);
//                     rows[i].addEventListener('click', clickRow);
//                 })(i);
//             }
//         }
//
//         document.addEventListener('mousemove', function (event) {
//             (!window.requestAnimationFrame) ? mousemoveDocument(event) : window.requestAnimationFrame(function () {
//                 mousemoveDocument(event);
//             });
//         });
//     };
// }());

// File#: _2_dropdown
// Usage: codyhouse.co/license
(function () {
    var Dropdown = function (element) {
        this.element = element;
        this.trigger = this.element.getElementsByClassName('dropdown__trigger')[0];
        this.dropdown = this.element.getElementsByClassName('dropdown__menu')[0];
        this.triggerFocus = false;
        this.dropdownFocus = false;
        this.hideInterval = false;
        // sublevels
        this.dropdownSubElements = this.element.getElementsByClassName('dropdown__sub-wrapperu');
        this.prevFocus = false; // store element that was in focus before focus changed
        this.addDropdownEvents();
    };

    Dropdown.prototype.addDropdownEvents = function () {
        //place dropdown
        var self = this;
        this.placeElement();
        this.element.addEventListener('placeDropdown', function (event) {
            self.placeElement();
        });
        // init dropdown
        this.initElementEvents(this.trigger, this.triggerFocus); // this is used to trigger the primary dropdown
        this.initElementEvents(this.dropdown, this.dropdownFocus); // this is used to trigger the primary dropdown
        // init sublevels
        this.initSublevels(); // if there are additional sublevels -> bind hover/focus events
    };

    Dropdown.prototype.placeElement = function () {
        var triggerPosition = this.trigger.getBoundingClientRect(),
            isRight = (window.innerWidth < triggerPosition.left + parseInt(getComputedStyle(this.dropdown).getPropertyValue('width')));

        var xPosition = isRight ? 'right: 0px; left: auto;' : 'left: 0px; right: auto;';
        this.dropdown.setAttribute('style', xPosition);
    };

    Dropdown.prototype.initElementEvents = function (element, bool) {
        var self = this;
        element.addEventListener('mouseenter', function () {
            bool = true;
            self.showDropdown();
        });
        element.addEventListener('focus', function () {
            self.showDropdown();
        });
        element.addEventListener('mouseleave', function () {
            bool = false;
            self.hideDropdown();
        });
        element.addEventListener('focusout', function () {
            self.hideDropdown();
        });
    };

    Dropdown.prototype.showDropdown = function () {
        if (this.hideInterval) clearInterval(this.hideInterval);
        this.showLevel(this.dropdown, true);
    };

    Dropdown.prototype.hideDropdown = function () {
        var self = this;
        if (this.hideInterval) clearInterval(this.hideInterval);
        this.hideInterval = setTimeout(function () {
            var dropDownFocus = document.activeElement.closest('.js-dropdown'),
                inFocus = dropDownFocus && (dropDownFocus == self.element);
            // if not in focus and not hover -> hide
            if (!self.triggerFocus && !self.dropdownFocus && !inFocus) {
                self.hideLevel(self.dropdown);
                // make sure to hide sub/dropdown
                self.hideSubLevels();
                self.prevFocus = false;
            }
        }, 300);
    };

    Dropdown.prototype.initSublevels = function () {
        var self = this;
        var dropdownMenu = this.element.getElementsByClassName('dropdown__menu');
        for (var i = 0; i < dropdownMenu.length; i++) {
            var listItems = dropdownMenu[i].children;
            // bind hover
            new menuAim({
                menu: dropdownMenu[i],
                activate: function (row) {
                    var subList = row.getElementsByClassName('dropdown__menu')[0];
                    if (!subList) return;
                    Util.addClass(row.querySelector('a'), 'dropdown__item--hover');
                    self.showLevel(subList);
                },
                deactivate: function (row) {
                    var subList = row.getElementsByClassName('dropdown__menu')[0];
                    if (!subList) return;
                    Util.removeClass(row.querySelector('a'), 'dropdown__item--hover');
                    self.hideLevel(subList);
                },
                submenuSelector: '.dropdown__sub-wrapper',
            });
        }
        // store focus element before change in focus
        this.element.addEventListener('keydown', function (event) {
            if (event.keyCode && event.keyCode == 9 || event.key && event.key == 'Tab') {
                self.prevFocus = document.activeElement;
            }
        });
        // make sure that sublevel are visible when their items are in focus
        this.element.addEventListener('keyup', function (event) {
            if (event.keyCode && event.keyCode == 9 || event.key && event.key == 'Tab') {
                // focus has been moved -> make sure the proper classes are added to subnavigation
                var focusElement = document.activeElement,
                    focusElementParent = focusElement.closest('.dropdown__menu'),
                    focusElementSibling = focusElement.nextElementSibling;

                // if item in focus is inside submenu -> make sure it is visible
                if (focusElementParent && !Util.hasClass(focusElementParent, 'dropdown__menu--is-visible')) {
                    self.showLevel(focusElementParent);
                }
                // if item in focus triggers a submenu -> make sure it is visible
                if (focusElementSibling && !Util.hasClass(focusElementSibling, 'dropdown__menu--is-visible')) {
                    self.showLevel(focusElementSibling);
                }

                // check previous element in focus -> hide sublevel if required
                if (!self.prevFocus) return;
                var prevFocusElementParent = self.prevFocus.closest('.dropdown__menu'),
                    prevFocusElementSibling = self.prevFocus.nextElementSibling;

                if (!prevFocusElementParent) return;

                // element in focus and element prev in focus are siblings
                if (focusElementParent && focusElementParent == prevFocusElementParent) {
                    if (prevFocusElementSibling) self.hideLevel(prevFocusElementSibling);
                    return;
                }

                // element in focus is inside submenu triggered by element prev in focus
                if (prevFocusElementSibling && focusElementParent && focusElementParent == prevFocusElementSibling) return;

                // shift tab -> element in focus triggers the submenu of the element prev in focus
                if (focusElementSibling && prevFocusElementParent && focusElementSibling == prevFocusElementParent) return;

                var focusElementParentParent = focusElementParent.parentNode.closest('.dropdown__menu');

                // shift tab -> element in focus is inside the dropdown triggered by a siblings of the element prev in focus
                if (focusElementParentParent && focusElementParentParent == prevFocusElementParent) {
                    if (prevFocusElementSibling) self.hideLevel(prevFocusElementSibling);
                    return;
                }

                if (prevFocusElementParent && Util.hasClass(prevFocusElementParent, 'dropdown__menu--is-visible')) {
                    self.hideLevel(prevFocusElementParent);
                }
            }
        });
    };

    Dropdown.prototype.hideSubLevels = function () {
        var visibleSubLevels = this.dropdown.getElementsByClassName('dropdown__menu--is-visible');
        if (visibleSubLevels.length == 0) return;
        while (visibleSubLevels[0]) {
            this.hideLevel(visibleSubLevels[0]);
        }
        var hoveredItems = this.dropdown.getElementsByClassName('dropdown__item--hover');
        while (hoveredItems[0]) {
            Util.removeClass(hoveredItems[0], 'dropdown__item--hover');
        }
    };

    Dropdown.prototype.showLevel = function (level, bool) {
        if (bool == undefined) {
            //check if the sublevel needs to be open to the left
            Util.removeClass(level, 'dropdown__menu--left');
            var boundingRect = level.getBoundingClientRect();
            if (window.innerWidth - boundingRect.right < 5 && boundingRect.left + window.scrollX > 2 * boundingRect.width) Util.addClass(level, 'dropdown__menu--left');
        }
        Util.addClass(level, 'dropdown__menu--is-visible');
        Util.removeClass(level, 'dropdown__menu--is-hidden');
    };

    Dropdown.prototype.hideLevel = function (level) {
        if (!Util.hasClass(level, 'dropdown__menu--is-visible')) return;
        Util.removeClass(level, 'dropdown__menu--is-visible');
        Util.addClass(level, 'dropdown__menu--is-hidden');

        level.addEventListener('animationend', function cb() {
            level.removeEventListener('animationend', cb);
            Util.removeClass(level, 'dropdown__menu--is-hidden dropdown__menu--left');
        });
    };


    var dropdown = document.getElementsByClassName('js-dropdown');
    if (dropdown.length > 0) { // init Dropdown objects
        for (var i = 0; i < dropdown.length; i++) {
            (function (i) {
                new Dropdown(dropdown[i]);
            })(i);
        }
    }
}());