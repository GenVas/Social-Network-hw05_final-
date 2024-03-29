from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from yatube.settings import POSTS_ON_PAGE, POSTS_ON_PROFILE_PAGE

from .forms import CommentForm, PostForm
from .models import Comment, Follow, Group, Post, User

NEW_POST_SUBMIT_TITLE = "Добавить запись"
NEW_POST_SUBMIT_BUTTON = "Добавить"
EDIT_POST_SUBMIT_TITLE = "Изменить запись"
EDIT_POST_SUBMIT_BUTTON = "Сохранить"


def index(request):
    post_list = Post.objects.all().select_related('group')
    paginator = Paginator(post_list, POSTS_ON_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'index.html',
        {'page': page, }
    )


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    paginator = Paginator(post_list, POSTS_ON_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, "group.html", {"group": group, "page": page})


@login_required
def new_post(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if not form.is_valid():
        return render(request,
                      "new.html", {"form": form,
                                   "html_title": NEW_POST_SUBMIT_TITLE,
                                   "submit": NEW_POST_SUBMIT_BUTTON})
    post = form.save(commit=False)
    post.author = request.user
    form.save()
    return redirect("index")


def profile(request, username):
    author = get_object_or_404(User, username=username)
    # posts = Post.objects.filter(author=author)
    posts = author.posts.all()
    paginator = Paginator(posts, POSTS_ON_PROFILE_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    following = (request.user.is_authenticated
                 and Follow.objects.filter(user=request.user,
                                           author=author).exists())
    followers = author.following.all()
    followings = author.follower.all()
    return render(request, 'profile.html', {'author': author,
                                            'page': page,
                                            'following': following,
                                            'followers': followers,
                                            'followings': followings
                                            }
                  )


def post_view(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        new_comment = form.save(commit=False)
        new_comment.author = request.user
        new_comment.post = post
        new_comment.save()
    comments = post.comments.all()
    context = {
        'post': post,
        'author': post.author,
        'form': form,
        'comments': comments,
    }
    return render(request, 'post.html', context)


@login_required
def post_edit(request, username, post_id):
    if username != request.user.username:
        return redirect('post', username=username, post_id=post_id)
    post = get_object_or_404(Post, pk=post_id, author__username=username)
    form = PostForm(instance=post,
                    data=request.POST or None,
                    files=request.FILES or None)
    if form.is_valid():
        form.save()
        return redirect('post', username=username, post_id=post_id)
    return render(request, 'new.html', {'form': form,
                                        'post': post,
                                        'html_title': EDIT_POST_SUBMIT_TITLE,
                                        'submit': EDIT_POST_SUBMIT_BUTTON})


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, id=post_id)
    form = CommentForm(request.POST or None)
    if not form.is_valid():
        comments = Comment.objects.filter(post_id=post_id)
        return render(
            request, "comments.html", {"form": form,
                                       "comments": comments
                                       }
        )
    comment = form.save(commit=False)
    comment.author = request.user
    comment.post = post
    form.save()
    return redirect('post', username=username, post_id=post_id)


def page_not_found(request, exception):
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)


@login_required
def follow_index(request):
    posts = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(posts, POSTS_ON_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'follow.html',
        {'page': page,
         }
    )


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user != author:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect('profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user != author:
        get_object_or_404(Follow, user=request.user,
                          author=author).delete()
    return redirect('profile', username=username)
