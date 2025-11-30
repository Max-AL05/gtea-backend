from django.contrib import admin # type: ignore
from django.urls import path # type: ignore
from sistema_gtea.views import categorias
from sistema_gtea.views import bootstrap, eventos
from sistema_gtea.views import estudiantes
from sistema_gtea.views import organizadores
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

    #Create organizador
        path('Organizador/', organizadores.OrganizadorView.as_view()),
    #organizador Data
        path('lista-Organizador/', organizadores.OrganizadorAll.as_view()),
    #Edit Organizador
        path('Organizador-edit/', organizadores.OrganizadorViewEdit.as_view()),

    #Login
        path('token/', auth.CustomAuthToken.as_view()),
    #Logout
        path('logout/', auth.Logout.as_view())
]


   
    