let pdfDoc = null;
    let pageNum = 1;
    let scale = 1.0;
    let isDragging = false;
    let startX, startY, scrollLeft, scrollTop;
    let utterance = null;
    let recognition = null;
    let currentX = 0, currentY = 0;
    let xOffset = 0, yOffset = 0;

    const zoomStep = 0.1; // Step size for each scroll event
    const minScale = 0.25; // Minimum zoom scale
    const maxScale = 4.0; // Maximum zoom scale

    const canvas = document.createElement("canvas");
    const ctx = canvas.getContext("2d");
    const pdfContainer = document.getElementById("pdf-container");
    const pageCounter = document.getElementById("page-counter");
    const pageInput = document.getElementById("page-input");
    

    // Function to handle zooming in and out based on scroll direction
    function handleScrollZoom(e) {
        e.preventDefault(); // Prevent default scroll behavior

        // Check scroll direction and adjust scale
        if (e.deltaY < 0) {
            // Scrolled up -> zoom in
            if (scale < maxScale) {
                scale += zoomStep;
            }
        } else {
            // Scrolled down -> zoom out
            if (scale > minScale) {
                scale -= zoomStep;
            }
        }

        // Re-render the page with the updated scale
        renderPage(pageNum, scale);
    }

        // Function to speak command success message
        function speakCommandSuccess(message) {
            utterance = new SpeechSynthesisUtterance(message);
            speechSynthesis.speak(utterance);
        }   
    
        function nextPage() {
            stopReading(); // Stop TTS before navigating
            if (pageNum < pdfDoc.numPages) {
                pageNum++;
                renderPage(pageNum, scale, false); // Set shouldRead to false
                
            }
        }
    
        function prevPage() {
            stopReading(); // Stop TTS before navigating
            if (pageNum > 1) {
                pageNum--;
                renderPage(pageNum, scale, false); // Set shouldRead to false
                
            }
        }
    
        function renderPage(pageNum, scale, shouldRead = false) {
            pdfDoc.getPage(pageNum).then(function(page) {
                const viewport = page.getViewport({ scale: scale });
                canvas.height = viewport.height;
                canvas.width = viewport.width;
        
                // Center the canvas
                canvas.style.display = 'block';
                canvas.style.margin = '0 auto';
                canvas.style.padding = '50px';
        
                const renderContext = {
                    canvasContext: ctx,
                    viewport: viewport
                };
                page.render(renderContext).promise.then(() => {
                    // Add watermark
                    ctx.save();
                    ctx.setTransform(1, 0, 0, 1, 0, 0); // Reset any transformations
                    ctx.font = `${30}px Arial`; // Base font size
                    ctx.fillStyle = "rgba(255, 0, 0, 0.3)";
                    ctx.textAlign = "center";
                    ctx.translate(canvas.width / 2, canvas.height / 2);
                    ctx.rotate(-Math.PI / 4);
                    ctx.scale(scale, scale); // Scale the watermark based on the zoom level
                    ctx.fillText("PROPERTY OF LAWANG BATO NATIONAL HIGH SCHOOL", 0, 0);
                    ctx.restore();
        
                    if (!pdfContainer.contains(canvas)) {
                        pdfContainer.appendChild(canvas);
                    }
                });
                page.getTextContent().then(function(textContent) {
                    const textItems = textContent.items;
                    let finalText = '';
                    for (let i = 0; i < textItems.length; i++) {
                        finalText += textItems[i].str + ' ';
                    }
                    canvas.setAttribute('data-text', finalText);
                    if (shouldRead) {
                        readPage();
                    }
                });
            }).catch(error => {
                console.error('Error rendering page:', error);
            });
            pageCounter.textContent = `${pageNum} / ${pdfDoc.numPages}`;
            pageInput.value = pageNum;
        }
        
        
    
        function readPage() {
            const text = canvas.getAttribute('data-text');
            if (text) {
                if (utterance) {
                    speechSynthesis.cancel(); // Cancel any ongoing speech
                }
                utterance = new SpeechSynthesisUtterance(text);
                speechSynthesis.speak(utterance);
                $('#notification').fadeIn(); // Show the notification
                setTimeout(function() {
                    $('#notification').fadeOut(); // Hide the notification after a delay
                }, 3000); // 3000 milliseconds = 3 seconds
            } else {
                console.error('No text found to read.');
            }
        }
    
        function stopReading() {
            if (speechSynthesis.speaking) {
                speechSynthesis.cancel();
            }
        }
    
        function zoomOut() {
            if (scale > 0.25) {
                scale -= 0.25;
                renderPage(pageNum, scale);
            }
        }
    
        function zoomIn() {
            if (scale < 4.0) {
                scale += 0.25;
                renderPage(pageNum, scale);
            }
        }
    
