$(document).ready(function() {
    $('#id_Category').change(function() {
        var selectedCategoryId = $(this).val();
        $('#id_Subcategories option').each(function() {
            var subcategoryCategoryId = $(this).data('category-id');
            if (subcategoryCategoryId == selectedCategoryId || !selectedCategoryId) {
                $(this).show();
            } else {
                $(this).hide();
            }
        });
        $('#id_Subcategories').val(''); // Reset subcategory selection
        $('#id_Subsection').val(''); // Reset subsection selection
        $('#id_Subsection option').hide(); // Hide all subsections initially
    });

    $('#id_Subcategories').change(function() {
        var selectedSubCategoryId = $(this).val();
        $('#id_Subsection option').each(function() {
            var subsectionSubCategoryId = $(this).data('section-id');
            if (subsectionSubCategoryId == selectedSubCategoryId || !selectedSubCategoryId) {
                $(this).show();
            } else {
                $(this).hide();
            }
        });
        $('#id_Subsection').val(''); // Reset subsection selection
    });
});


let noOfCharac = 150;
let contents = document.querySelectorAll(".book-description");
contents.forEach(content => {
        let displayText = content.textContent.slice(0, noOfCharac);
        let moreText = content.textContent.slice(noOfCharac);
        if(content.textContent.length > noOfCharac){
            content.innerHTML = `${displayText}<span class="dots">...</span><span class="hide more">${moreText}</span>`;
        }
});

function readMore(btn) {
    // Find the parent row <tr> of the button clicked
    let row = btn.closest('tr');

    // Toggle visibility of the new content row and current row
    if (btn.textContent === "More Info") {
        // Hide the current row
        row.style.display = 'none';

        // Create a new <tr> to insert after the current one
        let newRow = document.createElement('tr');
        newRow.classList.add('new-row');

        // Insert new HTML content inside the new row
        newRow.innerHTML = `
            <td colspan="11">
                <div class="info-container pt-4">
                    <div class="read-more-body row">
                        <div class="read-more-bookInfo col-5">
                            <div>
                                <div class="center-item row">
                                    <dt class="fs-3">${row.querySelector(".over-flow").textContent}</dt>
                                </div>
                                <div class="center-item row">
                                    <span class="fs-5">${row.children[1].textContent}</span>
                                </div>
                                <div class="center-item row">
                                    <img src="${row.querySelector('.lib-img') ? row.querySelector('.lib-img').src : ''}" class="lib-img">
                                </div>
                            </div>
                        </div>
                        <div class="col" style="padding-top: 80px; padding-right: 50px; text-align: justify;">
                            <div class="row">
                                <dt class="center-item mb-3" style="font-size: 1.2rem;">Description</dt>
                                <p style="font-size: .8rem;">${row.querySelector(".book-description").textContent}</p>
                            </div>
                            <div class="row">
                                <div class="col">
                                    <dt class="center-item">Category</dt>
                                    <span class="center-item">${row.children[4].textContent}</span>
                                </div>
                                <div class="col">
                                    <dt class="center-item">SubCategory</dt>
                                    <span class="center-item" style="font-size:.8rem;">${row.children[5].textContent}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="row mt-5">
                        <div class="col">
                            <dt class="d-flex justify-content-center row">stock</dt>
                            <p class="d-flex justify-content-center row">${row.children[9].textContent}</p>
                        </div>
                        <div class="col">
                            <dt class="d-flex justify-content-center row">file type</dt>
                            <p class="d-flex justify-content-center row">${row.children[8].textContent}</p>
                        </div>
                        <div class="col">
                            <dt class="d-flex justify-content-center row">language</dt>
                            <p class="d-flex justify-content-center row">${row.children[6].textContent}</p>
                        </div>
                        <div class="col-2">
                            <dt class="d-flex justify-content-center">actions</dt>
                            <div class="row restore-delete">
                                ${row.querySelector(".more-info-btn").innerHTML}
                                ${row.querySelector(".more-info-btn2").innerHTML}
                            </div>
                        </div>
                    </div>
                </div>
                <button class="btn btn-danger" onclick="readLess(this)">Less Info</button>
            </td>
        `;

        // Insert the new row after the current row
        row.parentNode.insertBefore(newRow, row.nextSibling);

    } else {
        // Remove the new row and show the original one
        let newRow = row.nextElementSibling;
        if (newRow && newRow.classList.contains('new-row')) {
            newRow.remove();  // Remove the new row
        }
        row.style.display = '';  // Show the original row
        btn.textContent = "More Info";  // Reset the button text
    }
}

