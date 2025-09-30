/**
 * Persian Date Picker JavaScript
 * Converts Gregorian dates to Jalali (Persian) calendar
 */

class PersianDatePicker {
    constructor(element, options = {}) {
        this.element = element;
        this.options = {
            format: 'YYYY/MM/DD',
            placeholder: 'مثال: ۱۴۰۳/۰۷/۰۱',
            minDate: null,
            maxDate: null,
            initialValue: null,
            ...options
        };
        
        this.isOpen = false;
        this.selectedDate = null;
        this.viewDate = new JalaliDate();
        
        this.init();
    }
    
    init() {
        this.setupElement();
        this.createPicker();
        this.bindEvents();
        
        // Set initial value if provided
        if (this.element.value) {
            this.setValueFromInput();
        }
    }
    
    setupElement() {
        this.element.setAttribute('readonly', 'readonly');
        this.element.setAttribute('placeholder', this.options.placeholder);
        this.element.classList.add('persian-date-picker');
    }
    
    createPicker() {
        this.picker = document.createElement('div');
        this.picker.className = 'persian-datepicker';
        this.picker.style.display = 'none';
        
        const wrapper = this.element.closest('.persian-date-wrapper') || this.element.parentNode;
        wrapper.style.position = 'relative';
        wrapper.appendChild(this.picker);
        
        this.renderPicker();
    }
    
    renderPicker() {
        const monthNames = [
            'فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور',
            'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند'
        ];
        
        const weekDays = ['ش', 'ی', 'د', 'س', 'چ', 'پ', 'ج'];
        
        this.picker.innerHTML = `
            <div class="persian-datepicker-header">
                <button type="button" class="persian-datepicker-nav" data-action="prev-month">
                    <i class="fas fa-chevron-right"></i>
                </button>
                <div class="persian-datepicker-title">
                    ${monthNames[this.viewDate.getMonth() - 1]} ${this.toPersianNumbers(this.viewDate.getFullYear())}
                </div>
                <button type="button" class="persian-datepicker-nav" data-action="next-month">
                    <i class="fas fa-chevron-left"></i>
                </button>
            </div>
            <div class="persian-datepicker-calendar">
                <div class="persian-datepicker-weekdays">
                    ${weekDays.map(day => `<div class="persian-datepicker-weekday">${day}</div>`).join('')}
                </div>
                <div class="persian-datepicker-days">
                    ${this.renderDays()}
                </div>
            </div>
            <div class="persian-datepicker-footer">
                <button type="button" class="persian-datepicker-today">امروز</button>
                <button type="button" class="persian-datepicker-clear">پاک کردن</button>
            </div>
        `;
        
        this.bindPickerEvents();
    }
    
    renderDays() {
        const year = this.viewDate.getFullYear();
        const month = this.viewDate.getMonth();
        
        // Get first day of the month and its day of week
        const firstDay = new JalaliDate(year, month, 1);
        const firstDayOfWeek = firstDay.getDay(); // 0 = Saturday, 1 = Sunday, etc.
        
        // Get days in month
        const daysInMonth = this.getDaysInMonth(year, month);
        const daysInPrevMonth = month === 1 ? this.getDaysInMonth(year - 1, 12) : this.getDaysInMonth(year, month - 1);
        
        let days = '';
        let dayCount = 1;
        let nextMonthDay = 1;
        
        // Previous month days
        for (let i = firstDayOfWeek - 1; i >= 0; i--) {
            const day = daysInPrevMonth - i;
            days += `<div class="persian-datepicker-day other-month" data-day="${day}" data-month="${month === 1 ? 12 : month - 1}" data-year="${month === 1 ? year - 1 : year}">
                ${this.toPersianNumbers(day)}
            </div>`;
        }
        
        // Current month days
        for (let day = 1; day <= daysInMonth; day++) {
            const classes = ['persian-datepicker-day'];
            const today = new JalaliDate();
            
            if (year === today.getFullYear() && month === today.getMonth() && day === today.getDate()) {
                classes.push('today');
            }
            
            if (this.selectedDate && 
                year === this.selectedDate.getFullYear() && 
                month === this.selectedDate.getMonth() && 
                day === this.selectedDate.getDate()) {
                classes.push('selected');
            }
            
            days += `<div class="${classes.join(' ')}" data-day="${day}" data-month="${month}" data-year="${year}">
                ${this.toPersianNumbers(day)}
            </div>`;
            
            dayCount++;
        }
        
        // Next month days
        const totalCells = 42; // 6 rows × 7 days
        const remainingCells = totalCells - (firstDayOfWeek + daysInMonth);
        
        for (let i = 0; i < remainingCells && nextMonthDay <= 14; i++) {
            days += `<div class="persian-datepicker-day other-month" data-day="${nextMonthDay}" data-month="${month === 12 ? 1 : month + 1}" data-year="${month === 12 ? year + 1 : year}">
                ${this.toPersianNumbers(nextMonthDay)}
            </div>`;
            nextMonthDay++;
        }
        
        return days;
    }
    
