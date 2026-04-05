console.log('WebUI Script loaded');

document.querySelectorAll('.logout').forEach(btn => {
    btn.addEventListener('click', (e) => {
        if (!confirm('Are you sure you want to log out?')) {
            e.preventDefault();
        }
    });
});