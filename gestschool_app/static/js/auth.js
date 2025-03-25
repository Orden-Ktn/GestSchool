setTimeout(function() {
    let alerts = document.querySelectorAll('.alert-fill'); // Sélectionne les alertes par leur classe
    alerts.forEach(function(alert) {
        alert.style.display = 'none';
    });
}, 8000);