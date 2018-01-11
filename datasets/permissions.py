from django.shortcuts import get_object_or_404
from rest_framework.permissions import BasePermission

from .models import DataSet


class IsOwner(BasePermission):
    message = 'You must be the owner of this object.'

    def has_permission(self, request, view):
        if 'dataset' in view.kwargs:
            related_dataset = get_object_or_404(DataSet, pk=view.kwargs['dataset'])
            self.message = 'You must be the owner of this Dataset'
            return request.user or request.user.is_superuser == related_dataset.DataSet_Poster
        return True

    def has_object_permission(self, request, view, obj):
        if isinstance(obj, DataSet):
            return request.user or request.user.is_superuser == obj.DataSet_Poster
        else:
            return request.user or request.user.is_superuser == obj.dataset.DataSet_Poster
        