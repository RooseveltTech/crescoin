from rest_framework import status
from rest_framework.decorators import APIView
from rest_framework.response import Response

from rest_framework.permissions import IsAuthenticated

from django.shortcuts import render

from django.contrib.auth import get_user_model

from core.func import send_email

from core.serializers import RegistrationSerializer, VerificationSerializer

from drf_yasg.utils import swagger_auto_schema
# Create your views here.
import requests

from main.permissions import AllowUser, UserAlreadyVerified

User = get_user_model()

class RegistrationAPIView(APIView):
    """Register a new user."""

    # permission_classes = (AllowAny,)
    serializer_class = RegistrationSerializer
    @swagger_auto_schema(request_body=RegistrationSerializer)
    def post(self, request):
        """Handle HTTP POST request."""
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        email = serializer.validated_data.get("email")
        first_name = serializer.validated_data.get("first_name")

        send_email(recipient=email, subject="CRESCOIN REGISTRATION",
                            template_dir="welcome_new_user.html",
                            name=first_name,
        )

        return Response(
            {"status": "success", "message": "User created successfully"},
            status=status.HTTP_201_CREATED
        )
    
class CheckEmailAPIView(APIView):
    def get(self, request):
        email = request.query_params.get('email')
        user = User.objects.filter(email=email)
        if user.exists():
            return Response(
                {
                    "exist": True
                },
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {
                    "exist": False
                },
                status=status.HTTP_200_OK
            )
        
class Verification(APIView):
    permission_classes = [IsAuthenticated, AllowUser, UserAlreadyVerified]

    serializer_class = VerificationSerializer
    @swagger_auto_schema(request_body=VerificationSerializer)
    def post(self, request):
        request_user = request.user
        serializer = self.serializer_class(data=request.data, context={"request_user": request_user})
        serializer.is_valid(raise_exception=True)
        return Response({"message":"verification successful"},status=status.HTTP_200_OK)
        