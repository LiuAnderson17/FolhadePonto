from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Autenticação
    path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    # Logout → redireciona EXPLICITAMENTE para /accounts/login/ (sem parâmetros)
    path('accounts/logout/', 
         auth_views.LogoutView.as_view(next_page='/accounts/login/'), 
         name='logout'),
    
    # Rotas do app ponto (inclui a raiz / apontando para dashboard)
    path('', include('ponto.urls')),
]