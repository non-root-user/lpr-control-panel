function showError(msg) {
    error.innerHTML = msg;
    error.style.display = 'block';
    setTimeout(() => error.style.display = 'none', 8000);
 }