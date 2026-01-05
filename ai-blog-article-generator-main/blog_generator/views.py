from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse,HttpResponse
from django.conf import settings
import json
from django.template.defaultfilters import safe  # optional
from django.utils.safestring import mark_safe
from django.template.defaultfilters import json_script  # if using template filter

# from pytube import YouTube
import yt_dlp
import os
import assemblyai as aai
# import openai
from .models import BlogPost
import traceback

import qrcode
from qrcode.constants import ERROR_CORRECT_L
from django.urls import reverse
from io import BytesIO

from googletrans import Translator
from deep_translator import GoogleTranslator
from django.template.loader import render_to_string
from xhtml2pdf import pisa

from urllib.parse import quote as urlquote
from django import forms
import re

# Create your views here.
@login_required
def index(request):
    return render(request, 'index.html')

@csrf_exempt
def generate_blog(request):
    if request.method == 'POST':
        try:
            # --- 1. Get Link from Request ---
            data = json.loads(request.body)
            yt_link = data['link']
        except (KeyError, json.JSONDecodeError):
            return JsonResponse({'error': 'Invalid data sent or missing YouTube link.'}, status=400)

        try:
            # --- 2. All Processing Steps ---
            
            # get yt title (Pytube can fail here)
            title = yt_title(yt_link)

            # get transcript (Pytube download, AssemblyAI API can fail here)
            transcription = get_transcription(yt_link)
            if not transcription:
                # Assuming get_transcription now returns None on failure
                return JsonResponse({'error': "Failed to get transcript. Check the YouTube link, video availability, or API key status."}, status=500)

            # use OpenAI to generate the blog (OpenAI API can fail here)
            blog_content = generate_blog_from_transcription(transcription)
            if not blog_content:
                return JsonResponse({'error': "Failed to generate blog article from transcription."}, status=500)

            # save blog article to database (DB save can fail)
            new_blog_article = BlogPost.objects.create(
                user=request.user,
                youtube_title=title,
                youtube_link=yt_link,
                generated_content=blog_content,
            )
            new_blog_article.save()

            # --- 3. Success Response ---
            return JsonResponse({'content': blog_content})
        except Exception as e:
            traceback.print_exc() # Prints the file, line number, and error type
            print(f"CRITICAL ERROR during blog generation: {type(e).__name__}: {e}")
            return JsonResponse({'error': f"Server processing failed: {type(e).__name__} - check server logs for details."}, status=500)
            
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)

def yt_title(link):
    """Get YouTube video title using yt-dlp"""
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(link, download=False)
            return info.get('title', 'Unknown Title')
    except Exception as e:
        print(f"Error getting title: {e}")
        return "Unknown Title"

def download_audio(link):
    """Download audio from YouTube video using yt-dlp (no conversion)"""
    try:
        print(f"Attempting to download audio from: {link}")
        
        # Ensure media directory exists
        if not os.path.exists(settings.MEDIA_ROOT):
            os.makedirs(settings.MEDIA_ROOT)
        
        # Configure yt-dlp to download best audio without conversion
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(settings.MEDIA_ROOT, '%(title)s.%(ext)s'),
            'quiet': False,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(link, download=True)
            filename = ydl.prepare_filename(info)
            
            print(f"Downloaded audio file: {filename}")
            
            if os.path.exists(filename):
                return filename
            else:
                # Sometimes the extension changes, try to find it
                base = os.path.splitext(filename)[0]
                for ext in ['.webm', '.m4a', '.opus', '.mp3']:
                    possible_file = base + ext
                    if os.path.exists(possible_file):
                        return possible_file
                
                print(f"Audio file not found")
                return None
                
    except Exception as e:
        print(f"Error downloading audio: {e}")
        import traceback
        traceback.print_exc()
        return None

def get_transcription(link):
    audio_file = download_audio(link)
    
    if not audio_file:
        print("Audio download failed, cannot transcribe")
        return None
    
    if not os.path.exists(audio_file):
        print(f"Audio file doesn't exist at: {audio_file}")
        return None
        
    print(f"Audio file exists, size: {os.path.getsize(audio_file)} bytes")
    
    aai.settings.api_key = settings.ASSEMBLYAI_API_KEY
    transcriber = aai.Transcriber()
    
    try:
        print("Starting transcription...")
        transcript = transcriber.transcribe(audio_file)
        transcription_text = transcript.text
        print("Transcription completed successfully")
    except Exception as e:
        print(f"AssemblyAI Transcription Error: {e}")
        traceback.print_exc()
        transcription_text = None
    finally:
        # Delete the file after use
        if os.path.exists(audio_file):
            os.remove(audio_file)
            print(f"Cleaned up audio file: {audio_file}")
            
    return transcription_text


