# views.py

from django.shortcuts import render
from librarian.models import Books, Category

def home(request):
    all_books = Books.objects.all()
    ebooks = Books.objects.filter(eBook=True)
    research_papers = Books.objects.filter(research_paper=True)
    
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
    }
    return render(request, 'home.html', context)