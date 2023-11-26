from rest_framework import status
from rest_framework.decorators import APIView
from rest_framework.response import Response

from rest_framework.permissions import IsAuthenticated

from main.models import Beneficiary
from main.permissions import CheckPin, UserHasPin, UserIsActive
from main.serializers import AllBeneficiarySerializer, ChangeTransactionPinSerializer, CreateBeneficiarySerializer, CreateTransactionPinSerializer, DeleteBeneficiarySerializer, FundAccountSerializer, GetExchangeForFundingAccountSerializer, GetExchangeRateSerializer, SendMoneySerializer
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

class CreateTransactionPinAPIView(APIView):
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

class UpdateTransactionPinAPIView(APIView):
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

class GetExchangeRateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GetExchangeRateSerializer
    def get(self, request):
        """ Get exchange rate """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({"rates":serializer.validated_data}, status=status.HTTP_200_OK)
    
class GetExchangeForFundingAccountAPIView(APIView):
    permission_classes = [IsAuthenticated, UserIsActive, UserHasPin]
    serializer_class = GetExchangeForFundingAccountSerializer
    def get(self, request):
        """ Fund account """
        currency_from = request.query_params.get('currency_from')
        serializer = self.serializer_class(data=request.data, context={"currency_from": currency_from})
        serializer.is_valid(raise_exception=True)
        return Response({"message":"successful"}, status=status.HTTP_200_OK)
    
class FundAccountAPIView(APIView):
    permission_classes = [IsAuthenticated, UserIsActive, UserHasPin]
    serializer_class = FundAccountSerializer
    @swagger_auto_schema(request_body=FundAccountSerializer)
    def post(self, request):
        """ Fund account """
        serializer = self.serializer_class(data=request.data, context={"request_user": request.user})
        serializer.is_valid(raise_exception=True)
        return Response({"response":serializer.validated_data}, status=status.HTTP_200_OK)
    
class SendMoneyAPIView(APIView):
    permission_classes = [IsAuthenticated, UserIsActive, UserHasPin]
    serializer_class = SendMoneySerializer
    @swagger_auto_schema(request_body=SendMoneySerializer)
    def post(self, request):
        """ Fund account """
        serializer = self.serializer_class(data=request.data, context={"request_user": request.user})
        serializer.is_valid(raise_exception=True)
        amount = serializer.validated_data.get("amount")
        receiver_tag = serializer.validated_data.get("receiver_tag")
        return Response({"message":f"you have send {amount} CRC to {receiver_tag}"}, status=status.HTTP_200_OK)
