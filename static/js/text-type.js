/**
 * Vanilla JS version of the TextType component.
 */
export class TextType {
  constructor(element, options = {}) {
    this.element = element;
    this.textArray = Array.isArray(options.text) ? options.text : [options.text];
    this.typingSpeed = options.typingSpeed || 50;
    this.pauseDuration = options.pauseDuration || 2000;
    this.deletingSpeed = options.deletingSpeed || 30;
    this.loop = options.loop !== undefined ? options.loop : true;
    this.cursorCharacter = options.cursorCharacter || '|';
    this.cursorBlinkDuration = options.cursorBlinkDuration || 0.5;

    this.displayedText = '';
    this.currentCharIndex = 0;
    this.isDeleting = false;
    this.currentTextIndex = 0;

    this.segments = options.segments || null;

    // Create internal structure
    this.element.innerHTML = '';
    this.contentSpan = document.createElement('span');
    this.contentSpan.className = 'text-type__wrapper';
    this.element.appendChild(this.contentSpan);

    if (options.showCursor !== false) {
      this.cursorSpan = document.createElement('span');
      this.cursorSpan.className = 'text-type__cursor';
      this.cursorSpan.textContent = this.cursorCharacter;
      this.element.appendChild(this.cursorSpan);
      this.initCursorAnimation();
    }

    this.start();
  }

  initCursorAnimation() {
    if (window.gsap) {
      window.gsap.to(this.cursorSpan, {
        opacity: 0,
        duration: this.cursorBlinkDuration,
        repeat: -1,
        yoyo: true,
        ease: 'power2.inOut'
      });
    }
  }

  start() {
    this.animate();
  }

  animate() {
    const currentText = this.textArray[this.currentTextIndex];
    
    if (this.isDeleting) {
      if (this.displayedText === '') {
        this.isDeleting = false;
        if (this.currentTextIndex === this.textArray.length - 1 && !this.loop) return;
        
        // Next sentence
        this.currentTextIndex = (this.currentTextIndex + 1) % this.textArray.length;
        this.currentCharIndex = 0;
        setTimeout(() => this.animate(), 200);
      } else {
        this.displayedText = this.displayedText.slice(0, -1);
        this.updateDisplay();
        setTimeout(() => this.animate(), this.deletingSpeed);
      }
    } else {
      if (this.currentCharIndex < currentText.length) {
        this.displayedText += currentText[this.currentCharIndex];
        this.currentCharIndex++;
        this.updateDisplay();
        setTimeout(() => this.animate(), this.typingSpeed);
      } else {
        if (!this.loop && this.currentTextIndex === this.textArray.length - 1) return;
        setTimeout(() => {
          this.isDeleting = true;
          this.animate();
        }, this.pauseDuration);
      }
    }
  }

  updateDisplay() {
    if (this.segments) {
      let remaining = this.displayedText;
      let html = '';
      for (const segment of this.segments) {
        if (remaining.length > 0) {
          const chunk = remaining.slice(0, segment.text.length);
          html += `<span class="${segment.className}">${chunk}</span>`;
          remaining = remaining.slice(segment.text.length);
        }
      }
      this.contentSpan.innerHTML = html;
    } else {
      this.contentSpan.textContent = this.displayedText;
    }
  }
}
