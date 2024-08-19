from django.shortcuts import render

# Create your views here.
import requests
import smtplib, os, jwt
from .emails import *
from django.utils import timezone
from rest_framework import pagination, generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from .models import Log, Message, UserData
from .pagination import CustomResponsePagination
from .serializers import MessageSerializer, UserSerializer
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

admin = 'noreply@fedgen.net'
domain = 'mail.fedgen.net'
pwd = 'I;GK7tzsAIkF'
port = 465
secret = "QYmXTKt6bnzaFi76H7R88FQ"

jwt_secret = os.environ['JWT_SECRET_KEY']

class CheckAuth(APIView):
    def post(self, request):
        if request.headers['Authorization']:
            token  = request.headers['Authorization']
            if not token:
                raise AuthenticationFailed('Unauthenticated')
            try:
                payload = jwt.decode(token, jwt_secret, algorithms=['HS256'])
            except jwt.ExpiredSignatureError:
                raise AuthenticationFailed('Unathenticated')
            return payload
        else:
            raise AuthenticationFailed('Unathenticated')

class EmailVerification(APIView):
    def post(self, request):
        try:
            response = Response()
            message = MIMEMultipart('alternative')
            url = request.data['url']
            token = request.data['token']
            to = request.data['to']
            if token == secret:
                message["Subject"] = "Verify Your email on FEDGEN"
                message["From"] = admin
                message['To'] = to
                plain_text = """\
                From: %s
                To: %s
                Subject: %s
                
                Please verify your email on FEDGEN to gain full access to your account. Follow this link %s
                """ % (admin, to, "Verify your email", url)
                Email = email_verification%(url)
                # Convert message to MIMEText objects
                part1 = MIMEText(plain_text, "plain")
                part2 = MIMEText(Email, "html")
                # Import objects into message
                message.attach(part1)
                message.attach(part2)
                try:
                    smtp_server = smtplib.SMTP_SSL(domain, port)
                    smtp_server.ehlo()
                    smtp_server.login(admin, pwd)
                    smtp_server.sendmail(admin, to, message.as_string())
                    smtp_server.close()
                    new_log = Log(time=timezone.now(), email_type="Email Verification", destination=to, status="delivered")
                    new_log.save()
                    response.data = {
                        "ok": True,
                        "details": "Email sent successfully!"
                    }
                    response.status_code = 200
                except Exception as ex:
                    new_log = Log(time=timezone.now(), email_type="Email Verification", destination=to, status="failed", info=str(ex))
                    new_log.save()
                    response.data = {
                        "ok": False,
                        "details": str(ex)
                    }
                    response.status_code = 400
            else:
                raise AuthenticationFailed('Unauthorized!')
        except KeyError:
            response.data = {
                "ok": False,
                "details": "Invalid request"
            }
            response.status_code = 400
        return response
class ResetPassword(APIView):
    """
    Email Notification when user resets password
    """
    def post(self, request):
        try:
            response = Response()
            message = MIMEMultipart('alternative')
            url = request.data['url']
            token = request.data['token']
            to = request.data['to']
            if token == secret:
                message["Subject"] = "Reset Your password"
                message["From"] = admin
                message['To'] = to
                plain_text = """\
                From: %s
                To: %s
                Subject: %s
                
                . Follow this link %s to reset your password
                """ % (admin, to, "Verify your email", url)
                Email = """\
                <html>
                    <body>
                        <h1>Reset Your password</h1>
                        <p>To reset your password, follow this link %s </p>
                    </body>
                </html>
                """ % (url)
                # Convert message to MIMEText objects
                part1 = MIMEText(plain_text, "plain")
                part2 = MIMEText(Email, "html")
                # Import objects into message
                message.attach(part1)
                message.attach(part2)
                try:
                    smtp_server = smtplib.SMTP_SSL(domain, port)
                    smtp_server.ehlo()
                    smtp_server.login(admin, pwd)
                    smtp_server.sendmail(admin, to, message.as_string())
                    smtp_server.close()
                    new_log = Log(time=timezone.now(), email_type="Password Reset", destination=to, status="delivered")
                    new_log.save()
                    response.data = {
                        "ok": True,
                        "details": "Email sent successfully!"
                    }
                    response.status_code = 200
                except Exception as ex:
                    new_log = Log(time=timezone.now(), email_type="Password Reset", destination=to, status="failed")
                    new_log.save()
                    response.data = {
                        "ok": False,
                        "details": ex
                    }
                    response.status_code = 400
            else:
                raise AuthenticationFailed('Unauthorized!')
        except KeyError:
            response.data = {
                "ok": False,
                "details": "Invalid request"
            }
            response.status_code = 400
        return response

