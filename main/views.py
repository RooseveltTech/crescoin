from rest_framework import status
from rest_framework.decorators import APIView
from rest_framework.response import Response

from rest_framework.permissions import IsAuthenticated

from main.models import Beneficiary
from main.permissions import CheckPin, UserHasPin, UserIsActive
from main.serializers import AllBeneficiarySerializer, ChangeTransactionPinSerializer, CreateBeneficiarySerializer, CreateTransactionPinSerializer, DeleteBeneficiarySerializer
from drf_yasg.utils import swagger_auto_schema
# Create your views here.


class GetUserBeneficiary(APIView):
    permission_classes = [IsAuthenticated, UserIsActive]
    serializer_class = AllBeneficiarySerializer
    def get(self, request):
        """ Get all user beneficiaries."""
        all_beneficiary = Beneficiary.objects.filter(user=request.user, is_deleted=False).order_by("-id")
        beneficiary_list = self.serializer_class(all_beneficiary, many=True)
        response = {
            "beneficiaries": beneficiary_list.data
        }
        return Response(response, status=status.HTTP_200_OK)
    
class CreateUserBeneficiary(APIView):
    permission_classes = [IsAuthenticated, UserIsActive, UserHasPin]
    serializer_class = CreateBeneficiarySerializer
    @swagger_auto_schema(request_body=CreateBeneficiarySerializer)
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        all_beneficiary = serializer.validated_data.get("beneficiary_data")
        beneficiary = Beneficiary.create_single_multiple_beneficiary(request.user, all_beneficiary)
        return Response({"message":"successful"}, status=status.HTTP_200_OK)

class DeleteUserBeneficiary(APIView):
    permission_classes = [IsAuthenticated, UserIsActive, UserHasPin]  
    serializer_class = DeleteBeneficiarySerializer
    @swagger_auto_schema(request_body=DeleteBeneficiarySerializer)
    def delete(self, request):
        serializer = self.serializer_class(data=request.data, context={"request_user": request.user})
        serializer.is_valid(raise_exception=True)
        return Response({"message": "beneficiary deleted successfully"}, status=status.HTTP_200_OK)

class CreatePayrollPinAPIView(APIView):
    permission_classes = [IsAuthenticated, UserIsActive, CheckPin]
    serializer_class = CreateTransactionPinSerializer
    @swagger_auto_schema(request_body=CreateTransactionPinSerializer)
    def post(self, request):
        """ Create a new pin """
        serializer = self.serializer_class(data=request.data, context={"request_user": request.user})
        serializer.is_valid(raise_exception=True)
        response = {
            "status": "success",
            "message": "transaction pin created",
        }
        return Response(response, status=status.HTTP_201_CREATED)

class PayrollPinUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, UserIsActive, UserHasPin]
    serializer_class = ChangeTransactionPinSerializer
    @swagger_auto_schema(request_body=ChangeTransactionPinSerializer)
    def put(self, request):
        serializer = self.serializer_class(data=request.data, context={"request_user": request.user})
        serializer.is_valid(raise_exception=True)
        return Response({
                "message": "transaction pin been has been changed successfully"
            }, status=status.HTTP_200_OK
        )
       