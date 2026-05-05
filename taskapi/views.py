from django.shortcuts import render

def home(request):
    return render(request, 'taskapi/index.html')
from django.db.models import Q
from django.contrib.auth.models import User
from rest_framework import generics, viewsets, filters
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Task, Profile
from .serializers import RegisterSerializer, UserSerializer, TaskSerializer
from .permissions import IsManagerOrAdmin, IsOwnerOrManagerOrAdmin
from django.shortcuts import render

def home(request):
    return render(request, 'taskapi/index.html')


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsManagerOrAdmin]


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'due_date', 'priority']

    def get_queryset(self):
        user = self.request.user
        try:
            role = user.profile.role
        except Profile.DoesNotExist:
            role = 'developer'

        if role in ['admin', 'manager']:
            return Task.objects.all().order_by('-created_at')

        return Task.objects.filter(
            Q(created_by=user) | Q(assigned_to=user)
        ).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class TaskFilterView(generics.ListAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Task.objects.all()
        status = self.request.query_params.get('status')
        priority = self.request.query_params.get('priority')
        if status:
            queryset = queryset.filter(status=status)
        if priority:
            queryset = queryset.filter(priority=priority)
        return queryset