class Author(APIView):
    def post(self, request):
        try:
            response = Response()
            message = MIMEMultipart('alternative')
            token = request.data['token']
            filter = request.data['filter']
            to = request.data['to']
            if token == secret:
                if  filter == "post_approve":
                    name = request.data['first_name']
                    title = request.data['title']
                    message["Subject"] = "PHIS Post Approved"
                    message["From"] = admin
                    message['To'] = to
                    plain_text = """\
                    From: %s
                    To: %s
                    Subject: %s
                    
                    Congratulations your post %s, has been approved by our reviewers.
                    """ % (admin, to, "PHIS Post Approved", title)
                    Email = post_approved%(name, title)
                    # Convert message to MIMEText objects
                    part1 = MIMEText(plain_text, "plain")
                    part2 = MIMEText(Email, "html")
                    # Import objects into message
                    message.attach(part1)
                    message.attach(part2)
                elif filter == "post_decline":
                    name = request.data['first_name']
                    title = request.data['title']
                    reason = request.data['reason']
                    message["Subject"] = "PHIS Post Declined"
                    message["From"] = admin
                    message['To'] = to
                    plain_text = """\
                    From: %s
                    To: %s
                    Subject: %s

                    Hello %s,
                    
                    Sorry your post %s, has been declined by our reviewers.
                    Reason: 
                    %s
                    """ % (admin, to, "PHIS Post Declined", name, title, reason)
                    Email = post_declined%(name, title, reason)
                    # Convert message to MIMEText objects
                    part1 = MIMEText(plain_text, "plain")
                    part2 = MIMEText(Email, "html")
                    # Import objects into message
                    message.attach(part1)
                    message.attach(part2)
                elif filter == "author_approve":
                    name = request.data['first_name']
                    message["Subject"] = "PHIS Author application approved"
                    message["From"] = admin
                    message['To'] = to
                    plain_text = """\
                    From: %s
                    To: %s
                    Subject: %s
                    
                    Congratulations %s, you have been approved to create posts on our platform.
                    """ % (admin, to, "PHIS Author application approved", name)
                    Email = author_approved%(name)
                    # Convert message to MIMEText objects
                    part1 = MIMEText(plain_text, "plain")
                    part2 = MIMEText(Email, "html")
                    # Import objects into message
                    message.attach(part1)
                    message.attach(part2)
                elif filter == "author_declined":
                    name = request.data['first_name']
                    message["Subject"] = "PHIS Author aplication declined"
                    message["From"] = admin
                    message['To'] = to
                    plain_text = """\
                    From: %s
                    To: %s
                    Subject: %s
                    
                    Sorry your application tp be an author has been declined at the moment by our reviewers.
                    """ % (admin, to, "PHIS Author application declined")
                    Email = author_declined%(name)
                    # Convert message to MIMEText objects
                    part1 = MIMEText(plain_text, "plain")
                    part2 = MIMEText(Email, "html")
                    # Import objects into message
                    message.attach(part1)
                    message.attach(part2)
                else:
                    raise AuthenticationFailed('Invalid request')

                try:
                    smtp_server = smtplib.SMTP_SSL(domain, port)
                    smtp_server.ehlo()
                    smtp_server.login(admin, pwd)
                    smtp_server.sendmail(admin, to, message.as_string())
                    smtp_server.close()
                    new_log = Log(time=timezone.now(), email_type="Author", destination=to, status="delivered")
                    new_log.save()
                    response.data = {
                        "ok": True,
                        "details": "Email sent successfully!"
                    }
                    response.status_code = 200
                except Exception as ex:
                    new_log = Log(time=timezone.now(), email_type="Author", destination=to, status="failed")
                    new_log.save()
                    response.data = {
                        "ok": False,
                        "details": ex
                    }
                    response.status_code = 400
                
            else:
                raise AuthenticationFailed('Unauthorized!')
        except KeyError:
            response.data = {
                "ok": False,
                "details": "Invalid request"
            }
            response.status_code = 400
        return response


