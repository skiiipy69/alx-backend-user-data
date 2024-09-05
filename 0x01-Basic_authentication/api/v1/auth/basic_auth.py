#!/usr/bin/env python3
"""
Module for authentication using Basic auth.
"""

from typing import TypeVar
from api.v1.auth.auth import Auth
import base64
from models.user import User


class BasicAuth(Auth):
    """Basic Authentication implementation."""

    def extract_base64_authorization_header(self,
                                            authorization_header: str) -> str:
        """Extract the Base64 part from the authorization header.

        Args:
            authorization_header (str): The full authorization header string.

        Returns:
            str: The Base64 part of the authorization header.
        """
        if authorization_header is None:
            return None
        if not isinstance(authorization_header, str):
            return None
        if not authorization_header.startswith('Basic '):
            return None

        return authorization_header.split(' ')[-1]

    def decode_base64_authorization_header(self,
                                           base64_authorization_header: str) -> str:
        """Decode the Base64 authorization header.

        Args:
            base64_authorization_header (str): The Base64 encoded string.

        Returns:
            str: The decoded string, or None if decoding fails.
        """
        if base64_authorization_header is None:
            return None
        if not isinstance(base64_authorization_header, str):
            return None

        try:
            decoded_bytes = base64.b64decode(
                base64_authorization_header.encode('utf-8')
            )
            return decoded_bytes.decode('utf-8')
        except Exception:
            return None

    def extract_user_credentials(self,
                                 decoded_base64_authorization_header: str) -> (str, str):
        """Extract user credentials from the decoded Base64 string.

        Args:
            decoded_base64_authorization_header (str): Decoded Base64 string.

        Returns:
            Tuple[str, str]: A tuple containing the user's email and password.
        """
        if decoded_base64_authorization_header is None:
            return (None, None)
        if not isinstance(decoded_base64_authorization_header, str):
            return (None, None)
        if ':' not in decoded_base64_authorization_header:
            return (None, None)

        email, password = decoded_base64_authorization_header.split(':', 1)
        return email, password

    def user_object_from_credentials(self,
                                     user_email: str, user_pwd: str) -> TypeVar('User'):
        """Retrieve a User object based on provided credentials.

        Args:
            user_email (str): The user's email.
            user_pwd (str): The user's password.

        Returns:
            User: The User object if credentials are valid, None otherwise.
        """
        if user_email is None or not isinstance(user_email, str):
            return None
        if user_pwd is None or not isinstance(user_pwd, str):
            return None

        try:
            users = User.search({"email": user_email})
            if not users:
                return None
            for user in users:
                if user.is_valid_password(user_pwd):
                    return user
            return None
        except Exception:
            return None

    def current_user(self, request=None) -> TypeVar('User'):
        """Retrieve the current user based on the request.

        Args:
            request: The HTTP request object.

        Returns:
            User: The User object if credentials are valid, None otherwise.
        """
        auth_header = self.authorization_header(request)
        if auth_header:
            token = self.extract_base64_authorization_header(auth_header)
            if token:
                decoded = self.decode_base64_authorization_header(token)
                if decoded:
                    email, password = self.extract_user_credentials(decoded)
                    if email:
                        return self.user_object_from_credentials(email, password)
        return None

