from rest_framework import serializers
from .models import DataSet
import simplejson

class DataSetSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
      ret = super(DataSetSerializer, self).to_representation(instance)
      ret['Data'] = simplejson.loads(ret['Data'])
      return ret

    DataSet_Poster = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = DataSet
        # fields = ('DataSet_Title', 'DataSet_Description')
        fields = '__all__'
        read_only_fields = ('DataSet_Posted',)
