from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import status, exceptions
from rest_framework.exceptions import ValidationError

from core.models import VERIFICATION_TYPE


User = get_user_model()

class RegistrationSerializer(serializers.ModelSerializer):
    """Serializers registration requests and creates a new user."""
    confirm_password = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'phone_number', 'user_tag', 'country', 'password', 'confirm_password')
        extra_kwargs = {
            'first_name': {'required': True, 'allow_null': False, 'allow_blank': False},
            'last_name': {'required': True, 'allow_null': False, 'allow_blank': False},
            'phone_number': {'required': True, 'allow_null': True, 'allow_blank': True},
            'country': {'required': True, 'allow_null': False, 'allow_blank': False},
            'user_tag': {'required': True, 'allow_null': False, 'allow_blank': False},
        }

    def validate(self, attrs):

        email = attrs.get('email')
        phone_number = attrs.get('phone_number')
        user_tag = attrs.get('user_tag')
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError({"message": "email already exists"})
        if User.objects.filter(phone_number=phone_number).exists():
            raise serializers.ValidationError({"message": "phone_number already exists"})
        if User.objects.filter(user_tag=user_tag).exists():
            raise serializers.ValidationError({"message": "user_tag already exists"})
        if attrs.get("confirm_password") != attrs.get("password"):
            raise serializers.ValidationError({"message": "password and confirm_password does not match"})
        
        attrs['password'] = make_password(attrs['password'])
        del attrs['confirm_password']
        return attrs
    
class CustomTokenObtainSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        email = attrs[self.username_field].lower()

        authenticate_kwargs = {
            self.username_field: email,
            'password': attrs['password'],
        }
        try:
            authenticate_kwargs['request'] = self.context['request']
            authenticate_kwargs['email'] = authenticate_kwargs['email'].lower()
        except KeyError:
            pass
        '''
            Checking if the user exists by getting the email(username field) from authentication_kwargs.
            If the user exists we check if the user account is active.
            If the user account is not active we raise the exception and pass the message.
            Thus stopping the user from getting authenticated altogether.

            And if the user does not exist at all we raise an exception with a different error message.
            Thus stopping the execution right there.
        '''
        try:
            user = User.objects.get(email=authenticate_kwargs['email'])
            
            if user.user_is_deleted is True:
                self.error_messages['error'] = (
                    'account does not exist'
                )
                raise exceptions.AuthenticationFailed(
                    self.error_messages['error']
                )
            
            if user.is_active is False:
                self.error_messages['error'] = (
                    'account disabled. please contact admin'
                )
                raise exceptions.AuthenticationFailed(
                    self.error_messages['error']
                )
                
            if user.user_is_suspended is True:
                self.error_messages['error'] = (
                    'account suspended. please contact admin'
                )
                raise exceptions.AuthenticationFailed(
                    self.error_messages['error']
                )

        except User.DoesNotExist:
            self.error_messages['no_active_account'] = (
                'account does not exist')
            raise exceptions.AuthenticationFailed(
                self.error_messages['no_active_account'],
            )
        authenticate_kwargs['email'] = user.email.lower()

        self.user = authenticate(email=user.email.lower(), password = authenticate_kwargs['password'])
        if self.user is None:
            self.error_messages['no_active_account'] = (
                'password is incorrect. please enter a correct password')
            raise exceptions.AuthenticationFailed(
                self.error_messages['no_active_account'],
            )
        
        return super().validate(attrs)
        
class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainSerializer

