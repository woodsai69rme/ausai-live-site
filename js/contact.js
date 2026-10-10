document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('contact-form');
  if (!form) return;

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn = form.querySelector('button[type="submit"]');
    const originalText = btn.innerHTML;
    
    // UI Loading state
    btn.innerHTML = 'Sending...';
    btn.disabled = true;

    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());
    
    try {
      // Send payload to n8n webhook (Placeholder URL, update to actual production webhook)
      const response = await fetch('https://n8n.ausai-tech.com/webhook/contact', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      });
      
      // Success State
      form.innerHTML = `
        <div style="text-align:center; padding: 32px; background: rgba(34, 197, 94, 0.1); border: 1px solid var(--green); border-radius: var(--radius);">
          <div style="font-size: 2rem; margin-bottom: 12px;">✅</div>
          <h3 style="color: var(--green); margin-bottom: 8px;">Message Sent!</h3>
          <p style="color: var(--text-dim); font-size: 0.95rem;">We'll get back to you within 24 hours.</p>
        </div>
      `;
    } catch (error) {
      // Error State
      btn.innerHTML = 'Error. Try Again.';
      btn.disabled = false;
      setTimeout(() => btn.innerHTML = originalText, 3000);
    }
  });
});
