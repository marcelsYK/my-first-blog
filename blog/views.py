import json

from django.shortcuts import redirect
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from watson_developer_cloud import LanguageTranslatorV2 as LanguageTranslator
from watson_developer_cloud import ToneAnalyzerV3

from .forms import PostForm
from .models import Post


# def post_list(request):
#   posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('published_date')
#  return render(request, 'blog/post_list.html', {'posts': posts})

def post_list(request):
    posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('published_date')
    tone_analyzer = ToneAnalyzerV3(
        username='729aa36c-75b7-443c-9383-cf54a7d14a2d',
        password='7jFlqMwQdW8M',
        version='2016-05-19 ')

    language_translator = LanguageTranslator(
        username='2145e0e3-d689-421f-90c6-2306a055b2fa',
        password='1iQdBjdOcVbZ')

    # print(json.dumps(translation, indent=2, ensure_ascii=False))

    for post in posts:
        data = json.dumps(tone_analyzer.tone(text=post.text), indent=1)  # converting to string and storing in the data
        j = json.loads(data);
        post.info = j['document_tone']['tone_categories'][0]['tones']
        # post.info = json.dumps(post.info);
        post.angerScore = post.info[0]['score']
        post.disgustScore = post.info[1]['score']
        post.fearScore = post.info[2]['score']
        post.joyScore = post.info[3]['score']
        post.sadScore = post.info[4]['score']
        # print(post.info[0]['tone_name'])
        translation = language_translator.translate(
            text=post.text,
            source='en',
            target='fr')
        post.translatedText = json.dumps(translation, indent=2, ensure_ascii=False)
    return render(request, 'blog/post_list.html', {'posts': posts})


def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    # Post.objects.get(pk=pk)
    return render(request, 'blog/post_detail.html', {'post': post})


def post_new(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm()
    return render(request, 'blog/post_edit.html', {'form': form})


def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/post_edit.html', {'form': form})