class VerificationSerializer(serializers.Serializer):
    
    verification_type = serializers.ChoiceField(required=True, choices=VERIFICATION_TYPE)
    driving_license = serializers.CharField(max_length=255, required=False, allow_null=True, allow_blank=True)
    passport_number = serializers.CharField(max_length=255, required=False, allow_null=True, allow_blank=True)
    passport_expiry_date = serializers.DateField(required=False, allow_null=True)
    passport_issue_date = serializers.DateField(required=False, allow_null=True)
    driving_license_number = serializers.CharField(max_length=255, required=False, allow_null=True, allow_blank=True)
    driving_license_expiry_date = serializers.DateField(required=False, allow_null=True)
    driving_license_issue_date = serializers.DateField(required=False, allow_null=True)

    def validate(self, attrs):
        today_date = timezone.now().date()
        least_expiry_date = today_date + timezone.timedelta(days=7)
        request_user = self.context.get('request_user')
        if attrs.get('verification_type') == "PASSPORT":
            if attrs.get('passport_number') is None:
                raise ValidationError({"passport_number": "This field is required"})
            if len(attrs.get('passport_number')) < 5:
                raise ValidationError({"passport_number": "passport_number must be at least 5 characters"})
            if attrs.get('passport_issue_date') is None:
                raise ValidationError({"passport_issue_date": "This field is required"})
            if attrs.get('passport_issue_date') > today_date:
                raise ValidationError({"passport_issue_date": "passport_issue_date cannot be in the future"})
            if attrs.get('passport_expiry_date') is None:
                raise ValidationError({"passport_expiry_date": "This field is required"})
            if attrs.get('passport_expiry_date') == attrs.get('passport_issue_date'):
                raise ValidationError({"passport_expiry_date": "passport_expiry_date cannot be the same as passport_issue_date"})
            if attrs.get('passport_expiry_date') < attrs.get('passport_issue_date'):
                raise ValidationError({"passport_expiry_date": "passport_expiry_date cannot be less than passport_issue_date"})
            if attrs.get('passport_expiry_date') < least_expiry_date:
                raise ValidationError({"passport_expiry_date": f"passport_expiry_date must be at least {least_expiry_date}"})
 
            request_user.passport_number = attrs.get('passport_number')
            request_user.passport_expiry_date = attrs.get('passport_expiry_date')
            request_user.passport_issue_date = attrs.get('passport_issue_date')
            request_user.verification_type = attrs.get('verification_type')
            request_user.user_is_active = True
            request_user.save()

        elif attrs.get('verification_type') == "DRIVING_LICENSE":
            if attrs.get('driving_license_number') is None:
                raise ValidationError({"message": "driving license number is required"})
            if len(attrs.get('driving_license_number')) < 5:
                raise ValidationError({"driving_license_number": "driving_license_number must be at least 5 characters"})
            if attrs.get('driving_license_issue_date') is None:
                raise ValidationError({"driving_license_issue_date": "This field is required"})
            if attrs.get('driving_license_issue_date') > today_date:
                raise ValidationError({"driving_license_issue_date": "driving_license_issue_date cannot be in the future"})
            if attrs.get('driving_license_expiry_date') is None:
                raise ValidationError({"driving_license_expiry_date": "This field is required"})
            if attrs.get('driving_license_expiry_date') == attrs.get('driving_license_issue_date'):
                raise ValidationError({"driving_license_expiry_date": "driving_license_expiry_date cannot be the same as driving_license_issue_date"})
            if attrs.get('driving_license_expiry_date') < attrs.get('driving_license_issue_date'):
                raise ValidationError({"driving_license_expiry_date": "driving_license_expiry_date cannot be less than driving_license_issue_date"})
            if attrs.get('driving_license_expiry_date') < least_expiry_date:
                raise ValidationError({"driving_license_expiry_date": f"driving_license_expiry_date must be at least {least_expiry_date}"})
            
            request_user.driving_license_number = attrs.get('driving_license_number')
            request_user.driving_license_expiry_date = attrs.get('driving_license_expiry_date')
            request_user.driving_license_issue_date = attrs.get('driving_license_issue_date')
            request_user.verification_type = attrs.get('verification_type')
            request_user.user_is_active = True
            request_user.save()
        
        else:
            raise ValidationError({"message": "verification_type is invalid"})

        return attrs