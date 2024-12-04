$(document).ready(function() {
    // Function to select tab and update dropdown text
    function selectTab(tabId, tabText) {
        // Hide all tab content
        $('.tab-pane').removeClass('show active');
        // Show selected tab
        $('#' + tabId).addClass('show active');
        // Update dropdown button text
        $('#borrowRequestDropdown').text(tabText);
    }

    // Ensure "Pending Requests" tab is selected by default when the page loads
    selectTab('pending', 'Pending Requests');

    // Event listener for borrow request dropdown items
    $('.dropdown-item').click(function(event) {
        event.preventDefault();
        const tabId = $(this).attr('onclick').match(/selectTab\('([^']+)'/)[1];
        const tabText = $(this).text();
        selectTab(tabId, tabText);
    });

    // Function to show book status tab and update dropdown text
    function showBookStatusTab(event, tabId, tabText) {
        event.preventDefault();
        // Hide all tab panes
        $('.tab-pane').removeClass('show active');
        // Show the selected tab pane
        $('#' + tabId).addClass('show active');
        // Update the dropdown button text
        $('#bookStatusDropdown').text(tabText);
    }

    // Set default tab and dropdown text on page load
    showBookStatusTab(new Event('DOMContentLoaded'), 'borrowed', 'Books to be Borrowed');

    // Event listener for book status dropdown items
    $('#bookStatusTabs a').click(function(event) {
        const tabId = $(this).attr('href').substring(1);
        const tabText = $(this).text();
        showBookStatusTab(event, tabId, tabText);
    });
});