function readLess(btn) {
    let newRow = btn.closest('tr');
    let originalRow = newRow.previousElementSibling;

    // Remove the new row and show the original row
    newRow.remove();
    originalRow.style.display = '';
    originalRow.querySelector('.read-btn').textContent = "More Info";
}



function setDeleteUrl(bookId) {
    var bookRow = document.getElementById('bookRow-' + bookId);
    bookRow.style.display = 'none';

    var deletedBookRow = document.getElementById('deletedBookRow-' + bookId);
    deletedBookRow.style.display = 'table-row';
}

function deleteAllBooks() {
    var bookRows = document.getElementsByClassName('bookRow');
    for (var i = 0; i < bookRows.length; i++) {
        bookRows[i].style.display = 'none';
    }

    var deletedBookRows = document.getElementsByClassName('deletedBookRow');
    for (var i = 0; i < deletedBookRows.length; i++) {
        deletedBookRows[i].style.display = 'table-row';
    }

    showDeletedBooks();
}

function confirmDeleteBookSection(bookId) {
    if (confirm('Are you sure you want to delete this book?')) {
        document.getElementById('deleteForm-' + bookId).submit();
    }
}

document.addEventListener('DOMContentLoaded', function() {
    const ebookCheckbox = document.getElementById('id_eBook');
    const researchPaperCheckbox = document.getElementById('id_research_paper');

    ebookCheckbox.addEventListener('change', function() {
        if (ebookCheckbox.checked) {
            researchPaperCheckbox.checked = false;
        }
    });

    researchPaperCheckbox.addEventListener('change', function() {
        if (researchPaperCheckbox.checked) {
            ebookCheckbox.checked = false;
        }
    });
});

function toggleAvailability(bookId) {
    var availabilityBtn = document.getElementById('availabilityBtn-' + bookId);
    var isAvailable = availabilityBtn.classList.contains('btn-success');
    var newAvailability = isAvailable ? 'false' : 'true';

    $.ajax({
        url: '{% url "toggle_availability" 0 %}'.replace('0', bookId),
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': '{{ csrf_token }}',
            'book_id': bookId,
            'available': newAvailability
        },
        success: function(response) {
            if (response.success) {
                if (newAvailability === 'true') {
                    availabilityBtn.innerHTML = 'Available';
                    availabilityBtn.classList.remove('btn-danger');
                    availabilityBtn.classList.add('btn-success');
                } else {
                    availabilityBtn.innerHTML = 'Not Available';
                    availabilityBtn.classList.remove('btn-success');
                    availabilityBtn.classList.add('btn-danger');
                }
            } else {
                console.log('Error toggling availability');
            }
        },
        error: function(xhr, status, error) {
            console.log('Error toggling availability:', error);
        }
    });
}

function confirmDeleteAll() {
    $('#deleteAllModal').modal('show');
}

function deleteAllBooks() {
    document.getElementById("deleteAllForm").submit();
}