    bindEvents() {
        // Show picker on input click
        this.element.addEventListener('click', () => {
            this.show();
        });
        
        // Hide picker on outside click
        document.addEventListener('click', (e) => {
            if (!this.picker.contains(e.target) && e.target !== this.element) {
                this.hide();
            }
        });
        
        // Handle input changes
        this.element.addEventListener('input', () => {
            this.setValueFromInput();
        });
    }
    
    bindPickerEvents() {
        // Navigation buttons
        this.picker.addEventListener('click', (e) => {
            if (e.target.matches('[data-action="prev-month"]') || e.target.closest('[data-action="prev-month"]')) {
                this.previousMonth();
                e.preventDefault();
            } else if (e.target.matches('[data-action="next-month"]') || e.target.closest('[data-action="next-month"]')) {
                this.nextMonth();
                e.preventDefault();
            }
        });
        
        // Day selection
        this.picker.addEventListener('click', (e) => {
            const dayElement = e.target.closest('.persian-datepicker-day:not(.other-month)');
            if (dayElement) {
                const day = parseInt(dayElement.dataset.day);
                const month = parseInt(dayElement.dataset.month);
                const year = parseInt(dayElement.dataset.year);
                
                this.selectDate(new JalaliDate(year, month, day));
                e.preventDefault();
            }
        });
        
        // Today button
        this.picker.querySelector('.persian-datepicker-today').addEventListener('click', (e) => {
            this.selectDate(new JalaliDate());
            e.preventDefault();
        });
        
        // Clear button
        this.picker.querySelector('.persian-datepicker-clear').addEventListener('click', (e) => {
            this.clear();
            e.preventDefault();
        });
    }
    
    show() {
        if (this.isOpen) return;
        
        this.isOpen = true;
        this.picker.style.display = 'block';
        
        // Update view to selected date or today
        if (this.selectedDate) {
            this.viewDate = new JalaliDate(this.selectedDate.getFullYear(), this.selectedDate.getMonth(), this.selectedDate.getDate());
        }
        
        this.renderPicker();
    }
    
    hide() {
        this.isOpen = false;
        this.picker.style.display = 'none';
    }
    
    selectDate(date) {
        this.selectedDate = date;
        this.updateInput();
        this.hide();
        
        // Trigger change event
        const event = new Event('change', { bubbles: true });
        this.element.dispatchEvent(event);
    }
    
    clear() {
        this.selectedDate = null;
        this.element.value = '';
        this.hide();
        
        // Trigger change event
        const event = new Event('change', { bubbles: true });
        this.element.dispatchEvent(event);
    }
    
    updateInput() {
        if (this.selectedDate) {
            const formatted = this.formatDate(this.selectedDate);
            this.element.value = formatted;
        }
    }
    
    setValueFromInput() {
        const value = this.element.value.trim();
        if (!value) {
            this.selectedDate = null;
            return;
        }
        
        try {
            const date = this.parseDate(value);
            if (date) {
                this.selectedDate = date;
            }
        } catch (e) {
            console.warn('Invalid date format:', value);
        }
    }
    