// Ensure dragging is only done on the canvas inside the pdfContainer
function startDragging(e) {
    if (e.target.tagName !== "CANVAS") return;  // Only allow dragging when the target is the canvas

    isDragging = true;
    pdfContainer.style.cursor = 'grabbing';

    // Get the starting positions of the mouse relative to the current offset
    startX = e.pageX - xOffset;
    startY = e.pageY - yOffset;

    e.preventDefault();  // Prevent text selection or default behavior
    e.stopPropagation(); // Prevent event propagation to other elements
}

function stopDragging(e) {
    if (!isDragging) return;  // Only stop if dragging is in progress

    isDragging = false;
    pdfContainer.style.cursor = 'grab';

    // Update offsets based on the current position
    xOffset = currentX;
    yOffset = currentY;

    e.preventDefault();
    e.stopPropagation();
}

function drag(e) {
    if (!isDragging) return;  // Do nothing if we're not dragging

    // Calculate the new position based on the mouse movement
    currentX = e.pageX - startX;
    currentY = e.pageY - startY;

    // Move the canvas by translating its position
    canvas.style.transform = `translate(${currentX}px, ${currentY}px)`;  // Apply dragging only to the canvas

    e.preventDefault();  // Prevent text selection or default behavior
    e.stopPropagation(); // Prevent event propagation
}