$(document).ready(function() {
    $('#deleteModalBook').on('show.bs.modal', function(event) {
        var button = $(event.relatedTarget);
        var bookId = button.data('bookid');
        $('#confirmDeleteBtnBook').data('bookid', bookId);
    });

    // Add click handler for the confirm button
    $('#confirmDeleteBtnBook').on('click', function() {
        var bookId = $(this).data('bookid');
        $('#deleteFormBook-' + bookId).submit();
    });

    $('#deleteModalRecentDel').on('show.bs.modal', function(event) {
        var button = $(event.relatedTarget);
        var bookId = button.data('bookid');
        var modal = $(this);
        modal.find('#confirmDeleteBtnRecentDel').click(function() {
            $('#deleteFormRecentDel-' + bookId).submit();
        });
    });

    $('#restoreModalRecentDel').on('show.bs.modal', function(event) {
        var button = $(event.relatedTarget);
        var bookId = button.data('bookid');
        var modal = $(this);
        modal.find('#confirmRestoreBtnRecentDel').click(function() {
            $('#restoreFormRecentDel-' + bookId).submit();
        });
    });
});

function submitDeleteForm(bookId) {
    var form = $('#deleteFormBook-' + bookId);
    form.submit();
}

function submitRestoreForm(bookId) {
    var form = $('#deleteFormBook-' + bookId);
    form.submit();
}

document.addEventListener('DOMContentLoaded', function() {
    const buttons = document.querySelectorAll('.availabilityBtn');
    buttons.forEach(button => {
        button.addEventListener('click', function(event) {
            event.preventDefault();
            const id = this.getAttribute('data-id');
            const status = this.getAttribute('data-status') === 'true';
            const type = this.getAttribute('data-type');
            openModal(id, status, type);
        });
    });
});

function openModal(id, status, type) {
    const modal = document.getElementById('statusModal');
    const modalBody = document.getElementById('modalBody');

    let actionUrl, buttonClass, buttonText, questionText;
    if (type === 'request') {
        actionUrl = `{% url 'toggle_book_status' 0 %}`.replace('0', id);
        buttonClass = status ? 'btn-success' : 'btn-success';
        buttonText = status ? 'In' : 'Yes';
        questionText = 'Are you sure you want to change the status of this book?';
    } else if (type === 'out') {
        actionUrl = `{% url 'toggle_out_status' 0 %}`.replace('0', id);
        buttonClass = status ? 'btn-danger' : 'btn-success';
        buttonText = status ? 'Out' : 'Yes';
        questionText = 'Are you sure that this book is returned?';
    }

    const content = `
        <p>${questionText}</p>
        <form id="toggleForm-${id}" method="post" action="${actionUrl}" style="display: inline;">
            {% csrf_token %}
            <button id="availabilityBtn-${id}" class="btn ${buttonClass}">
                ${buttonText}
            </button>
            <button type="button" class="btn btn-secondary" onclick="closeModal()">Cancel</button>
        </form>
    `;

    modalBody.innerHTML = content;
    modal.style.display = 'block';
}

function closeModal() {
    const modal = document.getElementById('statusModal');
    modal.style.display = 'none';
}

window.onclick = function(event) {
    const modal = document.getElementById('statusModal');
    if (event.target == modal) {
        modal.style.display = 'none';
    }
};

function keepSessionAlive() {
    fetch(keepSessionAliveUrl, {
        method: 'GET',
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    }).then(response => response.json())
      .then(data => {
          console.log('Session kept alive:', data);
      }).catch(error => {
          console.error('Error keeping session alive:', error);
      });
}

// Event listener to keep the session alive on every mouse click
document.addEventListener('click', keepSessionAlive);
document.addEventListener('keypress', keepSessionAlive);

// Optionally, you can still send an AJAX request periodically
setInterval(keepSessionAlive, 300000);


function showTab(event, tabId) {
    event.preventDefault();
            
                // Hide all tab content
    $('.tab-pane').removeClass('show active').addClass('hidden');
            
                // Remove active classes from all tabs
    $('#bookStatusTabs a').removeClass('text-blue-600 border-blue-600 active')
        .addClass('text-gray-600 border-transparent');
            
                // Show the selected tab content
    $('#' + tabId).removeClass('hidden').addClass('show active');
            
                // Add active class to the selected tab
    $(event.currentTarget).addClass('border-blue-600 active')
        .removeClass('border-transparent');
}
        
            // Function to view book details
