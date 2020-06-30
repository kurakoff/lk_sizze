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


// File#: _1_responsive-sidebar
// Usage: codyhouse.co/license
(function () {
	var Sidebar = function (element) {
		this.element = element;
		this.triggers = document.querySelectorAll('[aria-controls="' + this.element.getAttribute('id') + '"]');
		this.firstFocusable = null;
		this.lastFocusable = null;
		this.selectedTrigger = null;
		this.showClass = "sidebar--is-visible";
		this.staticClass = "sidebar--static";
		this.readyClass = "sidebar--loaded";
		this.layout = false; // this will be static or mobile
		initSidebar(this);
	};

	function initSidebar(sidebar) {
		initSidebarResize(sidebar); // handle changes in layout -> mobile to static and viceversa

		if (sidebar.triggers) { // open sidebar when clicking on trigger buttons - mobile layout only
			for (var i = 0; i < sidebar.triggers.length; i++) {
				sidebar.triggers[i].addEventListener('click', function (event) {
					event.preventDefault();
					if (Util.hasClass(sidebar.element, sidebar.showClass)) return;
					sidebar.selectedTrigger = event.target;
					showSidebar(sidebar);
					initSidebarEvents(sidebar);
				});
			}
		}
	};

	function showSidebar(sidebar) { // mobile layout only
		Util.addClass(sidebar.element, sidebar.showClass);
		getFocusableElements(sidebar);
		Util.moveFocus(sidebar.element);
	};

	function closeSidebar(sidebar) { // mobile layout only
		Util.removeClass(sidebar.element, sidebar.showClass);
		sidebar.firstFocusable = null;
		sidebar.lastFocusable = null;
		if (sidebar.selectedTrigger) sidebar.selectedTrigger.focus();
		sidebar.element.removeAttribute('tabindex');
		//remove listeners
		cancelSidebarEvents(sidebar);
	};

	function initSidebarEvents(sidebar) { // mobile layout only
		//add event listeners
		sidebar.element.addEventListener('keydown', handleEvent.bind(sidebar));
		sidebar.element.addEventListener('click', handleEvent.bind(sidebar));
	};

	function cancelSidebarEvents(sidebar) { // mobile layout only
		//remove event listeners
		sidebar.element.removeEventListener('keydown', handleEvent.bind(sidebar));
		sidebar.element.removeEventListener('click', handleEvent.bind(sidebar));
	};

	function handleEvent(event) { // mobile layout only
		switch (event.type) {
			case 'click': {
				initClick(this, event);
			}
			case 'keydown': {
				initKeyDown(this, event);
			}
		}
	};

	function initKeyDown(sidebar, event) { // mobile layout only
		if (event.keyCode && event.keyCode == 27 || event.key && event.key == 'Escape') {
			//close sidebar window on esc
			closeSidebar(sidebar);
		} else if (event.keyCode && event.keyCode == 9 || event.key && event.key == 'Tab') {
			//trap focus inside sidebar
			trapFocus(sidebar, event);
		}
	};

	function initClick(sidebar, event) { // mobile layout only
		//close sidebar when clicking on close button or sidebar bg layer
		if ($(event.target).hasClass('node')) {
			closeSidebar(sidebar);
		}
		if (!event.target.closest('.js-sidebar__close-btn') && !Util.hasClass(event.target, 'js-sidebar')) return;
		event.preventDefault();
		closeSidebar(sidebar);
	};

	function trapFocus(sidebar, event) { // mobile layout only
		if (sidebar.firstFocusable == document.activeElement && event.shiftKey) {
			//on Shift+Tab -> focus last focusable element when focus moves out of sidebar
			event.preventDefault();
			sidebar.lastFocusable.focus();
		}
		if (sidebar.lastFocusable == document.activeElement && !event.shiftKey) {
			//on Tab -> focus first focusable element when focus moves out of sidebar
			event.preventDefault();
			sidebar.firstFocusable.focus();
		}
	};

	function initSidebarResize(sidebar) {
		// custom event emitted when window is resized - detect only if the sidebar--static@{breakpoint} class was added
		var beforeContent = getComputedStyle(sidebar.element, ':before').getPropertyValue('content');
		if (beforeContent && beforeContent != '' && beforeContent != 'none') {
			checkSidebarLayour(sidebar);

			sidebar.element.addEventListener('update-sidebar', function (event) {
				checkSidebarLayour(sidebar);
			});
		}
		Util.addClass(sidebar.element, sidebar.readyClass);
	};

	function checkSidebarLayour(sidebar) {
		var layout = getComputedStyle(sidebar.element, ':before').getPropertyValue('content').replace(/\'|"/g, '');
		if (layout == sidebar.layout) return;
		sidebar.layout = layout;
		if (layout != 'static') Util.addClass(sidebar.element, 'is-hidden');
		Util.toggleClass(sidebar.element, sidebar.staticClass, layout == 'static');
		if (layout != 'static') setTimeout(function () {
			Util.removeClass(sidebar.element, 'is-hidden')
		});
		// reset element role
		(layout == 'static') ? sidebar.element.removeAttribute('role', 'alertdialog') : sidebar.element.setAttribute('role', 'alertdialog');
		// reset mobile behaviour
		if (layout == 'static' && Util.hasClass(sidebar.element, sidebar.showClass)) closeSidebar(sidebar);
	};

	function getFocusableElements(sidebar) {
		//get all focusable elements inside the drawer
		var allFocusable = sidebar.element.querySelectorAll('[href], input:not([disabled]), select:not([disabled]), textarea:not([disabled]), button:not([disabled]), iframe, object, embed, [tabindex]:not([tabindex="-1"]), [contenteditable], audio[controls], video[controls], summary');
		getFirstVisible(sidebar, allFocusable);
		getLastVisible(sidebar, allFocusable);
	};

	function getFirstVisible(sidebar, elements) {
		//get first visible focusable element inside the sidebar
		for (var i = 0; i < elements.length; i++) {
			if (elements[i].offsetWidth || elements[i].offsetHeight || elements[i].getClientRects().length) {
				sidebar.firstFocusable = elements[i];
				return true;
			}
		}
	};

	function getLastVisible(sidebar, elements) {
		//get last visible focusable element inside the sidebar
		for (var i = elements.length - 1; i >= 0; i--) {
			if (elements[i].offsetWidth || elements[i].offsetHeight || elements[i].getClientRects().length) {
				sidebar.lastFocusable = elements[i];
				return true;
			}
		}
	};

	//initialize the Sidebar objects
	var sidebar = document.getElementsByClassName('js-sidebar');
	if (sidebar.length > 0) {
		for (var i = 0; i < sidebar.length; i++) {
			(function (i) {
				new Sidebar(sidebar[i]);
			})(i);
		}
		// switch from mobile to static layout
		var customEvent = new CustomEvent('update-sidebar');
		window.addEventListener('resize', function (event) {
			(!window.requestAnimationFrame) ? setTimeout(function () {
				resetLayout();
			}, 250) : window.requestAnimationFrame(resetLayout);
		});

		function resetLayout() {
			for (var i = 0; i < sidebar.length; i++) {
				(function (i) {
					sidebar[i].dispatchEvent(customEvent)
				})(i);
			}
			;
		};
	}
}());


// File#: _1_accordion
// Usage: codyhouse.co/license
(function () {
	var Accordion = function (element) {
		this.element = element;
		this.items = Util.getChildrenByClassName(this.element, 'js-accordion__item');
		this.showClass = 'accordion__item--is-open';
		this.animateHeight = (this.element.getAttribute('data-animation') == 'on');
		this.multiItems = !(this.element.getAttribute('data-multi-items') == 'off');
		this.initAccordion();
	};

	Accordion.prototype.initAccordion = function () {
		//set initial aria attributes
		for (var i = 0; i < this.items.length; i++) {
			var button = this.items[i].getElementsByTagName('button')[0],
				content = this.items[i].getElementsByClassName('js-accordion__panel')[0],
				isOpen = Util.hasClass(this.items[i], this.showClass) ? 'true' : 'false';
			Util.setAttributes(button, {
				'aria-expanded': isOpen,
				'aria-controls': 'accordion-content-' + i,
				'id': 'accordion-header-' + i
			});
			Util.addClass(button, 'js-accordion__trigger');
			Util.setAttributes(content, {'aria-labelledby': 'accordion-header-' + i, 'id': 'accordion-content-' + i});
		}

		//listen for Accordion events
		this.initAccordionEvents();
	};

	Accordion.prototype.initAccordionEvents = function () {
		var self = this;

		this.element.addEventListener('click', function (event) {
			var trigger = event.target.closest('.js-accordion__trigger');
			//check index to make sure the click didn't happen inside a children accordion
			if (trigger && Util.getIndexInArray(self.items, trigger.parentElement) >= 0) self.triggerAccordion(trigger);
		});
	};

	Accordion.prototype.triggerAccordion = function (trigger) {
		var self = this;
		var bool = (trigger.getAttribute('aria-expanded') === 'true');

		this.animateAccordion(trigger, bool);
	};

	Accordion.prototype.animateAccordion = function (trigger, bool) {
		var self = this;
		var item = trigger.closest('.js-accordion__item'),
			content = item.getElementsByClassName('js-accordion__panel')[0],
			ariaValue = bool ? 'false' : 'true';

		if (!bool) Util.addClass(item, this.showClass);
		trigger.setAttribute('aria-expanded', ariaValue);

		if (this.animateHeight) {
			//store initial and final height - animate accordion content height
			var initHeight = bool ? content.offsetHeight : 0,
				finalHeight = bool ? 0 : content.offsetHeight;
		}

		if (window.requestAnimationFrame && this.animateHeight) {
			Util.setHeight(initHeight, finalHeight, content, 200, function () {
				self.resetContentVisibility(item, content, bool);
			});
		} else {
			self.resetContentVisibility(item, content, bool);
		}

		if (!this.multiItems && !bool) this.closeSiblings(item);

	};

	Accordion.prototype.resetContentVisibility = function (item, content, bool) {
		Util.toggleClass(item, this.showClass, !bool);
		content.removeAttribute("style");
		if (bool && !this.multiItems) { // accordion item has been closed -> check if there's one open to move inside viewport
			this.moveContent();
		}
	};

	Accordion.prototype.closeSiblings = function (item) {
		//if only one accordion can be open -> search if there's another one open
		var index = Util.getIndexInArray(this.items, item);
		for (var i = 0; i < this.items.length; i++) {
			if (Util.hasClass(this.items[i], this.showClass) && i != index) {
				this.animateAccordion(this.items[i].getElementsByClassName('js-accordion__trigger')[0], true);
				return false;
			}
		}
	};

	Accordion.prototype.moveContent = function () { // make sure title of the accordion just opened is inside the viewport
		var openAccordion = this.element.getElementsByClassName(this.showClass);
		if (openAccordion.length == 0) return;
		var boundingRect = openAccordion[0].getBoundingClientRect();
		if (boundingRect.top < 0 || boundingRect.top > window.innerHeight) {
			var windowScrollTop = window.scrollY || document.documentElement.scrollTop;
			window.scrollTo(0, boundingRect.top + windowScrollTop);
		}
	};

	//initialize the Accordion objects
	var accordions = document.getElementsByClassName('js-accordion');
	if (accordions.length > 0) {
		for (var i = 0; i < accordions.length; i++) {
			(function (i) {
				new Accordion(accordions[i]);
			})(i);
		}
	}
}());


// File#: _1_custom-select
// Usage: codyhouse.co/license
(function () {
	// NOTE: you need the js code only when using the --custom-dropdown variation of the Custom Select component. Default version does nor require JS.

	var CustomSelect = function (element) {
		this.element = element;
		this.select = this.element.getElementsByTagName('select')[0];
		this.optGroups = this.select.getElementsByTagName('optgroup');
		this.options = this.select.getElementsByTagName('option');
		this.selectedOption = getSelectedOptionText(this);
		this.selectId = this.select.getAttribute('id');
		this.trigger = false;
		this.dropdown = false;
		this.customOptions = false;
		this.arrowIcon = this.element.getElementsByTagName('svg');
		this.label = document.querySelector('[for="' + this.selectId + '"]');

		initCustomSelect(this); // init markup
		initCustomSelectEvents(this); // init event listeners
	};

	function initCustomSelect(select) {
		// create the HTML for the custom dropdown element
		select.element.insertAdjacentHTML('beforeend', initButtonSelect(select) + initListSelect(select));

		// save custom elements
		select.dropdown = select.element.getElementsByClassName('js-select__dropdown')[0];
		select.trigger = select.element.getElementsByClassName('js-select__button')[0];
		select.customOptions = select.dropdown.getElementsByClassName('js-select__item');

		// hide default select
		Util.addClass(select.select, 'is-hidden');
		if (select.arrowIcon.length > 0) select.arrowIcon[0].style.display = 'none';
	};

	function initCustomSelectEvents(select) {
		// option selection in dropdown
		initSelection(select);

		// click events
		select.trigger.addEventListener('click', function () {
			toggleCustomSelect(select, false);
		});
		if (select.label) {
			// move focus to custom trigger when clicking on <select> label
			select.label.addEventListener('click', function () {
				Util.moveFocus(select.trigger);
			});
		}
		// keyboard navigation
		select.dropdown.addEventListener('keydown', function (event) {
			if (event.keyCode && event.keyCode == 38 || event.key && event.key.toLowerCase() == 'arrowup') {
				keyboardCustomSelect(select, 'prev', event);
			} else if (event.keyCode && event.keyCode == 40 || event.key && event.key.toLowerCase() == 'arrowdown') {
				keyboardCustomSelect(select, 'next', event);
			}
		});
	};

	function toggleCustomSelect(select, bool) {
		var ariaExpanded;
		if (bool) {
			ariaExpanded = bool;
		} else {
			ariaExpanded = select.trigger.getAttribute('aria-expanded') == 'true' ? 'false' : 'true';
		}
		select.trigger.setAttribute('aria-expanded', ariaExpanded);
		if (ariaExpanded == 'true') {
			var selectedOption = getSelectedOption(select);
			Util.moveFocus(selectedOption); // fallback if transition is not supported
			select.dropdown.addEventListener('transitionend', function cb() {
				Util.moveFocus(selectedOption);
				select.dropdown.removeEventListener('transitionend', cb);
			});
			placeDropdown(select); // place dropdown based on available space
		}
	};

	function placeDropdown(select) {
		var triggerBoundingRect = select.trigger.getBoundingClientRect();
		Util.toggleClass(select.dropdown, 'select__dropdown--right', (window.innerWidth < triggerBoundingRect.left + select.dropdown.offsetWidth));
		// check if there's enough space up or down
		var moveUp = (window.innerHeight - triggerBoundingRect.bottom) < triggerBoundingRect.top;
		Util.toggleClass(select.dropdown, 'select__dropdown--up', moveUp);
		// check if we need to set a max width
		var maxHeight = moveUp ? triggerBoundingRect.top - 20 : window.innerHeight - triggerBoundingRect.bottom - 20;
		// set max-height based on available space
		select.dropdown.setAttribute('style', 'max-height: ' + maxHeight + 'px; width: ' + triggerBoundingRect.width + 'px;');
	};

	function keyboardCustomSelect(select, direction, event) { // navigate custom dropdown with keyboard
		event.preventDefault();
		var index = Util.getIndexInArray(select.customOptions, document.activeElement);
		index = (direction == 'next') ? index + 1 : index - 1;
		if (index < 0) index = select.customOptions.length - 1;
		if (index >= select.customOptions.length) index = 0;
		Util.moveFocus(select.customOptions[index]);
	};

	function initSelection(select) { // option selection
		select.dropdown.addEventListener('click', function (event) {
			var option = event.target.closest('.js-select__item');
			if (!option) return;
			selectOption(select, option);
		});
	};

	function selectOption(select, option) {
		if (option.hasAttribute('aria-selected') && option.getAttribute('aria-selected') == 'true') {
			// selecting the same option
			select.trigger.setAttribute('aria-expanded', 'false'); // hide dropdown
		} else {
			var selectedOption = select.dropdown.querySelector('[aria-selected="true"]');
			if (selectedOption) selectedOption.setAttribute('aria-selected', 'false');
			option.setAttribute('aria-selected', 'true');
			select.trigger.getElementsByClassName('js-select__label')[0].textContent = option.textContent;
			select.trigger.setAttribute('aria-expanded', 'false');
			// new option has been selected -> update native <select> element _ arai-label of trigger <button>
			updateNativeSelect(select, option.getAttribute('data-value'));
			updateTriggerAria(select);
		}
		// move focus back to trigger
		select.trigger.focus();
	};

	function updateNativeSelect(select, value) {
		for (var i = 0; i < select.options.length; i++) {
			if (select.options[i].value == value) {
				select.select.selectedIndex = i; // set new value
				select.select.dispatchEvent(new CustomEvent('change')); // trigger change event
				break;
			}
		}
	};

	function updateTriggerAria(select) {
		select.trigger.setAttribute('aria-label', select.options[select.select.selectedIndex].innerHTML + ', ' + select.label.textContent);
	};

	function getSelectedOptionText(select) {// used to initialize the label of the custom select button
		var label = '';
		if ('selectedIndex' in select.select) {
			label = select.options[select.select.selectedIndex].text;
		} else {
			label = select.select.querySelector('option[selected]').text;
		}
		return label;

	};

	function initButtonSelect(select) { // create the button element -> custom select trigger
		// check if we need to add custom classes to the button trigger
		var customClasses = select.element.getAttribute('data-trigger-class') ? ' ' + select.element.getAttribute('data-trigger-class') : '';

		var label = select.options[select.select.selectedIndex].innerHTML + ', ' + select.label.textContent;

		var button = '<button type="button" class="js-select__button select__button' + customClasses + '" aria-label="' + label + '" aria-expanded="false" aria-controls="' + select.selectId + '-dropdown"><span aria-hidden="true" class="js-select__label select__label">' + select.selectedOption + '</span>';
		if (select.arrowIcon.length > 0 && select.arrowIcon[0].outerHTML) {
			var clone = select.arrowIcon[0].cloneNode(true);
			Util.removeClass(clone, 'select__icon');
			button = button + clone.outerHTML;
		}

		return button + '</button>';

	};

	function initListSelect(select) { // create custom select dropdown
		var list = '<div class="js-select__dropdown select__dropdown" aria-describedby="' + select.selectId + '-description" id="' + select.selectId + '-dropdown">';
		list = list + getSelectLabelSR(select);
		if (select.optGroups.length > 0) {
			for (var i = 0; i < select.optGroups.length; i++) {
				var optGroupList = select.optGroups[i].getElementsByTagName('option'),
					optGroupLabel = '<li><span class="select__item select__item--optgroup">' + select.optGroups[i].getAttribute('label') + '</span></li>';
				list = list + '<ul class="select__list" role="listbox">' + optGroupLabel + getOptionsList(optGroupList) + '</ul>';
			}
		} else {
			list = list + '<ul class="select__list" role="listbox">' + getOptionsList(select.options) + '</ul>';
		}
		return list;
	};

	function getSelectLabelSR(select) {
		if (select.label) {
			return '<p class="sr-only" id="' + select.selectId + '-description">' + select.label.textContent + '</p>'
		} else {
			return '';
		}
	};

	function getOptionsList(options) {
		var list = '';
		for (var i = 0; i < options.length; i++) {
			var selected = options[i].hasAttribute('selected') ? ' aria-selected="true"' : ' aria-selected="false"';
			list = list + '<li><button type="button" class="reset js-select__item select__item select__item--option" role="option" data-value="' + options[i].value + '" ' + selected + '>' + options[i].text + '</button></li>';
		}
		;
		return list;
	};

	function getSelectedOption(select) {
		var option = select.dropdown.querySelector('[aria-selected="true"]');
		if (option) return option;
		else return select.dropdown.getElementsByClassName('js-select__item')[0];
	};

	function moveFocusToSelectTrigger(select) {
		if (!document.activeElement.closest('.js-select')) return
		select.trigger.focus();
	};

	function checkCustomSelectClick(select, target) { // close select when clicking outside it
		if (!select.element.contains(target)) toggleCustomSelect(select, 'false');
	};

	//initialize the CustomSelect objects
	var customSelect = document.getElementsByClassName('js-select');
	if (customSelect.length > 0) {
		var selectArray = [];
		for (var i = 0; i < customSelect.length; i++) {
			(function (i) {
				selectArray.push(new CustomSelect(customSelect[i]));
			})(i);
		}

		// listen for key events
		window.addEventListener('keyup', function (event) {
			if (event.keyCode && event.keyCode == 27 || event.key && event.key.toLowerCase() == 'escape') {
				// close custom select on 'Esc'
				selectArray.forEach(function (element) {
					moveFocusToSelectTrigger(element); // if focus is within dropdown, move it to dropdown trigger
					toggleCustomSelect(element, 'false'); // close dropdown
				});
			}
		});
		// close custom select when clicking outside it
		window.addEventListener('click', function (event) {
			selectArray.forEach(function (element) {
				checkCustomSelectClick(element, event.target);
			});
		});
	}
}());







