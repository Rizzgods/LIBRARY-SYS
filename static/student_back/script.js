document.addEventListener("DOMContentLoaded", function() {
  // Simulate fetching data with a timeout
  setTimeout(fetchBooks, 2000); // Simulate a 2-second delay

  function fetchBooks() {
    // Simulate fetching data from the server
    const books = [
      {
        BookImage: { url: "https://via.placeholder.com/150" },
        BookTitle: "Book 1",
        Author: "Author 1",
        Date: "2023"
      },
      {
        BookImage: { url: "https://via.placeholder.com/150" },
        BookTitle: "Book 2",
        Author: "Author 2",
        Date: "2022"
      },
      {
        BookImage: { url: "https://via.placeholder.com/150" },
        BookTitle: "Book 3",
        Author: "Author 3",
        Date: "2021"
      },
      {
        BookImage: { url: "https://via.placeholder.com/150" },
        BookTitle: "Book 4",
        Author: "Author 4",
        Date: "2020"
      }
    ];

    // Update the cards container with the fetched books
    const cardsContainer = document.getElementById("cards-container");
    cardsContainer.innerHTML = books.map(book => `
      <div class="bg-white shadow rounded-lg flex flex-col h-128">
        <div class="flex-shrink-0">
          <img src="${book.BookImage.url}" alt="${book.BookTitle}" class="w-full h-72 object-cover rounded-t-md">
        </div>
        <div class="p-4 flex-grow">
          <h3 class="mt-1 font-bold">${book.BookTitle}</h3>
          <p class="text-sm text-gray-600">Author(s): ${book.Author}</p>
          <p class="text-sm text-gray-600">Publication: ${book.Date}</p>
        </div>
      </div>
    `).join('');
  }
});