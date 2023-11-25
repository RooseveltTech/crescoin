from rest_framework.exceptions import APIException
from rest_framework import status
from rest_framework import permissions

class NoPermission(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = {
        "error": "error",
        "params": "you are not permitted to perform this action",
    }
    default_code = "Not permitted"

class AccountSuspended(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = {
        "error": "error",
        "message": "account suspended please contact admin",
    }
    default_code = "Not permitted"

class IncorrectPin(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = {
        "error": "error",
        "params": "incorrect pin",
    }
    default_code = "Not permitted"

class NoPin(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = {
        "error": "error",
        "params": "create user pin first",
    }
    default_code = "Not permitted"

class HasPin(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = {
        "error": "error",
        "params": "user already have pin",
    }
    default_code = "Not permitted"

class UserNotVerified(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = {
        "error": "error",
        "params": "user not verified",
    }
    default_code = "Not permitted"

class UserVerified(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = {
        "error": "error",
        "params": "user already verified",
    }
    default_code = "Not permitted"


class AllowUser(permissions.BasePermission):
    """
    View based permission user is active.
    """

    def has_permission(self, request, view):
        if request.user.user_is_deleted:
            raise NoPermission()
        elif request.user.user_is_suspended:
            raise AccountSuspended()
        else:
            return True
        
class UserIsActive(permissions.BasePermission):
    """
    View based permission employee is active.
    """

    def has_permission(self, request, view):
        if request.user.user_is_active:
            return True
        else:
            raise NoPermission()
        
class UserHasPin(permissions.BasePermission):
    """
    View based permission user is active.
    """

    def has_permission(self, request, view):
        if request.user.transaction_pin is None or request.user.transaction_pin == "":
            raise NoPin()
        else:
            return True
        
class CheckPin(permissions.BasePermission):
    """
    View based permission user is active.
    """

    def has_permission(self, request, view):
        if request.user.transaction_pin:
            raise HasPin()
        else:
            return True
        
class UserIsVerified(permissions.BasePermission):
    """
    View based permission user is active.
    """

    def has_permission(self, request, view):
        if request.user.user_is_active:
            raise UserNotVerified()
        else:
            return True
        
class UserAlreadyVerified(permissions.BasePermission):
    """
    View based permission user is active.
    """

    def has_permission(self, request, view):
        if request.user.user_is_active:
            raise UserVerified()
        else:
            return True