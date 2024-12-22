from django.contrib import admin
from django.urls import path, include
from django_security_tools.views import home_view  # Correctly import the home view

"""
URL configuration for django_security_tools project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""



urlpatterns = [
    path('', home_view, name='home'),  # Home page route
    path('mac_address_changer/', include('mac_address_changer.urls')),  # MAC Address Changer URLs
    path('network_scanner/', include('network_scanner.urls')),  # Network Scanner URLs
    path('admin/', admin.site.urls),  # Admin site
]