from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.views.generic import View, DeleteView
from django.urls import reverse_lazy
from django import forms
from .models import Api2dKey, Api2dGroup2ExpirationMapping
from django.conf import settings
from .utilities import Api2dClient
from django.conf import settings


class MP3UploadForm(forms.Form):
    """Form for uploading MP3 files"""

    mp3_file = forms.FileField(
        label="MP3 File",
        widget=forms.FileInput(
            attrs={
                "accept": ".mp3",
                "class": "form-control",
            }
        ),
    )

    def clean_mp3_file(self):
        mp3_file = self.cleaned_data.get("mp3_file")
        if not mp3_file:
            raise forms.ValidationError("No file was uploaded.")

        # Check file extension
        if not mp3_file.name.lower().endswith(".mp3"):
            raise forms.ValidationError("Only MP3 files are allowed.")

        return mp3_file


class ApiKeyForm(forms.ModelForm):
    """Form for adding a new API key"""

    class Meta:
        model = Api2dKey
        fields = ["key"]
        widgets = {
            "key": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Enter your API key"}
            )
        }
        labels = {"key": "API Key"}


class ApiKeyView(LoginRequiredMixin, View):
    """View to display and manage the user's API key"""

    def get(self, request, *args, **kwargs):
        try:
            # Get the API key for the current user
            api_key = Api2dKey.objects.get(user=request.user)
            form = ApiKeyForm()

            # Get the API endpoint from environment variable
            context = {
                "has_api_key": True,
                "api_key": api_key,
                "form": form,
                "api2d_openai_endpoint": settings.API2D_OPENAI_ENDPOINT,
            }
        except Api2dKey.DoesNotExist:
            client = Api2dClient(settings.API2D_ADMIN_KEY, settings.API2D_API_ENDPOINT)

            key_group = Api2dGroup2ExpirationMapping.objects.first()
            try:
                api2d_key_instance = client.call_custom_key_save(
                    type_id=key_group.type_id, n=1
                )
                api_key = Api2dKey.objects.create(
                    key=api2d_key_instance[0]["key"],
                    user=request.user,
                    group=key_group,
                    created_at=timezone.now(),
                )
                return redirect("api2d:api-key")
            except ValueError as e:
                messages.error(request, str(e))
                return redirect("api2d:api-key")

        return render(request, "api2d/api_key_list.html", context)


class ApiKeyDeleteView(LoginRequiredMixin, DeleteView):
    """View to delete the user's API key"""

    model = Api2dKey
    success_url = reverse_lazy("pages:home")  # Redirect to home page after deletion
    template_name = "api2d/api_key_confirm_delete.html"

    def get_object(self, queryset=None):
        """Get the API key for the current user"""
        obj = get_object_or_404(Api2dKey, user=self.request.user)
        return obj

    def delete(self, request, *args, **kwargs):
        """Handle successful deletion"""
        response = super().delete(request, *args, **kwargs)
        messages.success(self.request, "Your API key has been deleted successfully.")
        return response


@login_required
def celpip_speaking(request):
    """Serve the MP3 processing page"""
    try:
        # Get the user's API key
        api_key = Api2dKey.objects.get(user=request.user)
        if api_key.expired_at and api_key.expired_at < timezone.now():
            messages.error(request, "Your API key has expired. Please renew it.")
            return redirect("api2d:api-key")
        context = {
            "api_key": api_key.key,
            "api2d_openai_endpoint": settings.API2D_CLAUDE_ENDPOINT,  # Updated to use Django's endpoint
            "api2d_openai_stt_model": settings.API2D_OPENAI_STT_MODEL,
            "api2d_openai_txt_model": settings.API2D_CLAUDE_MODEL,
            "celpip_improve_sys_prompt": settings.CLAUDE_CELPIP_WRITTING_SYSTEM_PROMPT,
        }
        return render(request, "api2d/CelpipSpeaking.html", context)
    except Api2dKey.DoesNotExist:
        messages.error(request, "积分不足，请先充值。")
        return redirect("api2d:api-key")


@login_required
def celpip_writting(request):
    try:
        # Get the user's API key
        api_key = Api2dKey.objects.get(user=request.user)
        if api_key.expired_at and api_key.expired_at < timezone.now():
            messages.error(request, "Your API key has expired. Please renew it.")
            return redirect("api2d:api-key")
        context = {
            "api_key": api_key.key,
            "api2d_claude_endpoint": settings.API2D_CLAUDE_ENDPOINT,  # Updated to use Django's endpoint
            "api2d_claude_model": settings.API2D_CLAUDE_MODEL,
            "celpip_writting_system_prompt": settings.CLAUDE_CELPIP_WRITTING_SYSTEM_PROMPT,
        }
        return render(request, "api2d/CelpipWritting.html", context)
    except Api2dKey.DoesNotExist:
        messages.error(request, "积分不足，请先充值。")
        return redirect("api2d:api-key")


def home_page_view(request):
    return render(request, "api2d/home.html")