class Messages(APIView):
    """Add a new notification for a user"""
    def post(self, request):
        CheckAuth.post(self, request)
        data = request.data
        response = Response()

        if data.get("to") is not None:
            recipient = UserData.objects.filter(auth_user_id=data.get("to")).first()
            if recipient is not None:
                message = Message(user=recipient, message=data.get("message"), url=data.get("url", None))
                recipient.num_read += 1
                recipient.save()
                message.save()

                response.data = {
                    "ok": True,
                    "object": "Message",
                    "created": "True"
                }
                response.status_code = 201
        else:
            response.data = {
                "ok": False,
                "error": "BadRequest"
            }
            response.status_code = 400

        return response
    
    def patch(self, request):
        response = Response()
        payload = CheckAuth.post(self, request)
        user = UserData.objects.filter(auth_user_id=payload['id']).first()
        
        if user is not None:
            unread_messages = user.messages.filter(is_read=False)
            for m in unread_messages:
                m.is_read = True
                m.save()
            user.num_read = 0
            user.save()
            response.data = {
                "ok": True,
                "object": "Message",
                "read": True
            }
            response.status_code = 200
        else:
            response.data = {"ok": False, "error": "NotFound"}
            response.status_code = 404

        return response

    def get(self, request):
        response = Response()
        payload = CheckAuth.post(self, request)
        user = UserData.objects.filter(auth_user_id=payload['id']).first()
        if user is not None:
            response.data = {
                "ok": True,
                "count": user.num_read
            }
            response.status_code = 200
        else:
            response.data = {
                "ok": False,
                "count": 0
            }
            response.status_code = 404

        return response


class GetUserMessages(generics.ListAPIView):
    serializer_class = MessageSerializer
    pagination_class = CustomResponsePagination

    def get_queryset(self):
        payload = CheckAuth.post(self, self.request)
        user = UserData.objects.filter(auth_user_id=payload['id']).first()
        
        if user is not None:
            return user.messages.all().order_by("-date")
        
        # Return an empty queryset if the user is not found
        return UserData.objects.none()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        if not queryset.exists():
            return Response(data={"ok": False}, status=status.HTTP_404_NOT_FOUND)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
        
class UserSignupEvent(APIView):
    def post(self, request):
        response = Response()
        data = request.data

        CheckAuth.post(self, request)
        user = UserData.objects.filter(auth_user_id=data['auth_user_id']).first()
        if user is None:
            serializer = UserSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

        response.data = {"ok": True}
        response.status_code = 200

        return response
    
class Populate(APIView):
    def post(self, request):
        response = Response()
        CheckAuth.post(self, request)

        data = request.data
        if data.get("list"):
            for u in data.get("list", []):
                user = UserData.objects.filter(auth_user_id=u['auth_user_id']).first()
                if user is None:
                    serializer = UserSerializer(data=u)
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                else:
                    continue

            response.data = {
                "ok": True,
                "populated": True
            }
            response.status_code = 201

        else:
            response.data = {"ok": False, "error": "BadRequest"}
            response.status_code = 400

        return response