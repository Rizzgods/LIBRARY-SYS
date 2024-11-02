$(document).ready(function(){
    $('.owl-carousel').owlCarousel({
        loop: true,
        margin: 10,
        nav: true,
        navText: [
            '<span class="material-symbols-outlined">arrow_back_ios</span>',
            '<span class="material-symbols-outlined">arrow_forward_ios</span>'
        ],
        responsive: {
            0: {
                items: 2.5
            },
            600: {
                items: 2.5
            },
            1000: {
                items: 5
            }
        }
    });

    document.querySelectorAll('.nav-link').forEach(tab => {
        tab.addEventListener('click', function() {
            const contentToShow = this.getAttribute('aria-controls');
            let targetHash = '';

            switch(contentToShow) {
                case 'home_content':
                    targetHash = '#home';
                    break;
                case 'bookmark_content':
                    targetHash = '#bookmark';
                    break;
                case 'history_content':
                    targetHash = '#history';
                    break;
                case 'settings_content':
                    targetHash = '#settings';
                    break;
                default:
                    targetHash = '#home';
            }

            history.pushState(null, '', targetHash);
            showContentBasedOnHash();
        });
    });

    document.querySelectorAll('.card').forEach(card => {
        card.addEventListener('click', function() {
            const bookId = this.getAttribute('data-book-id');
            fetchBookInfo(bookId);
        });
    });

    function fetchBookInfo(bookId) {
        $.ajax({
            url: `/StudentMobile/home/book/${bookId}/`,
            method: 'GET',
            success: function(response) {
                const bookInfo = response.book;

                // Store book details in localStorage
                localStorage.setItem('lastBook', JSON.stringify(bookInfo));

                // Update the info_content section with the fetched book info
                updateInfoContent(bookInfo);

                // Show the info_content section
                document.querySelectorAll('.content-section').forEach(section => section.classList.add('hidden'));
                document.getElementById('info_content').classList.remove('hidden');
                history.pushState(null, '', `#book-${bookId}`);
                setActiveTab('');
            }
        });
    }

    function updateInfoContent(bookInfo) {
        document.querySelector('#info_content img').src = bookInfo.BookImage.url;
        document.querySelector('#info_content .title').textContent = bookInfo.BookTitle;
        document.querySelector('#info_content .author').textContent = `Author: ${bookInfo.Author}`;
        document.querySelector('#info_content .date').textContent = `Date: ${bookInfo.Date}`;
        document.querySelector('#info_content .description').textContent = `Description: ${bookInfo.Description}`;
        

        const viewButton = document.querySelector('#info_content .view-button');
        viewButton.setAttribute('data-book-id', bookInfo.id);
        viewButton.addEventListener('click', function() {
            redirectToPreview(this);
        });

        const bookmarkButton = document.querySelector('#info_content .bookmark-button');
        if (bookInfo.isBookmarked) {
            bookmarkButton.innerHTML = '<i class="fas fa-bookmark"></i> Unbookmark';
            bookmarkButton.classList.add('bookmarked');
        } else {
            bookmarkButton.innerHTML = '<i class="far fa-bookmark"></i> Bookmark';
            bookmarkButton.classList.remove('bookmarked');
        }

        bookmarkButton.addEventListener('click', function() {
            toggleBookmark(bookInfo.id);
        });
    }

    function redirectToPreview(button) {
        // Retrieve the book ID from the data attribute of the button
        const bookId = button.getAttribute('data-book-id');

        // Redirect to the preview URL
        window.location.href = `/StudentMobile/preview/${bookId}/`;
    }

    function toggleBookmark(bookId) {
        $.ajax({
            url: `/StudentMobile/home/book/${bookId}/bookmark/`,
            method: 'POST',
            data: {
                'csrfmiddlewaretoken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            success: function(response) {
                const bookInfo = response.book;
                updateInfoContent(bookInfo);
            }
        });
    }

    function setActiveTab(tabId) {
        document.querySelectorAll('.nav-link').forEach(t => t.classList.remove('active'));
        if (tabId) {
            document.getElementById(tabId).classList.add('active');
        }
    }

    // Function to show content based on the URL hash
    function showContentBasedOnHash() {
        const currentHash = window.location.hash;

        document.querySelectorAll('.content-section').forEach(section => section.classList.add('hidden'));

        if (currentHash.startsWith('#book-')) {
            const lastBook = JSON.parse(localStorage.getItem('lastBook'));
            if (lastBook) {
                updateInfoContent(lastBook);
            }
            document.getElementById('info_content').classList.remove('hidden');
            setActiveTab('');
        } else if (currentHash === '#bookmark') {
            document.getElementById('bookmark_content').classList.remove('hidden');
            setActiveTab('bookmark-tab');
        } else if (currentHash === '#history') {
            document.getElementById('history_content').classList.remove('hidden');
            setActiveTab('borrow-history-tab');
        } else if (currentHash === '#settings') {
            document.getElementById('settings_content').classList.remove('hidden');
            setActiveTab('settings-tab');
        } else {
            document.getElementById('home_content').classList.remove('hidden');
            setActiveTab('home-tab');
        }
    }

    // Show content based on the initial URL hash
    showContentBasedOnHash();

    // Handle browser back/forward buttons
    window.addEventListener('popstate', showContentBasedOnHash);
});