from rest_framework import serializers


class SelectPackageSerializer(serializers.Serializer):
    package_name = serializers.ChoiceField(choices=['standard', 'enterprise'])
    payment_method_id = serializers.CharField(max_length=100, required=True)
