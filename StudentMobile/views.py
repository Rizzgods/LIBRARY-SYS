from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from librarian.models import Books
from django.views.decorators.csrf import csrf_exempt

def home(request):
    all_books = Books.objects.all()
    ebooks = Books.objects.filter(eBook=True)
    research_papers = Books.objects.filter(research_paper=True)
    bookmarked_books = Books.objects.filter(bookmarked_by=request.user)
    
    categories = {
        'Generalities': Books.objects.filter(Category__name='Generalities'),
        'Religion': Books.objects.filter(Category__name='Religion'),
        'Social Sciences': Books.objects.filter(Category__name='Social Sciences'),
        'Language': Books.objects.filter(Category__name='Language'),
        'Science': Books.objects.filter(Category__name='Science'),
        'Technology (Applied Sciences)': Books.objects.filter(Category__name='Technology (Applied Sciences)'),
        'Arts and Recreation': Books.objects.filter(Category__name='Arts and Recreation'),
        'Literature': Books.objects.filter(Category__name='Literature'),
        'History and Geography': Books.objects.filter(Category__name='History and Geography'),
        'Philosophy and Psychology': Books.objects.filter(Category__name='Philosophy and Psychology'),
    }
    
    context = {
        'all_books': all_books,
        'ebooks': ebooks,
        'research_papers': research_papers,
        'categories': categories,
        'bookmarked_books': bookmarked_books,
    }
    return render(request, 'navbar.html', context)

def book_info(request, book_id):
    book = get_object_or_404(Books, id=book_id)
    is_bookmarked = request.user in book.bookmarked_by.all()
    book_data = {
        'BookImage': {'url': book.BookImage.url},
        'BookTitle': book.BookTitle,
        'Author': book.Author,
        'Date': book.Date,
        'Description': book.Description,
        'isBookmarked': is_bookmarked,
    }
    return JsonResponse({'book': book_data})

@csrf_exempt
def toggle_bookmark(request, book_id):
    if request.method == 'POST':
        book = get_object_or_404(Books, id=book_id)
        if request.user in book.bookmarked_by.all():
            book.bookmarked_by.remove(request.user)
            is_bookmarked = False
        else:
            book.bookmarked_by.add(request.user)
            is_bookmarked = True
        book_data = {
            'BookImage': {'url': book.BookImage.url},
            'BookTitle': book.BookTitle,
            'Author': book.Author,
            'Date': book.Date,
            'Description': book.Description,
            'isBookmarked': is_bookmarked,
        }
        return JsonResponse({'book': book_data})