from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from librarian.models import ApprovedRequest, Books
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from student.forms import PasswordChangeForm
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth import update_session_auth_hash


def home(request):
    all_books = Books.objects.all()
    ebooks = Books.objects.filter(eBook=True)
    research_papers = Books.objects.filter(research_paper=True)
    bookmarked_books = Books.objects.filter(bookmarked_by=request.user)
    borrowed_books = ApprovedRequest.objects.filter(requested_by=request.user)
    
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
        'borrowed_books': borrowed_books,
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
    

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important to keep the user logged in
            messages.success(request, 'Your password was successfully updated!')
            return redirect('home')  # Redirect to home or any other page
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'settings.html', {
        'form': form,
        'user': request.user
    })

from pdf2image import convert_from_path
import os

def preview(request, book_id):
    book = get_object_or_404(Books, id=book_id)

    # Check if the book has a PDF file
    if book.BookFile:
        # Define a path to store the images (or you could use a temporary location)
        output_folder = os.path.join('media', 'book_previews', f'book_{book_id}')
        os.makedirs(output_folder, exist_ok=True)

        # Convert PDF pages to images
        pdf_path = book.BookFile.path
        images = convert_from_path(pdf_path)

        # Save each image and get the URLs
        image_urls = []
        for i, image in enumerate(images):
            image_path = os.path.join(output_folder, f'page_{i + 1}.jpg')
            image.save(image_path, 'JPEG')
            image_urls.append(image_path)

    context = {
        'book': book,
        'image_urls': image_urls
    }

    return render(request, 'preview.html', context)