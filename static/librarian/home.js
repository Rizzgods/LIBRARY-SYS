$(document).ready(function(){
    $('.nav-link').on('click', function() {
        const target = $(this).attr('aria-controls');
        $('.content-section').addClass('hidden');
        $('#' + target).removeClass('hidden');
        history.pushState(null, '', '#' + target);
    });

    function loadContent(url, target) {
        $.get(url, function(data) {
            $('#' + target).html($(data).find('#' + target).html());
        });
    }

    window.onpopstate = function() {
        const hash = window.location.hash.substring(1);
        if (hash) {
            $('.content-section').addClass('hidden');
            $('#' + hash).removeClass('hidden');
        }
    };

    const initialHash = window.location.hash.substring(1);
    if (initialHash) {
        $('.content-section').addClass('hidden');
        $('#' + initialHash).removeClass('hidden');
    }
});