    formatDate(date) {
        const year = this.toPersianNumbers(date.getFullYear());
        const month = this.toPersianNumbers(date.getMonth().toString().padStart(2, '0'));
        const day = this.toPersianNumbers(date.getDate().toString().padStart(2, '0'));
        
        return `${year}/${month}/${day}`;
    }
    
    parseDate(dateString) {
        // Convert Persian numbers to English
        const englishDate = this.toEnglishNumbers(dateString);
        
        const parts = englishDate.split('/');
        if (parts.length === 3) {
            const year = parseInt(parts[0]);
            const month = parseInt(parts[1]);
            const day = parseInt(parts[2]);
            
            if (year && month && day) {
                return new JalaliDate(year, month, day);
            }
        }
        
        return null;
    }
    
    previousMonth() {
        if (this.viewDate.getMonth() === 1) {
            this.viewDate = new JalaliDate(this.viewDate.getFullYear() - 1, 12, 1);
        } else {
            this.viewDate = new JalaliDate(this.viewDate.getFullYear(), this.viewDate.getMonth() - 1, 1);
        }
        this.renderPicker();
    }
    
    nextMonth() {
        if (this.viewDate.getMonth() === 12) {
            this.viewDate = new JalaliDate(this.viewDate.getFullYear() + 1, 1, 1);
        } else {
            this.viewDate = new JalaliDate(this.viewDate.getFullYear(), this.viewDate.getMonth() + 1, 1);
        }
        this.renderPicker();
    }
    
    getDaysInMonth(year, month) {
        if (month <= 6) {
            return 31;
        } else if (month <= 11) {
            return 30;
        } else {
            // Check if leap year
            return this.isLeapYear(year) ? 30 : 29;
        }
    }
    
    isLeapYear(year) {
        const cycle = 2820;
        const breaks = [0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1];
        
        let jp = breaks[0];
        let jump = 0;
        
        for (let j = 1; j <= 128; j++) {
            const jm = breaks[j];
            jump = jm - jp;
            if (year < jp + jump) break;
            jp = jm;
        }
        
        let n = year - jp;
        
        if (n < jump) {
            if (jump - n < 6) {
                n = n - jump + ((jump / 4) | 0) * 4;
            }
            return ((n + 1) % 4) === 0;
        } else {
            return false;
        }
    }
    
    toPersianNumbers(str) {
        const persian = '۰۱۲۳۴۵۶۷۸۹';
        const english = '0123456789';
        let result = str.toString();
        
        for (let i = 0; i < english.length; i++) {
            result = result.replace(new RegExp(english[i], 'g'), persian[i]);
        }
        
        return result;
    }
    
    toEnglishNumbers(str) {
        const persian = '۰۱۲۳۴۵۶۷۸۹';
        const english = '0123456789';
        let result = str.toString();
        
        for (let i = 0; i < persian.length; i++) {
            result = result.replace(new RegExp(persian[i], 'g'), english[i]);
        }
        
        return result;
    }
}

// Simple Jalali Date class
class JalaliDate {
    constructor(year, month, day) {
        if (arguments.length === 0) {
            // Current date
            const now = new Date();
            const jDate = this.gregorianToJalali(now.getFullYear(), now.getMonth() + 1, now.getDate());
            this.year = jDate.year;
            this.month = jDate.month;
            this.day = jDate.day;
        } else {
            this.year = year;
            this.month = month;
            this.day = day;
        }
    }
    
    getFullYear() {
        return this.year;
    }
    
    getMonth() {
        return this.month;
    }
    
    getDate() {
        return this.day;
    }
    
    getDay() {
        // Convert to Gregorian to get day of week
        const gDate = this.jalaliToGregorian(this.year, this.month, this.day);
        const jsDate = new Date(gDate.year, gDate.month - 1, gDate.day);
        return (jsDate.getDay() + 1) % 7; // Convert JS day (0=Sunday) to Persian (0=Saturday)
    }
    
