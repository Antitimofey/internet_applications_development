from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status
from lab3_api.serializer import DatasetSerializer
from app_for_lab1.models import Dataset
from rest_framework.views import APIView
from rest_framework.decorators import api_view


class DatasetList(APIView):
    model_class = Dataset
    serializer_class = DatasetSerializer

    def get(self, request, format=None):
        datasets = self.model_class.objects.all()
        serializer = self.serializer_class(datasets, many=True)
        return Response(serializer.data)
    

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    

class DatasetDetail(APIView):
    model_class = Dataset
    serializer_class = DatasetSerializer

    def get(self, request, pk, format=None):
        dataset = get_object_or_404(self.model_class, pk=pk)
        serializer = self.serializer_class(dataset)
        return Response(serializer.data)
    
    def put(self, request, pk, format=None):
        dataset = get_object_or_404(self.model_class, pk)
        serializer = self.serializer_class(dataset, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk, format=None):
        dataset = get_object_or_404(self.model_class, pk)
        dataset.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['PUT'])
def put(request, pk, format=None):
    dataset = get_object_or_404(Dataset, pk=pk)
    serializer = DatasetSerializer(dataset, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

