from django.contrib.auth import get_user
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.views.generic import  CreateView, DetailView, ListView
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
# from django.views.decorators.cache import cache_page

from .forms import CommentForm, PostForm
from .models import Comment, Follow, Group, Post, User

CHAR_LIM = 30
POSTS_LIM = 10
CACHE_TIMEOUT = 20


def pagination(posts, request):
    paginator = Paginator(posts, POSTS_LIM)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj


class Index(ListView):
    model = Post
    template_name: str = 'posts/index.html'
    context_object_name = 'posts'
    paginate_by = POSTS_LIM

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Последние обновления на сайте'
        return context

# @cache_page(timeout=CACHE_TIMEOUT, key_prefix='index_page')
# def index(request):
#     posts = Post.objects.all()
#     template = 'posts/index.html'
#     title = 'Последние обновления на сайте'
#     page_obj = pagination(posts, request)
#     context = {
#         'posts': posts,
#         'title': title,
#         'page_obj': page_obj,
#     }
#     return render(request, template, context)


class Group_posts(ListView):
    model = Post
    template_name = 'posts/group_list.html'
    context_object_name = 'posts'
    paginate_by = POSTS_LIM

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['group'] = get_object_or_404(Group, slug=self.kwargs['slug'])
        context['title'] = 'Записи сообщества ' + str(context['group'])
        return context

    def get_queryset(self):
        return Post.objects.filter(group__slug=self.kwargs['slug'])

# def group_posts(request, slug):
#     group = get_object_or_404(Group, slug=slug)
#     template = 'posts/group_list.html'
#     posts = group.posts.all()
#     title = f'Записи сообщества {group}'
#     page_obj = pagination(posts, request)
#     context = {
#         'title': title,
#         'posts': posts,
#         'group': group,
#         'page_obj': page_obj,
#     }
#     return render(request, template, context)


class Profile(ListView):
    model = Post
    template_name = 'posts/profile.html'
    context_object_name = 'post'
    paginate_by = POSTS_LIM

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['author'] = get_object_or_404(
            User, username=self.kwargs['username'])
        context['title'] = (
            'Профайл пользователя ' + str(context['author'].get_full_name()))
        context['following'] = Follow.objects.filter(
            user=self.request.user.id, author=context['author']).exists()
        return context

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs['username'])
        return Post.objects.filter(author=user)

# def profile(request, username):
#     author = get_object_or_404(User, username=username)
#     posts = author.posts.all()
#     following = Follow.objects.filter(user=request.user.id,
#                                       author=author).exists()
#     title = f'Профайл пользователя {author.get_full_name()}'
#     page_obj = pagination(posts, request)
#     template = 'posts/profile.html'
#     context = {
#         'author': author,
#         'page_obj': page_obj,
#         'title': title,
#         'following': following,
#     }
#     return render(request, template, context)


class Post_detail(DetailView):
    model = Post
    form_class = CommentForm
    template_name = 'posts/post_detail.html'
    context_object_name = 'post'
    pk_url_kwarg = 'post_id'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = Comment.objects.filter(
            post=self.kwargs['post_id'])
        context['title'] = ('Пост ' + str(context['post']))
        return context

# def post_detail(request, post_id):
#     post = get_object_or_404(Post, pk=post_id)
#     form = CommentForm(request.POST or None)
#     comments = Comment.objects.filter(post=post_id)
#     text_lim = post.text[:CHAR_LIM]
#     title = f'Пост {text_lim}'
#     template = 'posts/post_detail.html'
#     context = {
#         'title': title,
#         'post': post,
#         'form': form,
#         'comments': comments
#     }
#     return render(request, template, context)


class Post_create(CreateView):
    model = Post
    form_class = PostForm
    template_name = 'posts/create_post.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm()
        context['is_edit'] = False
        return context

    def form_valid(self, form):
        form = form.save(commit=False)
        form.author = get_user(self.request)
        form.save()
        return redirect(reverse('posts:profile', args=[self.request.user]))

# @login_required
# def post_create(request):
#     user = get_user(request)
#     if request.method == 'POST':
#         form = PostForm(request.POST, request.FILES)
#         if form.is_valid():
#             frm = form.save(commit=False)
#             frm.author = user
#             frm.save()
#             return redirect(reverse('posts:profile', args=[user]))
#     form = PostForm()
#     context = {
#         'form': form,
#         'is_edit': False,
#     }
#     template = 'posts/create_post.html'
#     return render(request, template, context)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id)
    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    instance=post,
                    )
    if request.method == 'POST':
        if form.is_valid:
            form.save()
            return redirect('posts:post_detail', post_id)
    context = {
        'form': form,
        'is_edit': True,
    }
    template = 'posts/create_post.html'
    return render(request, template, context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    template = 'posts:post_detail'
    return redirect(template, post_id=post_id)


@login_required
def follow_index(request):
    posts = Post.objects.filter(author__following__user=request.user)
    page_obj = pagination(posts, request)
    context = {
        'posts': posts,
        'page_obj': page_obj,
    }
    template = 'posts/follow.html'
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if author != request.user:
        Follow.objects.get_or_create(author=author,
                                     user=request.user)
    template = 'posts:profile'
    return redirect(template, username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(author=author,
                          user=request.user).delete()
    template = 'posts:profile'
    return redirect(template, username=username)
