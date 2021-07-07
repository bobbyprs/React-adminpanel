# from login_app.django_app.settings import MEDIA_ROOT
from django.conf.urls import url
from django.contrib.sessions.models import Session
from django.http.response import JsonResponse
from django.shortcuts import render,HttpResponse
from rest_framework import request, serializers, viewsets
from django.conf import settings
from rest_framework import response
from rest_framework import authentication
from .models import Admin, Clinical, User,Staff
from .serializers import ClinicalSerializer, UserSerializer,AdminSerializer,StaffSerializer
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework import permissions
from django.contrib import auth
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie, csrf_protect
from rest_framework.views import APIView
from django.views.generic import View
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from .permission import IsAdminOrReadOnly
import requests
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from pytrials.client import ClinicalTrials
import pandas as pd
import csv
import pandas as pd
import datetime
import uuid
import json
import os
from django.conf import settings
from rest_framework.permissions import BasePermission, IsAuthenticated, SAFE_METHODS
import re
# Create your views here.

ct = ClinicalTrials()

class UserViewSet(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    queryset=User.objects.all()
    serializer_class = UserSerializer

class AdminViewSet(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    queryset=Admin.objects.all()
    serializer_class = AdminSerializer


# class CsrfExemptSessionAuthentication(SessionAuthentication):

#     def enforce_csrf(self, request):
#         return  # 

# @method_decorator(ensure_csrf_cookie, name='dispatch')
class StaffViewSet(viewsets.ModelViewSet,IsAdminOrReadOnly):
    authentication_classes = [TokenAuthentication]
    queryset=Staff.objects.all()
    permission_classes= [IsAdminOrReadOnly]
    serializer_class = StaffSerializer


class LoginView(APIView):
  # permission_classes = (permissions.AllowAny,)
  def post(self, request, format=None):
    data = self.request.data

    username = data['username']
    password = data['password']


    try:
      user = auth.authenticate(username=username, password=password)
      # user=User.objects.get(username=request.data['username'])

      # if user.check_password(request.data['password']):
          
      #     staff_status=self.request.user.is_staff
      #     super_user=self.request.user.is_superuser
      #     user_id = self.request.user.id
      #     print(user_id)
      #     return Response({'session_key':token.key,"staff_status":staff_status,"super_user":super_user,'userId':user_id})
      # return Response('Password incorrect',status=status.HTTP_401_UNAUTHORIZED)

      if user is not None:
        auth.login(request, user)
        staff_status=request.user.is_staff
        super_user=request.user.is_superuser
        user_id = request.user.id
        token, _=Token.objects.get_or_create(user=user)
        print(user_id)
        return Response({"success": "User authenticated", "username": username,"session_key":token.key,"staff_status":staff_status,"super_user":super_user,'userId':user_id})
        
      # else:
      #   return Response({"error": "Error Authenticated",})
    except:
      return Response('User Name or Password incorrect',status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
  def post(self, request, format=None):
    try:
      auth.logout(request)
      return Response({'success': 'Loggout Out'})
    except:
      return Response({'error': 'something went wrong'})


class Getdata(APIView):

  permission_classes = [IsAuthenticated]

  def post(self,request,format=None):
    list1=[]
    list2=[]
    try:
      
        disease=request.data["disease"]
        minrank=request.data["minrank"]
        maxrank=request.data["maxrank"]
        user = User.objects.get(username=request.user)       
    except:
        return Response({"error":"Every Field is Required"})
   
    field=['NCTId','Condition','ArmGroupDescription','InterventionType','BriefTitle','OrgFullName','OfficialTitle','BriefSummary','ReferencePMID','SecondaryOutcomeMeasure','PrimaryOutcomeMeasure','DetailedDescription','Phase','ArmGroupType','ArmGroupInterventionName','InterventionDescription','OverallStatus','StudyType','LastUpdatePostDate']
    d=disease.split()
    b="+".join(d)          #diseases
    fie="%2C".join(field)  #fields
    url=f"https://clinicaltrials.gov/api/query/study_fields?expr={b}&fields={fie}&min_rnk={minrank}&max_rnk={maxrank}&fmt=json"
    response = requests.get(url)
    json_file=response.json()
    jso=json_file['StudyFieldsResponse']['StudyFields']
    y=json.dumps(jso)
    d = json.loads(y)
    l=[]
    for i in range(len(d)):
        for key,value in d[i].items():
            if type(value)==type(l):
                s=""
                for m in  value:
                    s+=str(m)
                d[i][key]=s
    y=json.dumps(d)
    f = open("media/demofile3.json", "w")
    f.write(y)
    f.close()
    FileName = '{}{:-%Y%m%d%H%M%S}.csv'.format(str(uuid.uuid4().hex), datetime.datetime.now())
    with open('media/demofile3.json', encoding='utf-8-sig') as f_input:
        df = pd.read_json(f_input)
        df.to_csv(f"media/{FileName}", encoding='utf-8', index=False)
    
    list1=[]
    list2=[]
    df = pd.read_csv (f"media/{FileName}")
    url1=f"https://clinicaltrials.gov/api/query/study_fields?expr={b}&fields=EligibilityCriteria&min_rnk={minrank}&max_rnk={maxrank}&fmt=json"
    response=requests.get(url1)
    y=response.json()
    for i in range(0,abs(int(minrank)-int(maxrank))+1):
        e=y['StudyFieldsResponse']['StudyFields'][i]['EligibilityCriteria']
        if e:
            if y['StudyFieldsResponse']['StudyFields'][i]['EligibilityCriteria'][0]:
                e=y['StudyFieldsResponse']['StudyFields'][i]['EligibilityCriteria'][0]
                pattern=re.compile(r'Inclusion Criteria|INCLUSION CRITERIA|inclusion criteria|Inclusion criteria|inclusion Criteria|inclusion|DISEASE CHARACTERISTICS')
                pattern2=re.compile(r'Exclusion Criteria|EXCLUSION CRITERIA|exclusion criteria|Exclusion criteria|exclusion Criteria|exclusion|CONCURRENT THERAPY')
                matches1=pattern.finditer(e)
                matches2=pattern2.finditer(e)
                a=""
                b=""
                if pattern2.search(e) and pattern.search(e):
                    for match in matches1:
                        l=match.span()
                    for match in matches2:
                        m=match.span()
                    for o in range(l[1]+1,m[0]):
                        a+=e[o]
                    for j in range(m[1]+1,len(e)):
                            b+=e[j]
                    list1.append(a)
                    list2.append(b)
                elif not pattern2.search(e) and pattern.search(e):
                    m=(23,len(e)-2)
                    for mk in range(m[0],m[1]):
                        a+=e[mk]
                    b=""
                    list1.append(a)
                    list2.append("NA")
                elif not pattern.search(e) and pattern2.search(e):
                    m=(23,len(e)-2)
                    for mk in range(m[0],m[1]):
                        a+=e[mk]
                    b=""
                    list1.append(a)
                    list2.append("NA")
                elif not pattern.search(e) and not pattern2.search(e):
                    list1.append(str(y['StudyFieldsResponse']['StudyFields'][i]['EligibilityCriteria'][0]))
                    list2.append(str(y['StudyFieldsResponse']['StudyFields'][i]['EligibilityCriteria'][0]))
        else:
            list1.append("NA")
            list2.append("NA")

    csv_input = pd.read_csv(f"media/{FileName}")
    csv_input['Inclusion Criteria'] = list1
    csv_input['Exclusion Criteria'] = list2
    csv_input.to_csv(f'media/{FileName}', index=False)
    FILENAME=f"http://127.0.0.1:8000/media/{FileName}"
    data1={"name":str(user),"disease":disease,"minrank":minrank,"maxrank":maxrank,"url":FILENAME}
    serializer=ClinicalSerializer(data=data1)
    if serializer.is_valid():
        serializer.save()
    
    return Response({"jsonurl":url,"filelink":FILENAME})
    # min = request.data['minrank']
    # max = request.data['maxrank']
    # disease = request.data['disease']
    # disease1 = disease.split(' ')[0]
    # disease2 = disease.split(' ')[1]
    # owner = str(self.request.user)
    # print(owner)
    # fields = "NCTId,Condition,ArmGroupDescription,InterventionType,BriefTitle,OrgFullName,OfficialTitle,BriefSummary,ReferencePMID,SecondaryOutcomeMeasure,PrimaryOutcomeMeasure,EligibilityCriteria,DetailedDescription,Phase,ArmGroupType,ArmGroupInterventionName,InterventionDescription,OverallStatus,StudyType,LastUpdatePostDate"
    # arr = fields.split(',')
    # print(len(arr))

    # if disease is not None:
    #   clinical_fields = ct.get_study_fields(
    #       search_expr=disease1+disease2,
    #       fields=arr,
    #       max_studies=int(max),
    #       fmt="csv",
    #   )

    #   csvdata=pd.DataFrame.from_records(clinical_fields[1:],columns=clinical_fields[0])
      
    #   FileName='{}{:-%Y%m%d%H%M%S}.csv'.format(str(uuid.uuid4().hex),datetime.datetime.now())
    #   csvdata.to_csv(f"./media/{FileName}",encoding='utf-8',index=False ,header=True)
    #   print(FileName)
    #   ress ={}
    #   ress['filelink'] =str(os.path.join('http://127.0.0.1:8000/media/',FileName))
    #   urls=f"http://127.0.0.1:8000/media/{FileName}"
    #   list1=[]
    #   list2=[]
    #   clinical_fields2 = ct.get_study_fields(
    #       search_expr=disease1+disease2,
    #       fields=arr,
    #       max_studies=int(max),
    #       fmt="json",
    #   )
    #   response=requests.get( clinical_fields2)
    #   y=response.json()
    #   for i in range(0,abs(int(min)-int(max))+1):
    #       e=y['StudyFieldsResponse']['StudyFields'][i]['EligibilityCriteria']
    #       if e:
    #           if y['StudyFieldsResponse']['StudyFields'][i]['EligibilityCriteria'][0]:
    #               e=y['StudyFieldsResponse']['StudyFields'][i]['EligibilityCriteria'][0]
    #               pattern=re.compile(r'Inclusion Criteria|INCLUSION CRITERIA|inclusion criteria|Inclusion criteria|inclusion Criteria|inclusion|DISEASE CHARACTERISTICS')
    #               pattern2=re.compile(r'Exclusion Criteria|EXCLUSION CRITERIA|exclusion criteria|Exclusion criteria|exclusion Criteria|exclusion|CONCURRENT THERAPY')
    #               matches1=pattern.finditer(e)
    #               matches2=pattern2.finditer(e)
    #               a=""
    #               b=""
    #               if pattern2.search(e) and pattern.search(e):
    #                   for match in matches1:
    #                       l=match.span()
    #                   for match in matches2:
    #                       m=match.span()
    #                   for o in range(l[1]+1,m[0]):
    #                       a+=e[o]
    #                   for j in range(m[1]+1,len(e)):
    #                           b+=e[j]
    #                   list1.append(a)
    #                   list2.append(b)
    #               elif not pattern2.search(e) and pattern.search(e):
    #                   m=(23,len(e)-2)
    #                   for mk in range(m[0],m[1]):
    #                       a+=e[mk]
    #                   b=""
    #                   list1.append(a)
    #                   list2.append("NA")
    #               elif not pattern.search(e) and pattern2.search(e):
    #                   m=(23,len(e)-2)
    #                   for mk in range(m[0],m[1]):
    #                       a+=e[mk]
    #                   b=""
    #                   list1.append(a)
    #                   list2.append("NA")
    #               elif not pattern.search(e) and not pattern2.search(e):
    #                   list1.append(str(y['StudyFieldsResponse']['StudyFields'][i]['EligibilityCriteria'][0]))
    #                   list2.append(str(y['StudyFieldsResponse']['StudyFields'][i]['EligibilityCriteria'][0]))
    #       else:
    #           list1.append("NA")
    #           list2.append("NA")

    #   csv_input = pd.read_csv(f"media/{FileName}")
    #   csv_input['Inclusion Criteria'] = list1
    #   csv_input['Exclusion Criteria'] = list2
    #   csv_input.to_csv(f'media/{FileName}', index=False)
    #   FILENAME=f"http://127.0.0.1:8000/media/{FileName}"
    #   print(FILENAME)
    #   print(urls)
    #   data1 = {"minrank":min,"maxrank":max,"disease":disease,"url":str(urls),'name':owner}
    
    #   serializer = ClinicalSerializer(data = data1)
      
    #   if serializer.is_valid():
    #     serializer.save()
    #     print(serializer.data)
        
    #   return Response({"filelink":FILENAME},status=status.HTTP_200_OK)
    # else:
    #   return Response({"error":"url error"})

  def get(self,request):
    serializer = Clinical.objects.all()
    serialized =ClinicalSerializer(serializer,many=True)
    return Response (serialized.data)

@method_decorator(ensure_csrf_cookie,name='dispatch')
class GetCsrfToken(APIView):
  permission_classes = [permissions.AllowAny]

  def get(self,request,format=None):
    return Response({'successs':'CSRF cookie set'})


{
"minrank":"1",
"maxrank":"100",
"disease":"Lung Cancer"
}

    