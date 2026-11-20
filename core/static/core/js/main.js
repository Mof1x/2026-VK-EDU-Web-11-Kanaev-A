document.addEventListener('DOMContentLoaded', () => {
  const avatarInput = document.querySelector('input[type="file"][name="avatar"]');
  const avatarPreview = document.getElementById('avatarPreview');
  let previewUrl;
  if (avatarInput && avatarPreview) {
    const original = avatarPreview.src;
    avatarInput.addEventListener('change', () => {
      if (previewUrl) URL.revokeObjectURL(previewUrl);
      const file = avatarInput.files[0];
      previewUrl = file ? URL.createObjectURL(file) : undefined;
      avatarPreview.src = previewUrl || original;
    });
  }

  async function send(form, submitter) {
    const data = new FormData(form, submitter);
    const response = await fetch(form.action, {
      method: 'POST',
      headers: { Accept: 'application/json' },
      body: data,
    });
    if (response.status === 401) {
      const login = new URL(document.body.dataset.loginUrl, window.location.origin);
      login.searchParams.set('next', location.pathname + location.search + location.hash);
      window.location.assign(login);
      return null;
    }
    const result = await response.json().catch(() => null);
    if (!response.ok || !result) {
      throw new Error(result?.error || 'Не удалось сохранить изменение. Попробуйте ещё раз.');
    }
    return result;
  }

  function showError(element, error) {
    element.textContent = error.message || 'Проверьте соединение и попробуйте ещё раз.';
    element.hidden = false;
  }

  function updateVote(form, buttons, result) {
    form.querySelector('.vote-count').textContent = result.rating;
    form.classList.toggle('voted-up', result.value === 1);
    form.classList.toggle('voted-down', result.value === -1);
    buttons.forEach((button) => {
      const selected = Number(button.value) === result.value;
      button.disabled = selected;
      button.setAttribute('aria-pressed', String(selected));
      button.title = selected ? 'Эта оценка уже поставлена' : '';
    });
  }

  document.querySelectorAll('[data-vote]').forEach((form) => {
    const error = form.querySelector('[data-ajax-error]');
    const buttons = Array.from(form.querySelectorAll('button[type="submit"]'));
    let pending = false;
    form.addEventListener('submit', async (event) => {
      event.preventDefault();
      if (pending || !event.submitter || event.submitter.disabled) return;
      pending = true;
      error.hidden = true;
      const previous = buttons.map((button) => button.disabled);
      try {
        const response = send(form, event.submitter);
        buttons.forEach((button) => { button.disabled = true; });
        const result = await response;
        if (result) updateVote(form, buttons, result);
      } catch (failure) {
        buttons.forEach((button, index) => { button.disabled = previous[index]; });
        showError(error, failure);
      } finally {
        pending = false;
      }
    });
  });

  const acceptForms = Array.from(document.querySelectorAll('[data-accept-answer]'));
  const acceptButtons = acceptForms.map((form) => form.querySelector('button'));
  let accepting = false;
  acceptForms.forEach((form) => {
    form.addEventListener('submit', async (event) => {
      event.preventDefault();
      if (accepting || !event.submitter || event.submitter.disabled) return;
      accepting = true;
      acceptForms.forEach((candidate) => {
        candidate.querySelector('[data-ajax-error]').hidden = true;
      });
      const previous = acceptButtons.map((button) => button.disabled);
      try {
        const response = send(form, event.submitter);
        acceptButtons.forEach((button) => { button.disabled = true; });
        const result = await response;
        if (!result) return;
        document.querySelectorAll('[data-answer-id]').forEach((card) => {
          const selected = card.dataset.answerId === String(result.answer_id);
          card.classList.toggle('border-success', selected);
          card.querySelector('[data-correct-badge]').hidden = !selected;
          const button = card.querySelector('[data-accept-answer] button');
          if (button) {
            button.disabled = selected;
            button.textContent = selected ? 'Ответ уже выбран' : 'Отметить верным';
          }
        });
      } catch (failure) {
        acceptButtons.forEach((button, index) => { button.disabled = previous[index]; });
        showError(form.querySelector('[data-ajax-error]'), failure);
      } finally {
        accepting = false;
      }
    });
  });
});
