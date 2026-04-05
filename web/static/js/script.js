console.log('WebUI Script loaded');

document.querySelectorAll('.logout').forEach(btn => {
    btn.addEventListener('click', (e) => {
        if (!confirm('Are you sure you want to log out?')) {
            e.preventDefault();
        }
    });
});

window.apiCall = async function(method, url, data = null) {
    const options = {
        method: method,
        headers: {
            'Content-Type': 'application/json'
        },
        credentials: 'include'
    };

    if (data) {
        options.body = JSON.stringify(data);
    }

    return fetch(url, options);
};