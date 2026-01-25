// آلة الحاسبة - حاسبة علمية بسيطة

class Calculator {
    constructor(previousOperandElement, currentOperandElement) {
        this.previousOperandElement = previousOperandElement;
        this.currentOperandElement = currentOperandElement;
        this.clear();
    }

    // مسح كل البيانات
    clear() {
        this.currentOperand = '0';
        this.previousOperand = '';
        this.operation = undefined;
    }

    // حذف آخر رقم
    delete() {
        if (this.currentOperand === '0') return;
        this.currentOperand = this.currentOperand.toString().slice(0, -1);
        if (this.currentOperand === '' || this.currentOperand === '-') {
            this.currentOperand = '0';
        }
    }

    // إضافة رقم أو نقطة عشرية
    appendNumber(number) {
        if (number === '.' && this.currentOperand.includes('.')) return;
        
        if (this.currentOperand === '0' && number !== '.') {
            this.currentOperand = number.toString();
        } else {
            this.currentOperand = this.currentOperand.toString() + number.toString();
        }
    }

    // تحديد العملية الحسابية
    chooseOperation(operation) {
        if (this.currentOperand === '0' && this.previousOperand === '') return;
        
        if (this.previousOperand !== '') {
            this.compute();
        }
        
        this.operation = operation;
        this.previousOperand = this.currentOperand;
        this.currentOperand = '0';
    }

    // تنفيذ العملية الحسابية
    compute() {
        let computation;
        const prev = parseFloat(this.previousOperand);
        const current = parseFloat(this.currentOperand);
        
        if (isNaN(prev) || isNaN(current)) return;
        
        switch (this.operation) {
            case '+':
                computation = prev + current;
                break;
            case '-':
                computation = prev - current;
                break;
            case '×':
                computation = prev * current;
                break;
            case '÷':
                if (current === 0) {
                    alert('لا يمكن القسمة على الصفر!');
                    this.clear();
                    return;
                }
                computation = prev / current;
                break;
            default:
                return;
        }
        
        this.currentOperand = this.formatNumber(computation);
        this.operation = undefined;
        this.previousOperand = '';
    }

    // تنسيق الرقم (قص الأصفار الزائدة)
    formatNumber(number) {
        const stringNumber = number.toString();
        const integerDigits = parseFloat(stringNumber.split('.')[0]);
        const decimalDigits = stringNumber.split('.')[1];
        
        let integerDisplay;
        if (isNaN(integerDigits)) {
            integerDisplay = '';
        } else {
            integerDisplay = integerDigits.toLocaleString('en-US', {
                maximumFractionDigits: 0
            });
        }
        
        if (decimalDigits != null) {
            return `${integerDisplay}.${decimalDigits}`;
        } else {
            return integerDisplay.toString();
        }
    }

    // تحديث الشاشة
    updateDisplay() {
        this.currentOperandElement.innerText = this.currentOperand;
        
        if (this.operation != null) {
            this.previousOperandElement.innerText = 
                `${this.previousOperand} ${this.operation}`;
        } else {
            this.previousOperandElement.innerText = '';
        }
    }
}

// التهيئة والربط مع DOM
const numberButtons = document.querySelectorAll('[data-number]');
const operationButtons = document.querySelectorAll('[data-operation]');
const equalsButton = document.querySelector('[data-action="equals"]');
const deleteButton = document.querySelector('[data-action="delete"]');
const clearButton = document.querySelector('[data-action="clear"]');
const previousOperandElement = document.querySelector('.previous-operand');
const currentOperandElement = document.querySelector('.current-operand');

const calculator = new Calculator(previousOperandElement, currentOperandElement);

// أحداث الأزرار
numberButtons.forEach(button => {
    button.addEventListener('click', () => {
        calculator.appendNumber(button.innerText);
        calculator.updateDisplay();
    });
});

operationButtons.forEach(button => {
    button.addEventListener('click', () => {
        calculator.chooseOperation(button.innerText);
        calculator.updateDisplay();
    });
});

equalsButton.addEventListener('click', () => {
    calculator.compute();
    calculator.updateDisplay();
});

clearButton.addEventListener('click', () => {
    calculator.clear();
    calculator.updateDisplay();
});

deleteButton.addEventListener('click', () => {
    calculator.delete();
    calculator.updateDisplay();
});

// دعم إدخال من لوحة المفاتيح
document.addEventListener('keydown', (event) => {
    if (!isNaN(event.key) || event.key === '.') {
        event.preventDefault();
        calculator.appendNumber(event.key);
        calculator.updateDisplay();
    } else if (event.key === '+' || event.key === '-') {
        event.preventDefault();
        calculator.chooseOperation(event.key);
        calculator.updateDisplay();
    } else if (event.key === '*') {
        event.preventDefault();
        calculator.chooseOperation('×');
        calculator.updateDisplay();
    } else if (event.key === '/') {
        event.preventDefault();
        calculator.chooseOperation('÷');
        calculator.updateDisplay();
    } else if (event.key === 'Enter' || event.key === '=') {
        event.preventDefault();
        calculator.compute();
        calculator.updateDisplay();
    } else if (event.key === 'Backspace') {
        event.preventDefault();
        calculator.delete();
        calculator.updateDisplay();
    } else if (event.key === 'Escape' || event.key === 'Delete') {
        event.preventDefault();
        calculator.clear();
        calculator.updateDisplay();
    }
});