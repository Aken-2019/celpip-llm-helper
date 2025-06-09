from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from allauth.account.forms import LoginForm, SignupForm

User = get_user_model()

class EmailLoginForm(LoginForm):
    """
    Custom login form that enforces email-only authentication.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Update the login field to be email-only
        self.fields['login'].label = _('Email')
        self.fields['login'].widget = forms.EmailInput(attrs={
            'type': 'email',
            'placeholder': _('Your email address'),
            'autocomplete': 'email',
            'class': 'form-control'
        })
        
    def clean_login(self):
        """Ensure the login field contains a valid email address."""
        login = self.cleaned_data.get('login')
        if login and '@' not in login:
            raise forms.ValidationError(_('Please enter a valid email address.'))
        return login

# class CustomSignupForm(SignupForm):
#     """
#     Custom signup form that collects username during registration
#     while still using email for authentication.
#     """
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         # Make username field required
#         self.fields['username'].required = True
#         # Update email field to be required (already is by default)
#         self.fields['email'].label = _('Email')
#         self.fields['email'].widget = forms.EmailInput(attrs={
#             'type': 'email',
#             'placeholder': _('Your email address'),
#             'autocomplete': 'email',
#             'class': 'form-control'
#         })
        
#     def clean_email(self):
#         email = super().clean_email()
#         if email and '@' not in email:
#             raise forms.ValidationError(_('Please enter a valid email address.'))
#         return email