def generate_blog_from_transcription(transcription):
    """Generate blog using OpenRouter API"""
    try:
        import requests

        print("Generating blog with OpenRouter AI...")

        # OpenRouter API URL
        API_URL = "https://api.perplexity.ai/chat/completions"


        # Model to use
        MODEL = "sonar-pro"

        # Construct messages for chat completion
        messages = [
            {
                "role": "user",
                "content": f"Write a blog article based on the following transcription:\n\n{transcription[:1500]}"
            }
        ]

        headers = {
            "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "<YOUR_SITE_URL>",  # optional, replace with your site
            "X-Title": "<YOUR_SITE_NAME>",      # optional, replace with your site name
        }

        payload = {
            "model": "sonar-pro",
            "messages": messages,
            "max_tokens": 1000,          # Maximum tokens for the blog output
            "verbosity": "low"           # Lower verbosity for conciseness
}


        response = requests.post(API_URL, headers=headers, json=payload, timeout=30)

        if response.status_code == 200:
            result = response.json()
            # Extract the generated content from the response
            generated_content = result['choices'][0]['message']['content']
            print("✓ Blog generated successfully")
            return generated_content
        else:
            print(f"API Error: {response.status_code} - {response.text}")
            return None

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return None





@login_required
def blog_list(request):
    blog_articles = BlogPost.objects.filter(user=request.user)
    return render(request, "all-blogs.html", {'blog_articles': blog_articles})


@login_required
def blog_details(request, pk):
    blog_article_detail = BlogPost.objects.get(id=pk)
    if request.user == blog_article_detail.user:
        return render(request, 'blog-details.html', {'blog_article_detail': blog_article_detail})
    else:
        return redirect('/')
    



@login_required
@csrf_exempt
def delete_blog(request, pk):
    if request.method == "POST":
        try:
            blog = BlogPost.objects.get(pk=pk, user=request.user, deleted_at__isnull=True)
            blog.soft_delete()  # use soft_delete method instead of delete
            return JsonResponse({"success": True})
        except BlogPost.DoesNotExist:
            return JsonResponse({"error": "Blog not found"}, status=404)
    return JsonResponse({"error": "Invalid method"}, status=405)

    

@login_required
def recently_deleted_blogs(request):
    blogs = BlogPost.all_objects.filter(user=request.user, deleted_at__isnull=False).order_by("-deleted_at")
    return render(request, "recently_deleted.html", {"blogs": blogs})


@login_required
@csrf_exempt
def permanent_delete_blogs(request):
    """Permanently delete selected recently deleted blogs"""
    if request.method == "POST":
        try:
            blog_ids = request.POST.getlist('blog_ids')
            
            if not blog_ids:
                return JsonResponse({"error": "No blogs selected"}, status=400)
            
            # Get all selected blogs that belong to the user and are deleted
            blogs_to_delete = BlogPost.all_objects.filter(
                pk__in=blog_ids, 
                user=request.user, 
                deleted_at__isnull=False
            )
            
            # Count before deletion
            count = blogs_to_delete.count()
            
            # Perform hard delete
            blogs_to_delete.delete()
            
            # Redirect to recently deleted blogs page
            return redirect('recently_deleted_blogs')
        
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    
    return JsonResponse({"error": "Invalid method"}, status=405)



@login_required
def restore_blog(request, pk):
    blog = get_object_or_404(BlogPost.all_objects, pk=pk, user=request.user, deleted_at__isnull=False)
    blog.restore()
    return redirect("recently_deleted_blogs")



# views.py
import textwrap
from io import BytesIO

import qrcode
from qrcode.constants import ERROR_CORRECT_L

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse

from .models import BlogPost


# views.py
import textwrap
from io import BytesIO

import qrcode
from qrcode.constants import ERROR_CORRECT_L

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse

from .models import BlogPost


def build_summary(text: str, min_len: int = 600, max_len: int = 800) -> str:
    if not text:
        return ""

    text = " ".join(text.split())  # normalize spaces

    if len(text) <= min_len:
        return text

    if len(text) <= max_len:
        return text

    cutoff = text.rfind(" ", 0, max_len)
    if cutoff == -1:
        cutoff = max_len

    return text[:cutoff].rstrip() + "..."


def download_blog_qr(request, pk):
    blog = get_object_or_404(BlogPost, pk=pk, user=request.user)

    # Use the correct field from your model
    full_text = blog.generated_content  # <-- this is the right field

    # Build 600–800 char summary
    summary = build_summary(full_text, min_len=600, max_len=800)

    # Build absolute URL of blog detail page
    blog_relative_url = reverse('blog-details', kwargs={'pk': blog.pk})
    blog_absolute_url = request.build_absolute_uri(blog_relative_url)

    # Combine summary + URL into QR payload
    qr_text = f"{summary}\n\nRead full blog: {blog_absolute_url}"

    qr = qrcode.QRCode(
        version=None,
        error_correction=ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_text)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)

    response = HttpResponse(buffer, content_type='image/png')
    response['Content-Disposition'] = f'attachment; filename=blog_{pk}_qr.png'
    return response






translator = Translator()

