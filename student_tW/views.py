from django.shortcuts import render
from django.core.paginator import Paginator
from librarian.models import Books, LANGUAGE_CHOICES, Category

def sstudent(request):
    start_year = request.GET.get('start_year')
    end_year = request.GET.get('end_year')
    language = request.GET.get('language')
    categories_filter = request.GET.get('categories')

    books = Books.objects.all()

    if start_year and start_year.isdigit():
        books = books.filter(Date__year__gte=int(start_year))
    
    if end_year and end_year.isdigit():
        books = books.filter(Date__year__lte=int(end_year))
    
    if language and language != 'all':
        books = books.filter(Language=language)
    
    if categories_filter:
        try:
            # Split the category string and filter only valid numbers
            category_ids = [int(cat) for cat in categories_filter.split(',') if cat.strip().isdigit()]
            if category_ids:
                # Use distinct() to avoid duplicate books when filtering by multiple categories
                books = books.filter(Category__id__in=category_ids).distinct()
        except ValueError:
            pass

    paginator = Paginator(books, 15) 
    page_number = request.GET.get('page', 1)
    books_page = paginator.get_page(page_number)

    languages = LANGUAGE_CHOICES
    categories = Category.objects.all()

    context = {
        'books_page': books_page,
        'languages': languages,
        'categories': categories,
        'start_year': start_year or '',
        'end_year': end_year or '',
        'language': language or 'all',
        'categories_filter': categories_filter or ''
    }

    return render(request, 's_main.html', context)