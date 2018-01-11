from django.contrib import messages
from django.contrib.auth.mixins import AccessMixin
from django.shortcuts import get_object_or_404, redirect

from .models import DataSet


class UserIsOwnerMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        dataset = get_object_or_404(DataSet, pk=self.kwargs['pk'])
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        elif request.user != dataset.creator:
            messages.add_message(
                request, 
                messages.ERROR, 
                'You have no permission to access this Dataset'
                )
            return redirect('index')
        return super().dispatch(request, *args, **kwargs)
