async function fetchBorrowRequests() {
    try {
        const response = await fetch('/api/borrow-requests/');
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        const data = await response.json();
        updateRequests('pendingRequestsContainer', data.borrow_requests, false);
        updateRequests('approvedRequestsContainer', data.approved_requests, 'approved');
        updateRequests('declinedRequestsContainer', data.declined_requests, 'declined');
    } catch (error) {
        console.error('Error fetching borrow requests:', error);
    }
}
function showAlert(message, type) {
    const alertContainer = document.getElementById('alertContainer'); // Make sure this container exists in your HTML
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.role = 'alert';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="close" data-dismiss="alert" aria-label="Close">
            <span aria-hidden="true">&times;</span>
        </button>
    `;
    alertContainer.appendChild(alertDiv);

    // Automatically remove the alert after a few seconds
    setTimeout(() => {
        alertDiv.classList.remove('show');
        alertDiv.classList.add('fade');
        setTimeout(() => alertDiv.remove(), 150); // Remove after fade out
    }, 5000); // Adjust the time as needed
}
async function approveRequest(requestId) {
    try {
        console.log(`Approving request ID: ${requestId}`); // Debug log

        // Disable the approve button
        const approveButton = document.querySelector(`#approveModal${requestId} .btn-success`);
        approveButton.disabled = true;

        // Close the approval modal
        $(`#approveModal${requestId}`).modal('hide');

        // Show loading modal
        $('#loadingModal').modal('show');

        const response = await fetch(`/borrow_requests/approve/${requestId}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            },
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.message || 'An unexpected error occurred.');
        }

        console.log('Approval successful:', data.message);
        alert(data.message); // Show a success message

        // Refresh the borrow requests
        fetchBorrowRequests();
    } catch (error) {
        console.error('Error approving request:', error);
        alert(`Approval failed: ${error.message}`);
    } finally {
        // Hide loading modal
        $('#loadingModal').modal('hide');

        // Re-enable the approve button in case of failure
        const approveButton = document.querySelector(`#approveModal${requestId} .btn-success`);
        if (approveButton) {
            approveButton.disabled = false;
        }
    }
}
function updateRequests(containerId, requests, requestType = false) {
    const container = document.getElementById(containerId);
    container.innerHTML = '';

    if (requests.length === 0) {
        container.innerHTML = '<div class="alert alert-warning">No requests at the moment.</div>';
        return;
    }

    const table = document.createElement('table');
    table.className = 'table table-striped';
    const thead = document.createElement('thead');
    thead.className = 'thead-light';
    const tbody = document.createElement('tbody');

    const headers = ['Book', 'Requested By', 'Requested At', 'Expires At', 'File Type', 'Action'];
    const headerRow = document.createElement('tr');
    headers.forEach(header => {
        const th = document.createElement('th');
        th.textContent = header;
        headerRow.appendChild(th);
    });
    thead.appendChild(headerRow);

    function formatDate(dateString) {
        if (!dateString) return 'N/A';
        const date = new Date(dateString);
        return date.toISOString().split('T')[0]; // This will give you YYYY-MM-DD
    }
    requests.forEach(request => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${request.book_title}</td>
            <td>${request.requested_by_name}</td>
            <td>${formatDate(request.requested_at)}</td>
            <td>${formatDate(request.expires_at)}</td>
            <td>${request.file_type}</td>
            <td>
                ${!requestType ? `
                <button type="button" class="btn btn-success" data-toggle="modal" data-target="#approveModal${request.id}">Approve</button>
                <button type="button" class="btn btn-danger" data-toggle="modal" data-target="#declineModal${request.id}">Decline</button>
                ` : ''}
                ${requestType === 'approved' ? `<button type="button" class="btn btn-danger" data-toggle="modal" data-target="#deleteApprovedModal${request.id}">Delete</button>` : ''}
                ${requestType === 'declined' ? `<button type="button" class="btn btn-danger" data-toggle="modal" data-target="#deleteDeclinedModal${request.id}">Delete</button>` : ''}
            </td>
        `;
        tbody.appendChild(row);

    // Approve modal for pending requests
    if (!requestType) {
        document.body.insertAdjacentHTML('beforeend', `
            <div class="modal fade" id="approveModal${request.id}" tabindex="-1" role="dialog" aria-labelledby="approveModalLabel${request.id}" aria-hidden="true">
                <div class="modal-dialog" role="document">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title" id="approveModalLabel${request.id}">Approve Request</h5>
                            <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                                <span aria-hidden="true">&times;</span>
                            </button>
                        </div>
                        <div class="modal-body">
                            Are you sure you want to approve this request?
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-dismiss="modal">Cancel</button>
                            <button type="button" class="btn btn-success" onclick="approveRequest(${request.id})">Approve</button>
                        </div>
                    </div>
                </div>
            </div>
        `);
    }
    
        // Decline modal for pending requests
        if (!requestType) {
            document.body.insertAdjacentHTML('beforeend', `
                <div class="modal fade" id="declineModal${request.id}" tabindex="-1" role="dialog" aria-labelledby="declineModalLabel${request.id}" aria-hidden="true">
                    <div class="modal-dialog" role="document">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title" id="declineModalLabel${request.id}">Decline Request</h5>
                                <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                                    <span aria-hidden="true">&times;</span>
                                </button>
                            </div>
                            <div class="modal-body">
                                <p>This action cannot be reversed</p>
                                <div class="form-group">
                                    <label for="declineReason${request.id}">Select a reason for declining:</label>
                                    <select class="form-control" id="declineReason${request.id}" name="decline_reason" required onchange="toggleOtherReason(${request.id})">
                                        <option value="" disabled selected>Select a reason</option>
                                        <option value="out_of_stock">Out of Stock</option>
                                        <option value="book_not_available">Book Not Available</option>
                                        <option value="invalid_request">Invalid Request</option>
                                        <option value="other">Other</option>
                                    </select>
                                </div>
                                <div class="form-group" id="otherReasonContainer${request.id}" style="display: none;">
                                    <label for="otherReasonInput${request.id}">Please specify:</label>
                                    <input type="text" class="form-control" id="otherReasonInput${request.id}" name="other_reason">
                                </div>
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" data-dismiss="modal">Cancel</button>
                                <form method="post" action="/borrow_requests/decline/${request.id}/">
                                    <input type="hidden" name="csrfmiddlewaretoken" value="${getCsrfToken()}">
                                    <input type="hidden" id="declineReasonInput${request.id}" name="decline_reason_input">
                                    <button type="submit" class="btn btn-danger" 
                                            onclick="
                                                let reasonValue = document.getElementById('declineReason${request.id}').value;
                                                let otherReasonValue = document.getElementById('otherReasonInput${request.id}').value;
                                                document.getElementById('declineReasonInput${request.id}').value = (reasonValue === 'other' && otherReasonValue.trim() !== '') 
                                                    ? otherReasonValue 
                                                    : reasonValue;
                                            ">
                                        Decline
                                    </button>
                                </form>
                            </div>
                        </div>
                    </div>
                </div>
            `);
        }

        // Delete modal for approved requests
        if (requestType === 'approved') {
            document.body.insertAdjacentHTML('beforeend', `
                <div class="modal fade" id="deleteApprovedModal${request.id}" tabindex="-1" role="dialog" aria-labelledby="deleteApprovedModalLabel${request.id}" aria-hidden="true">
                    <div class="modal-dialog" role="document">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title" id="deleteApprovedModalLabel${request.id}">Delete Approved Request</h5>
                                <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                                    <span aria-hidden="true">&times;</span>
                                </button>
                            </div>
                            <div class="modal-body">
                                Are you sure you want to delete this approved request?
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" data-dismiss="modal">Cancel</button>
                                <form method="post" action="/delete_approved_request/${request.id}/">
                                    <input type="hidden" name="csrfmiddlewaretoken" value="${getCsrfToken()}">
                                    <button type="submit" class="btn btn-danger">Delete</button>
                                </form>
                            </div>
                        </div>
                    </div>
                </div>
            `);
        }

        // Delete modal for declined requests
        if (requestType === 'declined') {
            document.body.insertAdjacentHTML('beforeend', `
                <div class="modal fade" id="deleteDeclinedModal${request.id}" tabindex="-1" role="dialog" aria-labelledby="deleteDeclinedModalLabel${request.id}" aria-hidden="true">
                    <div class="modal-dialog" role="document">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title" id="deleteDeclinedModalLabel${request.id}">Delete Declined Request</h5>
                                <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                                    <span aria-hidden="true">&times;</span>
                                </button>
                            </div>
                            <div class="modal-body">
                                Are you sure you want to delete this declined request?
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" data-dismiss="modal">Cancel</button>
                                <form method="post" action="/delete_declined_request/${request.id}/">
                                    <input type="hidden" name="csrfmiddlewaretoken" value="${getCsrfToken()}">
                                    <button type="submit" class="btn btn-danger">Delete</button>
                                </form>
                            </div>
                        </div>
                    </div>
                </div>
            `);
        }
    });

    table.appendChild(thead);
    table.appendChild(tbody);
    container.appendChild(table);
}


function validateDeclineForm(requestId) {
    const selectBox = document.getElementById(`declineReason${requestId}`);
    const otherReasonInput = document.getElementById(`otherReasonInput${requestId}`);
    
    if (selectBox.value === 'other' && otherReasonInput.value.trim() === '') {
        alert("Please specify a reason if you selected 'Other'.");
        return false;
    }
    return true;
}

function toggleOtherReason(requestId) {
    const selectBox = document.getElementById(`declineReason${requestId}`);
    const otherReasonContainer = document.getElementById(`otherReasonContainer${requestId}`);
    
    if (selectBox.value === 'other') {
        otherReasonContainer.style.display = 'block';
    } else {
        otherReasonContainer.style.display = 'none';
    }
}

function getCsrfToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]').value;
}

function fetchRequests() {
    // Get the search input and the active tab
    const input = document.getElementById('requestsSearch').value.toLowerCase();
    const activeTab = document.querySelector('.tab-pane.show.active').id;
    let table;

    // Determine which table to filter based on the active tab
    if (activeTab === 'pending') {
        table = document.querySelectorAll('#pendingRequestsContainer tbody tr');
    } else if (activeTab === 'approved') {
        table = document.querySelectorAll('#approvedRequestsContainer tbody tr');
    } else if (activeTab === 'declined') {
        table = document.querySelectorAll('#declinedRequestsContainer tbody tr');
    }

    // Filter the rows in the determined table
    table.forEach(row => {
        const text = row.textContent.toLowerCase();
        row.style.display = text.includes(input) ? '' : 'none';
    });
}

function selectTab(tabId, tabName) {
    document.querySelectorAll('.tab-pane').forEach(tab => {
        tab.classList.remove('show', 'active');
    });
    document.getElementById(tabId).classList.add('show', 'active');

    document.querySelectorAll('.input-group input').forEach(input => {
        input.style.display = 'none';
    });
    document.getElementById(`requestsSearch`).style.display = 'block';
}

// Fetch borrow requests every 10 seconds
setInterval(fetchBorrowRequests, 10000);

// Initial fetch
fetchBorrowRequests();