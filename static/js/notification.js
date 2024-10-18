function toggleDropdown() {
    var dropdown = document.getElementById('notification-dropdown');
    dropdown.style.display = dropdown.style.display === 'block' ? 'none' : 'block';
}

function addNotification(message) {
    var dropdown = document.getElementById('notification-dropdown');
    var badge = document.getElementById('notification-badge');
    var newNotification = document.createElement('div');
    newNotification.className = 'dropdown-item';
    newNotification.textContent = message;
    dropdown.prepend(newNotification);
    badge.textContent = parseInt(badge.textContent) + 1;
}

document.addEventListener('DOMContentLoaded', function() {
    var notifications = [];
    {% for message in messages %}
        {% if message.extra_tags == user.username %}
            notifications.push('{{ message }}');
        {% endif %}
    {% endfor %}

    notifications.forEach(function(notification) {
        addNotification(notification);
    });
});
