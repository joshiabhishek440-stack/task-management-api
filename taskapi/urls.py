from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RegisterView, ProfileView, UserListView, TaskViewSet, TaskFilterView

router = DefaultRouter()
router.register(r'tasks', TaskViewSet, basename='task')

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('users/', UserListView.as_view(), name='users'),
    path('tasks/filter/', TaskFilterView.as_view(), name='task-filter'),
    path('', include(router.urls)),
]