import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import View, DeleteView
from django.urls import reverse_lazy
from django import forms
from .models import Api2dKey, Api2dGroup2ExpirationMapping
from django.conf import settings
from django.utils.safestring import mark_safe



class MP3UploadForm(forms.Form):
    """Form for uploading MP3 files"""
    mp3_file = forms.FileField(
        label='MP3 File',
        widget=forms.FileInput(attrs={
            'accept': '.mp3',
            'class': 'form-control',
        })
    )
    
    def clean_mp3_file(self):
        mp3_file = self.cleaned_data.get('mp3_file')
        if not mp3_file:
            raise forms.ValidationError("No file was uploaded.")
        
        # Check file extension
        if not mp3_file.name.lower().endswith('.mp3'):
            raise forms.ValidationError("Only MP3 files are allowed.")
        
        return mp3_file


class ApiKeyForm(forms.ModelForm):
    """Form for adding a new API key"""
    class Meta:
        model = Api2dKey
        fields = ['key']
        widgets = {
            'key': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your API key'})
        }
        labels = {
            'key': 'API Key'
        }

class ApiKeyView(LoginRequiredMixin, View):
    """View to display and manage the user's API key"""
    
    def get(self, request, *args, **kwargs):
        try:
            # Get the API key for the current user
            api_key = Api2dKey.objects.get(user=request.user)
            form = ApiKeyForm()
            
            # Get the API endpoint from environment variable
            api2d_openai_endpoint = os.getenv("DYNACONF_API2D_OPENAI_ENDPOINT")
            context = {
                'has_api_key': True,
                'api_key': api_key,
                'form': form,
                'api2d_openai_endpoint': api2d_openai_endpoint
            }
        except Api2dKey.DoesNotExist:
            form = ApiKeyForm()
            context = {
                'has_api_key': False,
                'api_key': None,
                'form': form
            }
        
        return render(request, 'api2d/api_key_list.html', context)
    
    def post(self, request, *args, **kwargs):
        form = ApiKeyForm(request.POST)
        if form.is_valid():
            # Check if user already has an API key
            if Api2dKey.objects.filter(user=request.user).exists():
                messages.error(request, 'You already have an API key. Please delete it before adding a new one.')
                return redirect('api2d:api-key')
            if Api2dKey.objects.filter(key=form.cleaned_data['key']).exists():
                messages.error(request, 'This API key is already in use by another user.')
                return redirect('api2d:api-key')

            from .utilities import Api2dClient
            client = Api2dClient(os.getenv("DYNACONF_API2D_ADMIN_KEY"), os.getenv("DYNACONF_API2D_API_ENDPOINT"))
            try:
                api2d_key_instance = client.get_key(form.cleaned_data['key'])
            except ValueError as e:
                messages.error(request, str(e))
                return redirect('api2d:api-key')

            # Save the new API key
            api_key = form.save(commit=False)
            api_key.created_at = api2d_key_instance.created_at
            api_key.user = request.user
            api_key.group = Api2dGroup2ExpirationMapping.objects.filter(type_id=api2d_key_instance.type_id).first()
            api_key.save()
            
            messages.success(request, 'API key added successfully!')
            return redirect('api2d:api-key')
        
        # If form is not valid, show errors
        context = {
            'has_api_key': Api2dKey.objects.filter(user=request.user).exists(),
            'api_key': Api2dKey.objects.filter(user=request.user).first(),
            'form': form
        }
        return render(request, 'api2d/api_key_list.html', context)

class ApiKeyDeleteView(LoginRequiredMixin, DeleteView):
    """View to delete the user's API key"""
    model = Api2dKey
    success_url = reverse_lazy('api2d:api-key')
    template_name = 'api2d/api_key_confirm_delete.html'
    
    def get_object(self, queryset=None):
        """Get the API key for the current user"""
        obj = get_object_or_404(Api2dKey, user=self.request.user)
        return obj
    
    def delete(self, request, *args, **kwargs):
        """Handle successful deletion"""
        response = super().delete(request, *args, **kwargs)
        messages.success(self.request, 'Your API key has been deleted successfully.')
        return response


@login_required
def upload_mp3(request):
    """Serve the MP3 processing page"""
    try:
        # Get the user's API key
        api_key = Api2dKey.objects.get(user=request.user)
        context = {
            'api_key': api_key.key,
            'api2d_openai_endpoint': os.getenv("DYNACONF_API2D_OPENAI_ENDPOINT"),
            'api2d_openai_stt_model': os.getenv("DYNACONF_API2D_OPENAI_STT_MODEL"),
            'api2d_openai_txt_model': os.getenv("DYNACONF_API2D_OPENAI_TXT_MODEL"),
            'celpip_improve_sys_prompt': settings.CELPIP_IMPROVE_SYS_PROMPT,
            'celpip_extend_sys_prompt': settings.CELPIP_EXTEND_SYS_PROMPT,
            'is_admin': request.user.is_superuser,  # Add admin status
        }
        return render(request, 'api2d/upload_mp3.html', context)
    except Api2dKey.DoesNotExist:
        messages.error(request, 'Please add your API key first.')
        return redirect('api2d:api-key')


def home_page_view(request):
    return render(request, 'api2d/home.html')
