from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import DetailView, View
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.http import Http404, HttpResponseRedirect
from django.urls import reverse
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


class HomePageView(View):
    """View to display the home page based on the Page model with slug 'home'"""
    template_name = 'pages/page_detail.html'
    
    def get(self, request, *args, **kwargs):
        try:
            # Try to get the page with slug 'home'
            page = Page.objects.get(slug='home', is_active=True)
        except Page.DoesNotExist:
            # Create a default home page if it doesn't exist
            page = Page.objects.create(
                title='Home',
                slug='home',
                content='<p>Welcome to my site!</p>',
                is_active=True
            )
            
        context = {
            'page': page,
            'view': self
        }
        return render(request, self.template_name, context)