function viewBookDetails(imageUrl, title, description) {
    $('#viewBookImage').attr('src', imageUrl);
    $('#viewBookTitle').text(title);
    $('#viewBookDescription').text(description);
    $('#viewBookModal').modal('show');
}
        
function selectTab(tabId, tabText) {
                // Hide all tab content
    $('.tab-pane').removeClass('show active');
                // Show selected tab
    $('#' + tabId).addClass('show active');
                // Update dropdown button text
    $('#borrowRequestDropdown').text(tabText);
}
        
            // Ensure "Pending Requests" tab is selected by default when the page loads
$(document).ready(function() {
    selectTab('pending', 'Pending Requests');
});

function filterRequests() {
    // Get the search input and the active tab
    const input = document.getElementById('searchRequests').value.toLowerCase();
    const activeTab = document.querySelector('.tab-pane.show.active').id;
    let table;

    // Determine which table to filter based on the active tab
    if (activeTab === 'borrowed') {
        table = document.querySelectorAll('#borrowedTable tbody tr');
    } else if (activeTab === 'returned') {
        table = document.querySelectorAll('#returnedTable tbody tr');
    } else if (activeTab === 'logs') {
        table = document.querySelectorAll('#logsTable tbody tr');
    }

    // Filter the rows in the determined table
    table.forEach(row => {
        const text = row.textContent.toLowerCase();
        row.style.display = text.includes(input) ? '' : 'none';
    });
}

// Add an event listener for the search input
document.getElementById('searchRequests').addEventListener('keyup', filterRequests);

function showBookStatusTab(event, tabId, tabText) {
    event.preventDefault();
    // Hide all tab panes
    document.querySelectorAll('.tab-pane').forEach(tab => {
        tab.classList.remove('show', 'active');
    });
    // Show the selected tab pane
    document.getElementById(tabId).classList.add('show', 'active');
    // Update the search placeholder based on the selected tab
    const searchInput = document.getElementById('searchRequests');
    if (tabId === 'borrowed') {
        searchInput.placeholder = 'Search Books to be Borrowed';
    } else if (tabId === 'returned') {
        searchInput.placeholder = 'Search Books to be Returned';
    } else if (tabId === 'logs') {
        searchInput.placeholder = 'Search Logs';
    }
    // Update the dropdown button text
    document.getElementById('bookStatusDropdown').textContent = tabText;
}

// Set default tab and dropdown text on page load
document.addEventListener('DOMContentLoaded', function() {
    showBookStatusTab(new Event('DOMContentLoaded'), 'borrowed', 'Books to be Borrowed');
});

function toggleUploadForms() {
    const uploadType = document.getElementById('uploadType').value;
    document.getElementById('singleBookUploadForm').style.display = uploadType === 'single' ? 'block' : 'none';
    document.getElementById('batchBookUploadForm').style.display = uploadType === 'batch' ? 'block' : 'none';
}

document.getElementById('uploadForm').addEventListener('submit', function(event) {
    const uploadButton = document.getElementById('uploadButton');
    
    // Disable the upload button
    uploadButton.disabled = true;
    
    // Show the loading modal
    $('#loadingModal').modal({
        backdrop: 'static',
        keyboard: false,
        show: true
    });
});

document.getElementById('uploadForm').addEventListener('submit', function(event) {
    const uploadButton = document.getElementById('uploadButton');
    
    // Disable the upload button
    uploadButton.disabled = true;
    
    // Show the loading modal
    $('#loadingModal').modal({
        backdrop: 'static',
        keyboard: false,
        show: true
    });
});

function submitDeleteForm() {
    var bookId = $('#confirmDeleteBtnBook').data('bookid');
    $('#deleteFormBook-' + bookId).submit();
}

$('#deleteModalBook').on('show.bs.modal', function(event) {
    var button = $(event.relatedTarget);
    var bookId = button.data('bookid');
    $('#confirmDeleteBtnBook').data('bookid', bookId);
});