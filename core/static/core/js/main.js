document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.vote-widget').forEach((widget) => {
    const btnUp = widget.querySelector('.vote-btn-up');
    const btnDown = widget.querySelector('.vote-btn-down');
    const countEl = widget.querySelector('.vote-count');
    if (!btnUp || !btnDown || !countEl) return;

    if (!widget.dataset.baseCount) {
      let initialCount = parseInt(countEl.textContent.trim(), 10) || 0;
      if (widget.classList.contains('voted-up')) {
        initialCount -= 1;
      } else if (widget.classList.contains('voted-down')) {
        initialCount += 1;
      }
      widget.dataset.baseCount = initialCount;
    }

    const baseCount = parseInt(widget.dataset.baseCount, 10);

    const updateUI = () => {
      if (widget.classList.contains('voted-up')) {
        countEl.textContent = baseCount + 1;
      } else if (widget.classList.contains('voted-down')) {
        countEl.textContent = baseCount - 1;
      } else {
        countEl.textContent = baseCount;
      }
    };

    btnUp.addEventListener('click', (e) => {
      e.preventDefault();
      if (widget.classList.contains('voted-up')) {
        widget.classList.remove('voted-up');
      } else {
        widget.classList.remove('voted-down');
        widget.classList.add('voted-up');
      }
      updateUI();
    });

    btnDown.addEventListener('click', (e) => {
      e.preventDefault();
      if (widget.classList.contains('voted-down')) {
        widget.classList.remove('voted-down');
      } else {
        widget.classList.remove('voted-up');
        widget.classList.add('voted-down');
      }
      updateUI();
    });
  });

  document.querySelectorAll('.correct-answer-toggle').forEach((label) => {
    const checkbox = label.querySelector('.correct-checkbox');
    if (!checkbox) return;

    const updateLabel = () => {
      if (checkbox.checked) {
        label.classList.add('is-correct');
      } else {
        label.classList.remove('is-correct');
      }
    };

    checkbox.addEventListener('change', updateLabel);
    updateLabel();
  });

  const avatarInputs = document.querySelectorAll('input[type="file"][accept*="image"], #avatarUpload');
  avatarInputs.forEach((input) => {
    input.addEventListener('change', (e) => {
      const file = e.target.files && e.target.files[0];
      if (!file) return;

      const previewImg = document.querySelector('.avatar-preview-box, #avatarPreview');
      if (previewImg) {
        const reader = new FileReader();
        reader.onload = (event) => {
          previewImg.src = event.target.result;
        };
        reader.readAsDataURL(file);
      }
    });
  });
});
