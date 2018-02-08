from rest_framework import serializers
from human_services.organizations import models

class OrganizationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Organization
        fields = ('id', 'name', 'description', 'website', 'email')
