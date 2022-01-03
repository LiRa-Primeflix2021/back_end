from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.authtoken.models import Token
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from user_app.api.serializers import RegistrationSerializer, ChangePasswordAndEmailSerializer
# from user_app import models
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from primeflix_app.models import User


# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# registration and log out
# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
 

@api_view(['POST',])
def registration_view(request):
    
    if (request.method == 'POST'):
        serializer = RegistrationSerializer(data=request.data)
        
        data={}
        if serializer.is_valid():
            temp_user = serializer.save()
            
            data['reponse'] = "Registration successful"
            data['username'] = temp_user.username
            data['email'] = temp_user.email
            
            # token = Token.objects.get(user=account).key
            # data['token'] = token
            
            refresh = RefreshToken.for_user(temp_user)
            
            data['token'] = {
                                'refresh' : str(refresh),
                                'access' : str(refresh.access_token),      
                            }
        
        else:
            data = serializer.errors    
            
        return Response(data)
        

@api_view(['POST',])
def logout_view(request):
    
    if (request.method == 'POST'):
        request.user.auth_token.delete()
        return Response(status=status.HTTP_200_OK)
    
            
# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# update password and email
# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
         

class ChangePasswordAndEmail(APIView):
    pass
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            temp_user = User.objects.get(pk=request.user.id)
        except User.DoesNotExist:
            return Response('Error : User doesn\'t exist in database', status=status.HTTP_404_NOT_FOUND)
        
        serializer = ChangePasswordAndEmailSerializer(temp_user)
        return Response(serializer.data) 
    
    def put(self, request):
        temp_user = request.user
        serializer = ChangePasswordAndEmailSerializer(temp_user, data=request.data)
        data={}
        if(serializer.is_valid()):
            temp_user = serializer.save()
            data['reponse'] = "Registration successful"
            data['username'] = temp_user.username

            refresh = RefreshToken.for_user(temp_user)
            data['token'] = {
                                'refresh' : str(refresh),
                                'access' : str(refresh.access_token),      
                            }
        else:
            data = serializer.errors    
            
        return Response(serializer.data)
