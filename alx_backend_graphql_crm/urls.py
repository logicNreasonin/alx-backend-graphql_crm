"""
URL configuration for alx_backend_graphql_crm project.

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
from django.contrib import admin
from django.urls import path
from graphene_django.views import GraphQLView
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('admin/', admin.site.urls),
    # The csrf_exempt is often used for local development/testing of GraphQL APIs
    # For production, ensure you understand the security implications or handle CSRF appropriately
    # (e.g., if your clients are traditional web browsers submitting forms).
    # For API clients, token-based authentication is more common.
    path("graphql", csrf_exempt(GraphQLView.as_view(graphiql=True))),
]
