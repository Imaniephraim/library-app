from django.shortcuts import render, get_object_or_404, redirect
from .models import Book, Member
from .forms import BookForm, MemberForm
import requests
from django.http import JsonResponse

def book_list(request):
    books = Book.objects.all()
    return render(request, 'book_list.html', {'books': books})

def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk)
    return render(request, 'book_detail.html', {'book': book})

def book_add(request):
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('book_list')
    else:
        form = BookForm()
    return render(request, 'book_form.html', {'form': form})

def book_update(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            return redirect('book_detail', pk=pk)
    else:
        form = BookForm(instance=book)
    return render(request, 'book_form.html', {'form': form})

def book_delete(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        book.delete()
        return redirect('book_list')
    return render(request, 'book_confirm_delete.html', {'book': book})

def member_list(request):
    members = Member.objects.all()
    return render(request, 'member_list.html', {'members': members})

def member_detail(request, pk):
    member = get_object_or_404(Member, pk=pk)
    return render(request, 'member_detail.html', {'member': member})

def member_add(request):
    if request.method == 'POST':
        form = MemberForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('member_list')
    else:
        form = MemberForm()
    return render(request, 'member_form.html', {'form': form})

def member_update(request, pk):
    member = get_object_or_404(Member, pk=pk)
    if request.method == 'POST':
        form = MemberForm(request.POST, instance=member)
        if form.is_valid():
            form.save()
            return redirect('member_detail', pk=pk)
    else:
        form = MemberForm(instance=member)
    return render(request, 'member_form.html', {'form': form})

def member_delete(request, pk):
    member = get_object_or_404(Member, pk=pk)
    if request.method == 'POST':
        member.delete()
        return redirect('member_list')
    return render(request, 'member_confirm_delete.html', {'member': member})

def fetch_books_from_api(request):
    url = 'http://flask-api-url/books/'
    response = requests.get(url)
    if response.status_code == 200:
        books = response.json()
        return JsonResponse({'books': books})
    else:
        return JsonResponse({'error': 'Failed to fetch books'}, status=response.status_code)

def add_book_to_api(request):
    if request.method == 'POST':
        url = 'http://flask-api-url/books/'
        data = {
            'title': request.POST.get('title'),
            'author': request.POST.get('author'),
            'publication_date': request.POST.get('publication_date'),
        }
        response = requests.post(url, json=data)
        if response.status_code == 201:
            return JsonResponse({'message': 'Book added successfully'})
        else:
            return JsonResponse({'error': 'Failed to add book'}, status=response.status_code)