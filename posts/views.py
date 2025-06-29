from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import Post
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from . import forms
from taggit.models import Tag
import json
from .models import Outfit
# Create your views here.

@login_required
def posts_list(request):
    # posts = Post.objects.all().order_by('-date')
    # return render(request, 'posts/posts_list.html', {'posts': posts})
    tag = request.GET.get('tag')
    tags = Tag.objects.all()
    if tag:
        # posts = Post.objects.filter(author=request.user, tags__name__in=[tag])
        posts = Post.objects.filter(author=request.user, tags__name=tag)
    else:
        posts = Post.objects.filter(author=request.user)
    
    return render(request, 'posts/posts_list.html', {'posts': posts, 'user': request.user, 'selected_tag': tag, 'tags': tags})

# def post_page(request, slug):
#     post = Post.objects.get(slug=slug)
#     return render(request, 'posts/post_page.html', {'post': post})

def post_page(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'posts/post_page.html', {'post': post})

@login_required(login_url= "/users/login/")
def post_new(request):
    if request.method == "POST":
        form = forms.CreatePost(request.POST, request.FILES)
        if form.is_valid():
            newpost = form.save(commit=False)
            newpost.author = request.user
            newpost.save()
            form.save_m2m() #to save tags as commit=False skips saving related many-to-many fields
            return redirect('posts:list')
            
    else:
        form = forms.CreatePost()
    return render(request, 'posts/post_new.html', {'form': form})
    