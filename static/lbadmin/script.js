$(document).ready(function() {
<<<<<<< HEAD
   
=======
    var userId, userStatus;

    $('#confirmDisableModal').on('show.bs.modal', function(event) {
        var button = $(event.relatedTarget);
        userId = button.data('user-id');
        userStatus = button.data('user-status');
        var actionText = userStatus ? 'disable' : 'activate';
        $('#action-text').text(actionText);
    });

    $('#confirmAction').click(function() {
        // Hide any open modal
        $('.modal').modal('hide');

        // Show loading spinner modal
        $('#loadingSpinnerModal').modal('show');

        $.ajax({
            url: '/toggle_user_status/', // Update this URL to match your Django URL configuration
            method: 'POST',
            data: {
                'user_id': userId,
                'csrfmiddlewaretoken': '{{ csrf_token }}'
            },
            success: function(response) {
                if (response.status == 'success') {
                    var newStatus = response.new_status;
                    $('#user-status-' + userId).text(newStatus);
                    var newButtonText = newStatus ? 'Disable' : 'Activate';
                    var newButtonClass = newStatus ? 'btn btn-danger' : 'btn btn-success';
                    $('button[data-user-id="' + userId + '"]').text(newButtonText).removeClass('btn-success btn-danger').addClass(newButtonClass);
                    $('button[data-user-id="' + userId + '"]').data('user-status', newStatus);
                    localStorage.setItem('activeSection', 'analytics-section'); // Store the active section
                    setTimeout(function() {
                        $('#successModalMessage').text('Successfully ' + (newStatus ? 'activated' : 'disabled'));
                        $('#successModal').modal('show');
                        setTimeout(function() {
                            $('#successModal').modal('hide');
                            location.reload(); // Refresh the page
                        }, 2000);
                    }, 500);
                }
            },
            complete: function() {
                // Hide loading spinner modal
                $('#loadingSpinnerModal').modal('hide');
            }
        });
    });
>>>>>>> 43d9a97dce1302de564145fd09a0d1e8094a5f56

    // Function to show the specified section
    function showSection(sectionId) {
        // Hide all sections
        $('#overview-section').hide(); 
        $('#active-section').hide();
        $('#analytics-section').hide();
        $('#Create-section').hide();
        $('#csv-section').hide();
        
        // Show the specified section
        $('#' + sectionId).show();
        
        // Store the active section in localStorage
        localStorage.setItem('activeSection', sectionId);
    }

    // Check local storage for active section and display it
    var activeSection = localStorage.getItem('activeSection');
    if (activeSection) {
        showSection(activeSection);
    } else {
        showSection('overview-section'); // Default to overview section
    }

    // Event listeners for sidebar links
    $('#overview-link').click(function() {
        showSection('overview-section');
    });

    $('#active-link').click(function() {
        showSection('active-section');
    });

    $('#analytics-link').click(function() {
        showSection('analytics-section');
    });

    $('#Create-link').click(function() {
        showSection('Create-section');
    });

    $('#CSV-link').click(function() {
        showSection('csv-section');
    });

<<<<<<< HEAD
    
=======
    // Example of storing the active section after an AJAX request
    $('button[data-user-id="' + userId + '"]').data('user-status', newStatus);
    localStorage.setItem('activeSection', 'analytics-section'); // Store the active section
    setTimeout(function() {
        $('#successModalMessage').text('Successfully ' + (newStatus ? 'activated' : 'disabled'));
        $('#successModal').modal('show');
        setTimeout(function() {
            $('#successModal').modal('hide');
            location.reload(); // Refresh the page
        }, 2000);
    }, 500);

    function filterTableByRole() {
        var filterValue = document.getElementById("role-filter").value.toLowerCase();
        var table = document.getElementById("user-list-tbody");
        var rows = table.getElementsByTagName("tr");

        for (var i = 0; i < rows.length; i++) {
            var roleCell = rows[i].getElementsByTagName("td")[3]; // Assuming role is in the fourth column
            if (roleCell) {
                var role = roleCell.textContent || roleCell.innerText;
                if (filterValue === "" || role.toLowerCase().indexOf(filterValue) > -1) {
                    rows[i].style.display = "";
                } else {
                    rows[i].style.display = "none";
                }
            }
        }
    }

    function searchTableByUsernameAndDetails() {
        var input = document.getElementById('search-input1');
        var filter = input.value.toLowerCase();
        var table = document.getElementById('user-list-tbody');
        var rows = table.getElementsByTagName("tr");
        var anyMatch = false;

        // Remove the "no matches" row if it exists
        var noMatchesRow = document.getElementById('no-matches-row');
        if (noMatchesRow) {
            noMatchesRow.remove();
        }

        // If the search input is blank, reset the state of the table
        if (filter === "") {
            for (var i = 0; i < rows.length; i++) {
                rows[i].style.display = ""; // Show all rows
            }
            return;
        }

        for (var i = 0; i < rows.length; i++) {
            var usernameCell = rows[i].getElementsByTagName("td")[0];
            var emailCell = rows[i].getElementsByTagName("td")[1];
            var nameCell = rows[i].getElementsByTagName("td")[2];
            var roleCell = rows[i].getElementsByTagName("td")[3];

            // Extract text content
            var username = usernameCell ? usernameCell.textContent.toLowerCase() : "";
            var email = emailCell ? emailCell.textContent.toLowerCase() : "";
            var name = nameCell ? nameCell.textContent.toLowerCase() : "";
            var role = roleCell ? roleCell.textContent.toLowerCase() : "";

            // Check if any of the fields match the search filter
            if (username.includes(filter) || email.includes(filter) || name.includes(filter) || role.includes(filter)) {
                rows[i].style.display = ""; // Show row
                anyMatch = true;
            } else {
                rows[i].style.display = "none"; // Hide row
            }
        }

        // If no rows match, display a "no matches" row
        if (!anyMatch) {
            noMatchesRow = document.createElement('tr');
            noMatchesRow.id = 'no-matches-row';
            noMatchesRow.innerHTML = `<td colspan="6">No "${input.value}" matches from the records</td>`;
            table.appendChild(noMatchesRow);
        }
    }

    // Attach event listeners
    document.getElementById("role-filter").addEventListener("change", filterTableByRole);
    document.getElementById("search-input1").addEventListener("input", searchTableByUsernameAndDetails);

>>>>>>> 43d9a97dce1302de564145fd09a0d1e8094a5f56
    // Function to show the overview content
    function showOverview() {
        document.getElementById('overview-section').style.display = 'block';
        document.getElementById('active-section').style.display = 'none';
        document.getElementById('analytics-section').style.display = 'none';
        document.getElementById('Create-section').style.display = 'none';
        document.getElementById('csv-section').style.display = 'none';
    }

    // Function to show the active content
    function showActive() {
        document.getElementById('overview-section').style.display = 'none';
        document.getElementById('active-section').style.display = 'block';
        document.getElementById('analytics-section').style.display = 'none';
        document.getElementById('Create-section').style.display = 'none';
        document.getElementById('csv-section').style.display = 'none';
    }

    // Function to show the analytics content
    function showAnalytics() {
        document.getElementById('overview-section').style.display = 'none';
        document.getElementById('active-section').style.display = 'none';
        document.getElementById('analytics-section').style.display = 'block';
        document.getElementById('Create-section').style.display = 'none';
        document.getElementById('csv-section').style.display = 'none';
    }

    // Function to show the create section
    function showCreate() {
        document.getElementById('overview-section').style.display = 'none';
        document.getElementById('active-section').style.display = 'none';
        document.getElementById('analytics-section').style.display = 'none';
        document.getElementById('Create-section').style.display = 'block';
        document.getElementById('csv-section').style.display = 'none';
    }

    function showCSV() {
        document.getElementById('overview-section').style.display = 'none';
        document.getElementById('active-section').style.display = 'none';
        document.getElementById('analytics-section').style.display = 'none';
        document.getElementById('Create-section').style.display = 'none';
        document.getElementById('csv-section').style.display = 'block';
    }

    // Show the overview content by default
    showOverview();

    // Add click event listeners to sidebar links
    document.getElementById('overview-link').addEventListener('click', function () {
        showOverview();
    });

    document.getElementById('active-link').addEventListener('click', function () {
        showActive();
    });

    document.getElementById('analytics-link').addEventListener('click', function () {
        showAnalytics();
    });

    document.getElementById('Create-link').addEventListener('click', function () {
        showCreate();
    });

    document.getElementById('CSV-link').addEventListener('click', function () {
        showCSV();
    });
});

