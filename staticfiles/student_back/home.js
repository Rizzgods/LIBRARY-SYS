document.addEventListener("DOMContentLoaded", function() {
    // Show placeholder cards for 0.5 seconds before showing actual content
    setTimeout(() => {
        document.getElementById("cards-container").classList.add("hidden");
        document.getElementById("actual-cards-container").classList.remove("hidden");
    }, 500);

    // Restore filter values from URL parameters
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.has('start_year')) {
        document.getElementById('range-start-input').value = urlParams.get('start_year');
    }
    if (urlParams.has('end_year')) {
        document.getElementById('range-end-input').value = urlParams.get('end_year');
    }
    if (urlParams.has('language')) {
        document.getElementById('language-filter').value = urlParams.get('language');
    }
    if (urlParams.has('categories')) {
        const categoryIds = urlParams.get('categories').split(',');
        categoryIds.forEach(id => {
            const checkbox = document.getElementById(`category-${id}`);
            if (checkbox) checkbox.checked = true;
        });
    }
    if (urlParams.has('book_type')) {
        document.getElementById('book-type-filter').value = urlParams.get('book_type');
    }
});

function applyFilters(page = 1) {
    const startYear = document.getElementById('range-start-input').value;
    const endYear = document.getElementById('range-end-input').value;
    const language = document.getElementById('language-filter').value;
    const bookType = document.getElementById('book-type-filter').value;
    const checkedCategories = Array.from(document.querySelectorAll('input[type="checkbox"]:checked'));
    
    // Show loading state
    document.getElementById("cards-container").classList.remove("hidden");
    document.getElementById("actual-cards-container").classList.add("hidden");
    
    const categories = checkedCategories.length > 0 
        ? checkedCategories.map(cb => cb.id.split('-')[1]).join(',')
        : '';

    const url = `/sstudent/?page=${page}&start_year=${startYear}&end_year=${endYear}${language !== 'all' ? `&language=${language}` : ''}${categories ? `&categories=${categories}` : ''}&book_type=${bookType}`;
    
    fetch(url)
        .then(response => response.text())
        .then(html => {
            // Wait for 0.5 seconds before showing results
            setTimeout(() => {
                const parser = new DOMParser();
                const doc = parser.parseFromString(html, 'text/html');
                
                // Get the results container
                const resultsContainer = document.getElementById("actual-cards-container");
                
                // Check if there are any book cards in the response
                const bookCards = doc.querySelectorAll('#actual-cards-container .bg-white');
                
                if (bookCards.length === 0) {
                    // If no books found, show the "No results" message
                    resultsContainer.innerHTML = `
                        <div class="col-span-full text-center text-gray-500 py-8">
                            <p class="text-xl">No books found matching your filters</p>
                            <p class="mt-2">Try adjusting your search criteria</p>
                        </div>
                    `;
                } else {
                    // If books found, update the container with the new content
                    const newContent = doc.querySelector('#actual-cards-container');
                    if (newContent) {
                        resultsContainer.innerHTML = newContent.innerHTML;
                    }
                }
                
                // Update pagination if books were found
                if (bookCards.length > 0) {
                    const newPagination = doc.querySelector('.pagination-controls');
                    const paginationContainer = document.querySelector('.pagination-controls');
                    if (newPagination && paginationContainer) {
                        paginationContainer.innerHTML = newPagination.innerHTML;
                    }
                } else {
                    // Clear pagination if no results
                    const paginationContainer = document.querySelector('.pagination-controls');
                    if (paginationContainer) {
                        paginationContainer.innerHTML = '';
                    }
                }
                
                // Hide loading state
                document.getElementById("cards-container").classList.add("hidden");
                document.getElementById("actual-cards-container").classList.remove("hidden");
            }, 500);
        })
        .catch(error => {
            // Wait for 0.5 seconds before showing error
            setTimeout(() => {
                console.error('Error:', error);
                document.getElementById("actual-cards-container").innerHTML = `
                    <div class="col-span-full text-center text-gray-500 py-8">
                        <p class="text-red-500">Error loading results. Please try again.</p>
                    </div>`;
                document.getElementById("cards-container").classList.add("hidden");
                document.getElementById("actual-cards-container").classList.remove("hidden");
            }, 500);
        });
}

function clearFilters() {
    document.getElementById('range-start-input').value = 1950;
    document.getElementById('range-end-input').value = 2024;
    document.getElementById('language-filter').value = 'all';
    document.getElementById('book-type-filter').value = 'all';  // Add this line
    document.querySelectorAll('input[type="checkbox"]').forEach(cb => cb.checked = false);
    applyFilters();
}

document.addEventListener('click', function(event) {
    if (event.target.matches('.pagination a')) {
        event.preventDefault();
        const page = event.target.getAttribute('data-page');
        applyFilters(page);
    }
});

// Add these functions to your existing JavaScript
function showPreview(bookData) {
  document.getElementById('preview-image').src = bookData.image;
  document.getElementById('preview-title').textContent = bookData.title;
  document.getElementById('preview-author').textContent = bookData.author;
  document.getElementById('preview-date').textContent = bookData.date;
  document.getElementById('preview-categories').innerHTML = bookData.categories;
  
  document.getElementById('preview-overlay').classList.remove('hidden');
  document.getElementById('preview-container').classList.remove('hidden');
  document.body.style.overflow = 'hidden';
}

function closePreview() {
  document.getElementById('preview-overlay').classList.add('hidden');
  document.getElementById('preview-container').classList.add('hidden');
  document.body.style.overflow = 'auto';
}

function showPreviewPage(bookData) {
  // Hide main content
  document.querySelector('.main-content').classList.add('hidden');
  
  // Show preview page
  const previewPage = document.querySelector('.preview-page');
  previewPage.classList.remove('hidden');
  
  // Update preview content
  previewPage.querySelector('.preview-image').src = bookData.image;
  previewPage.querySelector('.preview-title').textContent = bookData.title;
  previewPage.querySelector('.preview-author').textContent = bookData.author;
  previewPage.querySelector('.preview-date').textContent = bookData.date;
  previewPage.querySelector('.preview-description').textContent = bookData.description;
  previewPage.querySelector('.preview-categories').innerHTML = bookData.categories;

  // Scroll to top
  window.scrollTo(0, 0);
}

function closePreviewPage() {
  // Show main content
  document.querySelector('.main-content').classList.remove('hidden');
  
  // Hide preview page
  document.querySelector('.preview-page').classList.add('hidden');
  
  // Scroll to previous position if needed
  window.scrollTo(0, 0);
}