    gregorianToJalali(gy, gm, gd) {
        const g_d_m = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334];
        
        let jy = (gy <= 1600) ? 0 : 979;
        gy -= (gy <= 1600) ? 621 : 1600;
        
        let gy2 = (gm > 2) ? (gy + 1) : gy;
        let days = (365 * gy) + ((gy2 + 3) / 4 | 0) - ((gy2 + 99) / 100 | 0) + ((gy2 + 399) / 400 | 0) - 80 + gd + g_d_m[gm - 1];
        
        jy += 33 * (days / 12053 | 0);
        days %= 12053;
        
        jy += 4 * (days / 1461 | 0);
        days %= 1461;
        
        jy += (days - 1) / 365 | 0;
        if (days > 365) days = (days - 1) % 365;
        
        let jm = (days < 186) ? 1 + (days / 31 | 0) : 7 + ((days - 186) / 30 | 0);
        let jd = 1 + ((days < 186) ? (days % 31) : ((days - 186) % 30));
        
        return { year: jy, month: jm, day: jd };
    }
    
    jalaliToGregorian(jy, jm, jd) {
        let gy = (jy <= 979) ? 1600 : 1979;
        jy -= (jy <= 979) ? 0 : 979;
        
        let days = (365 * jy) + ((jy / 33 | 0) * 8) + (((jy % 33) + 3) / 4 | 0) + 78 + jd + ((jm < 7) ? (jm - 1) * 31 : ((jm - 7) * 30) + 186);
        
        gy += 400 * (days / 146097 | 0);
        days %= 146097;
        
        let leap = true;
        if (days >= 36525) {
            days--;
            gy += 100 * (days / 36524 | 0);
            days %= 36524;
            if (days >= 365) days++;
            else leap = false;
        }
        
        gy += 4 * (days / 1461 | 0);
        days %= 1461;
        
        if (days >= 366) {
            leap = false;
            days--;
            gy += days / 365 | 0;
            days = days % 365;
        }
        
        let gd = days + 1;
        let sal_a = [0, 31, ((leap) ? 29 : 28), 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
        
        let gm = 0;
        for (gm = 0; gm < 13; gm++) {
            let v = sal_a[gm];
            if (gd <= v) break;
            gd -= v;
        }
        
        return { year: gy, month: gm, day: gd };
    }
}

// Initialize Persian date pickers when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize all Persian date pickers
    const dateInputs = document.querySelectorAll('.persian-date-picker');
    dateInputs.forEach(input => {
        if (!input.persianDatePicker) {
            // Wrap the input with a wrapper div if not already wrapped
            if (!input.closest('.persian-date-wrapper')) {
                const wrapper = document.createElement('div');
                wrapper.className = 'persian-date-wrapper';
                input.parentNode.insertBefore(wrapper, input);
                wrapper.appendChild(input);
                
                // Add calendar icon
                const icon = document.createElement('i');
                icon.className = 'fas fa-calendar-alt persian-date-icon';
                wrapper.appendChild(icon);
            }
            
            input.persianDatePicker = new PersianDatePicker(input);
        }
    });
    
    // Initialize all Persian datetime pickers
    const datetimeInputs = document.querySelectorAll('.persian-datetime-picker');
    datetimeInputs.forEach(input => {
        if (!input.persianDatePicker) {
            // Wrap the input with a wrapper div if not already wrapped
            if (!input.closest('.persian-datetime-wrapper')) {
                const wrapper = document.createElement('div');
                wrapper.className = 'persian-datetime-wrapper';
                input.parentNode.insertBefore(wrapper, input);
                wrapper.appendChild(input);
                
                // Add calendar icon
                const icon = document.createElement('i');
                icon.className = 'fas fa-calendar-clock persian-datetime-icon';
                wrapper.appendChild(icon);
            }
            
            input.persianDatePicker = new PersianDatePicker(input, {
                format: 'YYYY/MM/DD HH:mm',
                placeholder: 'مثال: ۱۴۰۳/۰۷/۰۱ ۱۴:۳۰'
            });
        }
    });
});
