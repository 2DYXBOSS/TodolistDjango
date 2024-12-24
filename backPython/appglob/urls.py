from django.urls import path,re_path
from .views import CurrentUserView, LoginView, LogoutView, RegisterView, TaskListCreateView, TaskDetailView, UpdateTaskStatusView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    re_path(r'^register/?$', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('tasks/', TaskListCreateView.as_view(), name='task-list-create'),
    path('tasks/<int:pk>/', TaskDetailView.as_view(), name='task-detail'),
    path('tasks/<int:pk>/toggle-status/', UpdateTaskStatusView.as_view(), name='update-task-status'),
    path('user/', CurrentUserView.as_view(), name='current-user'),
    path('logout/', LogoutView.as_view(), name='logout'),
]