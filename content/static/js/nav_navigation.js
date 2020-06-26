// File#: _1_filter-navigation
// Usage: codyhouse.co/license
(function () {
    var FilterNav = function (element) {
        this.element = element;
        this.wrapper = this.element.getElementsByClassName('js-filter-nav__wrapper')[0];
        this.nav = this.element.getElementsByClassName('js-filter-nav__nav')[0];
        this.list = this.nav.getElementsByClassName('js-filter-nav__list')[0];
        this.control = this.element.getElementsByClassName('js-filter-nav__control')[0];
        this.modalClose = this.element.getElementsByClassName('js-filter-nav__close-btn')[0];
        this.placeholder = this.element.getElementsByClassName('js-filter-nav__placeholder')[0];
        this.marker = this.element.getElementsByClassName('js-filter-nav__marker');
        this.layout = 'expanded';
        initFilterNav(this);
    };

    function initFilterNav(element) {
        checkLayout(element); // init layout
        if (element.layout == 'expanded') placeMarker(element);
        element.element.addEventListener('update-layout', function (event) { // on resize - modify layout
            checkLayout(element);
        });

        // update selected item
        element.wrapper.addEventListener('click', function (event) {
            var newItem = event.target.closest('.js-filter-nav__btn');
            if (newItem) {
                updateCurrentItem(element, newItem);
                return;
            }
            // close modal list - mobile version only
            if (Util.hasClass(event.target, 'js-filter-nav__wrapper') || event.target.closest('.js-filter-nav__close-btn')) toggleModalList(element, false);
        });

        // open modal list - mobile version only
        element.control.addEventListener('click', function (event) {
            toggleModalList(element, true);
        });

        // listen for key events
        window.addEventListener('keyup', function (event) {
            // listen for esc key
            if ((event.keyCode && event.keyCode == 27) || (event.key && event.key.toLowerCase() == 'escape')) {
                // close navigation on mobile if open
                if (element.control.getAttribute('aria-expanded') == 'true' && isVisible(element.control)) {
                    toggleModalList(element, false);
                }
            }
            // listen for tab key
            if ((event.keyCode && event.keyCode == 9) || (event.key && event.key.toLowerCase() == 'tab')) {
                // close navigation on mobile if open when nav loses focus
                if (element.control.getAttribute('aria-expanded') == 'true' && isVisible(element.control) && !document.activeElement.closest('.js-filter-nav__wrapper')) toggleModalList(element, false);
            }
        });
    };

    function updateCurrentItem(element, btn) {
        if (btn.getAttribute('aria-current') == 'true') {
            toggleModalList(element, false);
            return;
        }
        var activeBtn = element.wrapper.querySelector('[aria-current]');
        if (activeBtn) activeBtn.removeAttribute('aria-current');
        btn.setAttribute('aria-current', 'true');
        // update trigger label on selection (visible on mobile only)
        element.placeholder.textContent = btn.textContent;
        toggleModalList(element, false);
        if (element.layout == 'expanded') placeMarker(element);
    };

    function toggleModalList(element, bool) {
        element.control.setAttribute('aria-expanded', bool);
        Util.toggleClass(element.wrapper, 'filter-nav__wrapper--is-visible', bool);
        if (bool) {
            element.nav.querySelectorAll('[href], button:not([disabled])')[0].focus();
        } else if (isVisible(element.control)) {
            element.control.focus();
        }
    };

    function isVisible(element) {
        return (element.offsetWidth || element.offsetHeight || element.getClientRects().length);
    };

    function checkLayout(element) {
        if (element.layout == 'expanded' && switchToCollapsed(element)) { // check if there's enough space
            element.layout = 'collapsed';
            Util.removeClass(element.element, 'filter-nav--expanded');
            Util.addClass(element.element, 'filter-nav--collapsed');
            Util.removeClass(element.modalClose, 'is-hidden');
            Util.removeClass(element.control, 'is-hidden');
        } else if (element.layout == 'collapsed' && switchToExpanded(element)) {
            element.layout = 'expanded';
            Util.addClass(element.element, 'filter-nav--expanded');
            Util.removeClass(element.element, 'filter-nav--collapsed');
            Util.addClass(element.modalClose, 'is-hidden');
            Util.addClass(element.control, 'is-hidden');
        }
        // place background element
        if (element.layout == 'expanded') placeMarker(element);
    };

    function switchToCollapsed(element) {
        return element.nav.scrollWidth > element.nav.offsetWidth;
    };

    function switchToExpanded(element) {
        element.element.style.visibility = 'hidden';
        Util.addClass(element.element, 'filter-nav--expanded');
        Util.removeClass(element.element, 'filter-nav--collapsed');
        var switchLayout = element.nav.scrollWidth <= element.nav.offsetWidth;
        Util.removeClass(element.element, 'filter-nav--expanded');
        Util.addClass(element.element, 'filter-nav--collapsed');
        element.element.style.visibility = 'visible';
        return switchLayout;
    };

    function placeMarker(element) {
        var activeElement = element.wrapper.querySelector('.js-filter-nav__btn[aria-current="true"]');
        if (element.marker.length == 0 || !activeElement) return;
        element.marker[0].style.width = activeElement.offsetWidth + 'px';
        element.marker[0].style.transform = 'translateX(' + (activeElement.getBoundingClientRect().left - element.list.getBoundingClientRect().left) + 'px)';
    };

    var filterNav = document.getElementsByClassName('js-filter-nav');
    if (filterNav.length > 0) {
        var filterNavArray = [];
        for (var i = 0; i < filterNav.length; i++) {
            filterNavArray.push(new FilterNav(filterNav[i]));
        }

        var resizingId = false,
            customEvent = new CustomEvent('update-layout');

        window.addEventListener('resize', function () {
            clearTimeout(resizingId);
            resizingId = setTimeout(doneResizing, 100);
        });

        // wait for font to be loaded
        document.fonts.onloadingdone = function (fontFaceSetEvent) {
            doneResizing();
        };

        function doneResizing() {
            for (var i = 0; i < filterNavArray.length; i++) {
                (function (i) {
                    filterNavArray[i].element.dispatchEvent(customEvent)
                })(i);
            }
            ;
        };
    }
}());