// Attach event listeners to the pdfContainer for the canvas
pdfContainer.addEventListener('mousedown', startDragging);
pdfContainer.addEventListener('mousemove', drag);
pdfContainer.addEventListener('mouseup', stopDragging);
pdfContainer.addEventListener('mouseleave', stopDragging);

    
        function jumpToPage(e) {
            if (e.key === 'Enter') {
                const page = parseInt(pageInput.value);
                if (page > 0 && page <= pdfDoc.numPages) {
                    pageNum = page;
                    renderPage(pageNum, scale);
                }
            }
        }
    
        function togglePauseResume() {
            const button = document.getElementById('pauseResumeButton');
            if (speechSynthesis.speaking) {
                if (speechSynthesis.paused) {
                    speechSynthesis.resume(); // If paused, resume
                    button.textContent = "pause";
                } else {
                    speechSynthesis.pause(); // If speaking, pause
                    button.textContent = "resume";
                }
            }
        }

        function goToPage(pageNumber) {
            stopReading(); // Stop TTS before navigating
            if (pageNumber >= 1 && pageNumber <= pdfDoc.numPages) {
                pageNum = pageNumber;
                renderPage(pageNum, scale, false); // Set shouldRead to false
            } else {
                console.error('Invalid page number:', pageNumber);
            }
        }

        // Add CSS transition
        document.addEventListener('DOMContentLoaded', function() {
            const button = document.getElementById('pauseResumeButton');
            button.style.transition = "all 0.3s ease";
        });
    
        window.addEventListener('beforeunload', function() {
            stopReading();
        });
    
        pdfjsLib.getDocument("{{ book.BookFile.url }}").promise.then(function(pdf) {
            pdfDoc = pdf;
            renderPage(pageNum, scale);
        }).catch(error => {
            console.error('Error loading PDF:', error);
        });
    
        // Speech recognition setup
        if ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window) {
            recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
            recognition.lang = 'en-US'; // Set language to English
            recognition.continuous = false; // Stop listening after one phrase is recognized
    
            recognition.onresult = function(event) {
                const transcript = event.results[0][0].transcript.trim().toLowerCase();
                console.log('Recognized:', transcript);
                if (transcript === 'next.') {
                    nextPage();
                    speakCommandSuccess('Next page navigated.');
                } else if (transcript === 'stop.') {
                    stopReading();
                    speakCommandSuccess('Reading stopped.');
                } else if (transcript === 'read.') {
                    readPage();
                    speakCommandSuccess('Reading started.');
                } else if (transcript === 'previous.') {
                    prevPage();
                    speakCommandSuccess('Previous page navigated.');
                } else if (transcript.startsWith('go to page')) {
                    const words = transcript.split(' ');
                    const pageNumberIndex = words.indexOf('page') + 1; // Find the index of the word "page"
                    if (pageNumberIndex !== 0 && pageNumberIndex < words.length) {
                        const pageNumber = parseInt(words[pageNumberIndex]);
                        if (!isNaN(pageNumber)) {
                            goToPage(pageNumber);
                            speakCommandSuccess(`Navigated to page ${pageNumber}.`);
                        } else {
                            console.error('Invalid page number:', words[pageNumberIndex]);
                        }
                    } else {
                        console.error('Page number not found in transcript:', transcript);
                    }
                }
                else if (transcript === 'pause.' || 'wait.') {
                    speakCommandSuccess('Reading pause');
                    togglePauseResume();
                    
                } else if (transcript === 'resume.' || 'go on.') {
                    speakCommandSuccess('Reading continue');
                    togglePauseResume();
                    
                }
                else if (transcript === 'zoom in.' || 'in.') {
                    zoomIn();
                    speakCommandSuccess('Zooming In');
                }
                else if (transcript === 'zoom out.') {
                    zoomOut();
                    speakCommandSuccess('Zooming out');
                }
            };
    
            recognition.onerror = function(event) {
                console.error('Speech recognition error:', event.error);
            };
    
            recognition.onend = function() {
                // Restart recognition after it ends
                recognition.start();
            };
    
            // Start recognition
            recognition.start();
        } else {
            console.error('Speech recognition not supported in this browser.');
        }

        // notif js
        $(document).ready(function() {
            var showingMore = false; // Track the current state of the "See More"/"See Less" toggle
            var notifications = [];  // Store notification data locally
        
            function fetchNotifications() {
                $.get("{% url 'fetch_notifications' %}", function(data) {
                    notifications = data; // Save the fetched data to the local variable
                    renderNotifications(); // Call the render function
                });
            }
        
            function renderNotifications() {
                $('#notification-dropdown').empty();
                
                if (notifications.length > 0) {
                    $('#notification-count').text(notifications.length).show();
                    $('#no-notifications').hide();
        
                    var markAllButton = $('<div class="dropdown-header">')
                        .html('<button id="mark-all-read" class="btn btn-link notif-btn">Mark All as Read</button>');
                    $('#notification-dropdown').append(markAllButton);
        
                    $('#mark-all-read').click(function(event) {
                        event.stopPropagation();
                        markAllAsRead();
                    });
        
                    // Determine how many notifications to display based on the "See More" state
                    var notificationsToShow = showingMore ? notifications.length : 5;
        
                    var limitedNotifications = notifications.slice(0, notificationsToShow);
                    limitedNotifications.forEach(function(notification) {
                        var item = $('<div class="dropdown-item">')
                            .html(`
                                    <a href="{% url 'borrowed_books' %}" class="notif-link">
                                        <div class="notification-icon-2">
                                            <span class="material-symbols-outlined icon-2">notification_important</span>
                                        </div>
                                        <div class="notif-message">
                                            ${notification.message}
                                            <div class="notification-time">${new Date(notification.created_at).toLocaleString()}</div>
                                        </div>
                                    </a>
                            `)
                            .attr('data-id', notification.id)
                            .toggleClass('read', notification.read)  // Use the local "read" state
                            .click(function() {
                                markAsRead(notification.id);
                            });
        
                        var deleteButton = $('<button class="btn btn-close ms-auto">')
                            .html('')
                            .click(function(event) {
                                event.stopPropagation();
                                deleteNotification(notification.id);
                            });
        
                        item.append(deleteButton);
                        $('#notification-dropdown').append(item);
                    });
        
                    // Re-append the "Mark All as Read" button
                    $('#notification-dropdown').prepend(markAllButton);
        
                    // Add "See More" button if there are more than 5 notifications
                    if (notifications.length > 5) {
                        var seeMoreBtn = $('<button id="see-more-btn" class="btn btn-link notif-btn">See More</button>');
                        var seeMoreContainer = $('<div class="dropdown-footer">').append(seeMoreBtn);
                        $('#notification-dropdown').append(seeMoreContainer);
        
                        // Set the text of the button based on the current state
                        seeMoreBtn.text(showingMore ? 'See Less' : 'See More');
        
                        // Prevent the dropdown from closing when clicking "See More" or "See Less"
                        seeMoreBtn.on('click', function(event) {
                            event.stopPropagation();  // Prevent dropdown from closing
        
                            showingMore = !showingMore; // Toggle the state
                            renderNotifications(); // Re-render the notifications based on the new state
                        });
                    }
                } else {
                    $('#notification-dropdown').html('<span class="dropdown-item-text no-notif" id="no-notifications">No notifications</span>');
                    $('#notification-count').hide();
                }
            }
        
            function markAsRead(notificationId) {
                $.post("{% url 'mark_notification_read' 0 %}".replace('0', notificationId), {
                    csrfmiddlewaretoken: '{{ csrf_token }}'
                }, function() {
                    // Find the notification in the local array and mark it as read
                    var notification = notifications.find(function(notif) {
                        return notif.id === notificationId;
                    });
                    if (notification) {
                        notification.read = true; // Update the local state
                    }
                    renderNotifications(); // Re-render the notifications
                });
            }
        
            function markAllAsRead() {
                $.post("{% url 'mark_all_notifications_read' %}", {
                    csrfmiddlewaretoken: '{{ csrf_token }}'
                }, function() {
                    // Update all notifications locally to be marked as read
                    notifications.forEach(function(notification) {
                        notification.read = true; // Update local state
                    });
                    renderNotifications(); // Re-render the notifications
                });
            }
        
            function deleteNotification(notificationId) {
                $.post("{% url 'delete_notification' 0 %}".replace('0', notificationId), {
                    csrfmiddlewaretoken: '{{ csrf_token }}'
                }, function() {
                    // Remove the notification from the local array
                    notifications = notifications.filter(function(notif) {
                        return notif.id !== notificationId;
                    });
                    renderNotifications(); // Re-render the notifications
                });
            }
        
            $('#notification-bell').on('click', function() {
                $('#notification-dropdown').toggle(); // Toggle visibility
        
                // Fetch and render notifications only if the dropdown is being shown
                if ($('#notification-dropdown').is(':visible')) {
                    fetchNotifications();
                }
            });
        
            setInterval(fetchNotifications, 60000); // Fetch every 60 seconds
            fetchNotifications();
        
            $(document).click(function(event) {
                if (!$(event.target).closest('#notification-bell').length && !$(event.target).closest('#notification-dropdown').length) {
                    $('#notification-dropdown').hide(); // Hide the dropdown when clicking outside
                }
            });
        });