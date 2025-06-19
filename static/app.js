// Animación de carga y feedback visual
document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('upload-form');
  const copyType = document.getElementById('copy-type');
  const tone = document.getElementById('tone');
  const fileInput = document.getElementById('excel-file');
  const submitBtn = document.getElementById('submit-btn');
  const resultSection = document.getElementById('result-section');
  const resultList = document.getElementById('result-list');
  const loader = document.getElementById('loader');

  if (form) {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      if (!fileInput.files.length) {
        alert('Por favor, selecciona un archivo Excel.');
        return;
      }
      submitBtn.disabled = true;
      loader.style.display = 'block';
      resultSection.style.display = 'none';
      resultList.innerHTML = '';

      const formData = new FormData();
      formData.append('excel', fileInput.files[0]);
      formData.append('copy_type', copyType.value);
      formData.append('tone', tone.value);

      try {
        const response = await fetch('/procesar', {
          method: 'POST',
          body: formData
        });
        const data = await response.json();
        loader.style.display = 'none';
        submitBtn.disabled = false;

        if (data.success) {
          resultSection.style.display = 'block';
          renderResults(data.results, data.premium);
        } else {
          alert(data.error || 'Ocurrió un error al procesar el archivo.');
        }
      } catch (err) {
        loader.style.display = 'none';
        submitBtn.disabled = false;
        alert('Error de conexión con el servidor.');
      }
    });
  }

  function renderResults(results, premium) {
    resultList.innerHTML = '';
    results.forEach(cliente => {
      const card = document.createElement('div');
      card.className = 'result-card';
      card.innerHTML = `
        <div class="client-name">${cliente.nombre}</div>
        <div class="promo-copy">${cliente.copy}</div>
        ${premium && cliente.telefono ? `
          <a class="btn-whatsapp" target="_blank"
            href="https://wa.me/${cliente.telefono}?text=${encodeURIComponent(cliente.copy)}">
            <svg width="20" height="20" fill="currentColor" viewBox="0 0 32 32"><path d="M16.001 3.2c-7.06 0-12.8 5.74-12.8 12.8 0 2.26.6 4.47 1.74 6.41l-1.84 6.73 6.9-1.81c1.86 1.02 3.97 1.56 6.02 1.56h.01c7.06 0 12.8-5.74 12.8-12.8s-5.74-12.8-12.8-12.8zm0 23.36c-1.82 0-3.62-.48-5.19-1.38l-.37-.21-4.1 1.08 1.1-4.01-.24-.41c-1.08-1.77-1.65-3.81-1.65-5.89 0-6.05 4.93-10.98 10.98-10.98s10.98 4.93 10.98 10.98-4.93 10.98-10.98 10.98zm6.01-8.29c-.33-.17-1.95-.96-2.25-1.07-.3-.11-.52-.17-.74.17-.22.33-.85 1.07-1.04 1.29-.19.22-.38.25-.71.08-.33-.17-1.39-.51-2.65-1.62-.98-.87-1.64-1.94-1.83-2.27-.19-.33-.02-.51.15-.68.15-.15.33-.38.5-.57.17-.19.22-.33.33-.55.11-.22.06-.41-.03-.58-.09-.17-.74-1.78-1.01-2.44-.27-.65-.54-.56-.74-.57-.19-.01-.41-.01-.63-.01-.22 0-.58.08-.89.41-.3.33-1.17 1.14-1.17 2.77s1.2 3.22 1.37 3.44c.17.22 2.36 3.6 5.73 4.91.8.28 1.43.45 1.92.58.81.21 1.54.18 2.12.11.65-.08 1.95-.8 2.23-1.57.28-.77.28-1.43.2-1.57-.08-.14-.3-.22-.63-.39z"/></svg>
            WhatsApp
          </a>
        ` : ''}
      `;
      resultList.appendChild(card);
    });
  }
});