function filterTableByMonth() {
    var filterValue = document.getElementById("month-filter").value;
    var table = document.getElementById("activity-log-tbody");
    var rows = table.getElementsByTagName("tr");
    var monthMapping = {
    "Jan.": "01", "Feb.": "02", "March": "03", "April": "04", 
    "May": "05", "June": "06", "July": "07", "Aug.": "08", 
    "Sept.": "09", "Oct.": "10", "Nov.": "11", "Dec.": "12"
    };

    for (var i = 0; i < rows.length; i++) {
    var loginTime = rows[i].getElementsByTagName("td")[1]; // Assuming login time is in the second column
    if (loginTime) {
        var dateParts = loginTime.innerHTML.split(' ');
        var shortMonth = dateParts[0];
        var monthIndex = monthMapping[shortMonth];
        if (filterValue === "" || monthIndex === filterValue) {
        rows[i].style.display = "";
        } else {
        rows[i].style.display = "none";
        }
    }
    }
}
function searchTableByUsernameActivity() {
    var input = document.getElementById("search-input");
    var filter = input.value.toLowerCase();
    var table = document.getElementById("activity-log-tbody");
    var rows = table.getElementsByTagName("tr");

    for (var i = 0; i < rows.length; i++) {
    var usernameCell = rows[i].getElementsByTagName("td")[0]; // Assuming username is in the first column
    if (usernameCell) {
        var username = usernameCell.textContent || usernameCell.innerText;
        if (username.toLowerCase().indexOf(filter) > -1) {
        rows[i].style.display = "";
        } else {
        rows[i].style.display = "none";
        }
    }
    }
}

