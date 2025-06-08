from django.shortcuts import render, get_object_or_404
from django.views.generic import DetailView
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.http import Http404
from .models import Page

class PageDetailView(DetailView):
    model = Page
    template_name = 'pages/page_detail.html'
    context_object_name = 'page'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_queryset(self):
        return Page.objects.filter(is_active=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add any additional context data here if needed
        return context