// File#: _1_header
// Usage: codyhouse.co/license
(function () {
    var mainHeader = document.getElementsByClassName('js-header');
    if (mainHeader.length > 0) {
        var trigger = mainHeader[0].getElementsByClassName('js-header__trigger')[0],
            nav = mainHeader[0].getElementsByClassName('js-header__nav')[0];

        // we'll use these to store the node that needs to receive focus when the mobile menu is closed
        var focusMenu = false;

        //detect click on nav trigger
        trigger.addEventListener("click", function (event) {
            event.preventDefault();
            toggleNavigation(!Util.hasClass(nav, 'header__nav--is-visible'));
        });

        // listen for key events
        window.addEventListener('keyup', function (event) {
            // listen for esc key
            if ((event.keyCode && event.keyCode == 27) || (event.key && event.key.toLowerCase() == 'escape')) {
                // close navigation on mobile if open
                if (trigger.getAttribute('aria-expanded') == 'true' && isVisible(trigger)) {
                    focusMenu = trigger; // move focus to menu trigger when menu is close
                    trigger.click();
                }
            }
            // listen for tab key
            if ((event.keyCode && event.keyCode == 9) || (event.key && event.key.toLowerCase() == 'tab')) {
                // close navigation on mobile if open when nav loses focus
                if (trigger.getAttribute('aria-expanded') == 'true' && isVisible(trigger) && !document.activeElement.closest('.js-header')) trigger.click();
            }
        });

        // listen for resize
        var resizingId = false;
        window.addEventListener('resize', function () {
            clearTimeout(resizingId);
            resizingId = setTimeout(doneResizing, 500);
        });

        function doneResizing() {
            if (!isVisible(trigger) && Util.hasClass(mainHeader[0], 'header--expanded')) toggleNavigation(false);
        };
    }

    function isVisible(element) {
        return (element.offsetWidth || element.offsetHeight || element.getClientRects().length);
    };

    function toggleNavigation(bool) { // toggle navigation visibility on small device
        Util.toggleClass(nav, 'header__nav--is-visible', bool);
        Util.toggleClass(mainHeader[0], 'header--expanded', bool);
        trigger.setAttribute('aria-expanded', bool);
        if (bool) { //opening menu -> move focus to first element inside nav
            nav.querySelectorAll('[href], input:not([disabled]), button:not([disabled])')[0].focus();
        } else if (focusMenu) {
            focusMenu.focus();
            focusMenu = false;
        }
    };
}());