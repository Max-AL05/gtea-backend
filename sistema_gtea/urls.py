from django.contrib import admin # type: ignore
from django.urls import path # type: ignore
from sistema_gtea.views import categorias
from sistema_gtea.views import bootstrap, eventos
from sistema_gtea.views import estudiantes
from sistema_gtea.views import organizadores
from sistema_gtea.views import sedes
from sistema_gtea.views import users
from sistema_gtea.views import auth

urlpatterns = [
    #Version
        path('bootstrap/version', bootstrap.VersionView.as_view()),
    #Admin 
    path('admin/', users.AdminView.as_view()),
    path('lista-admins/', users.AdminAll.as_view()),
    path('admins-edit/', users.AdminsViewEdit.as_view()),

    #categorias
    path('categorias/', categorias.CategoriaView.as_view()),
    path('lista-categorias/', categorias.CategoriaAll.as_view()),
    path('categorias-edit/', categorias.CategoriaViewEdit.as_view()),

    #eventos    
    path('eventos/', eventos.EventoView.as_view()),
    path('lista-eventos/', eventos.EventosAll.as_view()),
    path('eventos-edit/', eventos.EventosViewEdit.as_view()),

    #estudiantes
    path('Estudiantes/', estudiantes.EstudiantesView.as_view()),    
    path('lista-Estudiantes/', estudiantes.EstudiantesALL.as_view()),
    path('Estudiantes-edit/', estudiantes.EstudiantesViewEdit.as_view()),

    #organizadores
    path('Organizador/', organizadores.OrganizadorView.as_view()),
    path('lista-Organizador/', organizadores.OrganizadorAll.as_view()),
    path('Organizador-edit/', organizadores.OrganizadorViewEdit.as_view()),

    #sedes
    path('sedes/', sedes.SedeView.as_view()),
    path('lista-sedes/', sedes.SedesAll.as_view()),
    path('sedes-edit/', sedes.SedesViewEdit.as_view()),    

    #Login
        path('token/', auth.CustomAuthToken.as_view()),
    #Logout
        path('logout/', auth.Logout.as_view())
]