function previewCSV() {
    const fileInput = document.getElementById('csvFile');
    const file = fileInput.files[0];
    const previewTable = document.getElementById('csvPreviewTable');
    const previewSection = document.getElementById('csvPreview');

    if (file) {
        const reader = new FileReader();
        reader.onload = function(event) {
            const csvData = event.target.result;
            const rows = csvData.split('\n').slice(0, 5);  // Preview first 5 rows
            const tableHeaders = rows[0].split(',').map(header => header.trim());

            // Clear previous preview
            previewTable.querySelector('thead').innerHTML = '';
            previewTable.querySelector('tbody').innerHTML = '';

            // Create headers
            const headerRow = document.createElement('tr');
            tableHeaders.forEach(header => {
                const th = document.createElement('th');
                th.textContent = header;
                headerRow.appendChild(th);
            });
            previewTable.querySelector('thead').appendChild(headerRow);

            // Populate preview with data rows
            rows.slice(1).forEach(row => {
                const rowData = row.split(',').map(cell => cell.trim());
                const rowElement = document.createElement('tr');
                rowData.forEach(cell => {
                    const td = document.createElement('td');
                    td.textContent = cell;
                    rowElement.appendChild(td);
                });
                previewTable.querySelector('tbody').appendChild(rowElement);
            });

            // Show preview section
            previewSection.style.display = 'block';
        };

        reader.readAsText(file);
    } else {
        // Hide preview if no file selected
        previewSection.style.display = 'none';
    }
}

function toggleForm() {
    var role = document.getElementById('role').value;
    var studentForm = document.getElementById('student-form');
    var librarianForm = document.getElementById('librarian-form');

    if (role === 'Student') {
        studentForm.classList.remove('d-none');
        librarianForm.classList.add('d-none');
    } else if (role === 'Librarian') {
        studentForm.classList.add('d-none');
        librarianForm.classList.remove('d-none');
    }
}

// Initialize form visibility based on the selected role
document.addEventListener('DOMContentLoaded', function() {
    toggleForm();
});