@csrf_exempt
def translate_blog(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            text = data.get('text', '')
            target_lang = data.get('target_lang', 'en')

            if not text.strip():
                return JsonResponse({'error': 'No text provided'}, status=400)

            translated_text = GoogleTranslator(source='auto', target=target_lang).translate(text)
            return JsonResponse({'translated_text': translated_text})

        except Exception as e:
            return JsonResponse({'error': f'Translation failed: {str(e)}'}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=405)




def generate_pdf(request, pk):
    blog_article = get_object_or_404(BlogPost, id=pk)
    context = {'blog_article_detail': blog_article}
    html = render_to_string('blog_pdf.html', context) # Your template

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="blog-{id}.pdf"'
    
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('Error generating PDF', status=500)
    return response




# WhatsApp share form
class WhatsAppShareForm(forms.Form):
    phone_number = forms.CharField(
        max_length=12,
        required=True,
        label="Enter phone number with country code (e.g., 919876543210)",
        widget=forms.TextInput(attrs={"placeholder": "Phone number with country code"})
    )
    message = forms.CharField(
        max_length=5000,  # Increased limit
        required=True,
        widget=forms.Textarea(attrs={"rows": 10, "cols": 70}),
        label="Blog's content to share on WhatsApp"
    )

    def clean_phone_number(self):
        phone = self.cleaned_data['phone_number']
        if not re.match(r'^\d{8,15}$', phone):
            raise forms.ValidationError("Enter a valid phone number with digits and country code only.")
        return phone


def share_on_whatsapp(request):
    # If 'text' param comes via GET, use it as initial message
    default_message = request.GET.get('text', 'Check out this blog post!')
    if request.method == "POST":
        form = WhatsAppShareForm(request.POST)
        if form.is_valid():
            phone_number = form.cleaned_data['phone_number']
            message = form.cleaned_data['message']
            encoded_message = urlquote(message)
            whatsapp_url = f"https://wa.me/{phone_number}?text={encoded_message}"
            return redirect(whatsapp_url)
    else:
        form = WhatsAppShareForm(initial={"message": default_message})

    return render(request, "share.html", {"form": form})




def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            error_message = "Invalid username or password."
            return render(request, 'login.html', {'error_message': error_message})
        
    return render(request, 'login.html')

def user_signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        repeatPassword = request.POST['repeatPassword']

        if password == repeatPassword:
            try:
                user = User.objects.create_user(username, email, password)
                user.save()
                login(request, user)
                return redirect('/')
            except:
                error_message = 'Error occured while creating account.'
                return render(request, 'signup.html', {'error_message':error_message})
        else:
            error_message = 'Password do not match.'
            return render(request, 'signup.html', {'error_message':error_message})
        
    return render(request, 'signup.html')

def user_logout(request):
    logout(request)
    return redirect('/')




def change_password(request):
    if request.method == "POST":
        if request.POST.get('new-password'):
            username = request.POST.get('username')
            old_password = request.POST.get('old-password')
            new_password = request.POST.get('new-password')

            user = authenticate(username=username, password=old_password)
            if user is not None:
                user.set_password(new_password)
                user.save()
                return redirect('login')  # Redirect to login page after successful password reset
            else:
                error_message = "Invalid username or old password."
                return render(request, 'change_password.html', {
                    'error_message': error_message,
                    'step': 1,
                })
        else:
            username = request.POST.get('username')
            old_password = request.POST.get('old-password')
            user = authenticate(username=username, password=old_password)
            if user is not None:
                return render(request, 'change_password.html', {
                    'step': 2,
                    'username': username,
                    'old_password': old_password,
                })
            else:
                error_message = "Invalid username or old password."
                return render(request, 'change_password.html', {
                    'error_message': error_message,
                    'step': 1,
                })
    return render(request, 'change_password.html', {'step': 1})





def forgot_password(request):
    if request.method == "POST":
        # Step 2: Handle new password set
        if request.POST.get('new-password'):
            username = request.POST.get('username')
            email = request.POST.get('email')
            new_password = request.POST.get('new-password')

            try:
                user = User.objects.get(username=username, email=email)
            except ObjectDoesNotExist:
                error_message = "Invalid username or email id."
                return render(request, 'forgot_password.html', {
                    'error_message': error_message,
                    'step': 1
                })

            user.set_password(new_password)
            user.save()
            success_message = "Password changed successfully. Please log in with your new password."
            return render(request, 'login.html', {
                'success_message': success_message,
                'step': 1
            })

        # Step 1: Verify username and email
        else:
            username = request.POST.get('username')
            email = request.POST.get('email')
            try:
                user = User.objects.get(username=username, email=email)
                # Credentials are correct, allow password reset
                return render(request, 'forgot_password.html', {
                    'step': 2,
                    'username': username,
                    'email': email,
                })
            except ObjectDoesNotExist:
                error_message = "Invalid username or email id."
                return render(request, 'forgot_password.html', {
                    'error_message': error_message,
                    'step': 1
                })

    # On GET request, show step 1
    return render(request, 'forgot_password.html', {'step': 1})
