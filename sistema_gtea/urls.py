"""point_experts_api URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.contrib import admin # type: ignore
from django.urls import path # type: ignore
from sistema_gtea.views import categorias
from sistema_gtea.views import bootstrap, eventos
from sistema_gtea.views import estudiantes
from sistema_gtea.views.organizadores import Organizador
from sistema_gtea.views import users
from sistema_gtea.views import auth

urlpatterns = [
    #Version
        path('bootstrap/version', bootstrap.VersionView.as_view()),
    #Create Admin 
        path('admin/', users.AdminView.as_view()),
    #Admin Data 
        path('lista-admins/', users.AdminAll.as_view()),
    #Edit Admin
        path('admins-edit/', users.AdminsViewEdit.as_view()),

    # Create Categoria
        path('categorias/', categorias.CategoriaView.as_view()),
    # Categoria Data (Lista)
        path('lista-categorias/', categorias.CategoriaAll.as_view()),
    # Edit Categoria
        path('categorias-edit/', categorias.CategoriaViewEdit.as_view()),
        
    #Create Evento
        path('eventos/', eventos.EventoView.as_view()),
    #Evento Data
        path('lista-eventos/', eventos.EventosAll.as_view()),
    #Edit Admin
        path('eventos-edit/', eventos.EventosViewEdit.as_view()),

    #Create estudiante
        path('Estudiantes/', estudiantes.EstudiantesView.as_view()),    
    #estudiante Data
        path('lista-Estudiantes/', estudiantes.EstudiantesALL.as_view()),
    #Edit estudiante
        path('Estudiantes-edit/', estudiantes.EstudiantesViewEdit.as_view()),

    #Login
        path('token/', auth.CustomAuthToken.as_view()),
    #Logout
        path('logout/', auth.Logout.as_view())
]


   
    #Create organizador
        #path('Organizador/', Organizador.organizadorView.as_view()),
    #organizador Data
        #path('lista-Organizador/', Organizador.OrganizadorAll.as_view()),
    #Edit Organizador
        #path('Organizador-edit/', Organizador.OrganizadorViewEdit.as_view()),