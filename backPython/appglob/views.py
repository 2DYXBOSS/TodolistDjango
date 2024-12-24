from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserSerializer, TaskSerializer

from django.contrib.auth import get_user_model
print(get_user_model())

from django.http import Http404
from rest_framework import status

from .models import Task


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]  # Accessible uniquement aux utilisateurs connectés

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")  # Récupérer le jeton de rafraîchissement depuis la requête
            if not refresh_token:
                return Response({"error": "Refresh token is required."}, status=400)

            # Invalider le jeton de rafraîchissement
            token = RefreshToken(refresh_token)
            token.blacklist()  # Nécessite l'installation de `django-rest-framework-simplejwt-token-blacklist`

            return Response({"message": "User logged out successfully."}, status=200)
        except Exception as e:
            return Response({"error": str(e)}, status=400)

class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user  # Utilisateur actuellement connecté
        serializer = UserSerializer(user)  # Sérialiser les données de l'utilisateur
        return Response(serializer.data)


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'User registered successfully'}, status=201)
        return Response(serializer.errors, status=400)
    


from django.contrib.auth import authenticate

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        # Debug: vérifier les données reçues
        print(f"Username: {username}, Password: {password}")

        user = authenticate(username=username, password=password)

        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
        # Ajouter un message d'erreur plus précis
        return Response({'error': 'Invalid credentials'}, status=401)
    
    
class UpdateTaskStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        try:
            task = Task.objects.get(id=pk, user=request.user)
            task.completed = not task.completed  # Change le statut
            task.save()
            return Response({"message": "Statut mis à jour", "completed": task.completed}, status=status.HTTP_200_OK)
        except Task.DoesNotExist:
            return Response({"error": "Tâche introuvable"}, status=status.HTTP_404_NOT_FOUND)

class TaskListCreateView(APIView):
    permission_classes = [IsAuthenticated]  

    def get(self, request):
        tasks = Task.objects.filter(user=request.user)  # Assure que le token correspond au user
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)  # Relie la tâche à l'utilisateur connecté
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

class TaskDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        try:
            return Task.objects.get(pk=pk, user=user)
        except Task.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        task = self.get_object(pk, request.user)
        serializer = TaskSerializer(task)
        return Response(serializer.data)

    def put(self, request, pk):
        task = self.get_object(pk, request.user)
        serializer = TaskSerializer(task, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        task = self.get_object(pk, request.user)
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    
