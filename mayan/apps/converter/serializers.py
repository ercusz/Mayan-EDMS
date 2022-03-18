from rest_framework import serializers

from .models import Asset


class AssetSerializer(serializers.HyperlinkedModelSerializer):
    image_url = serializers.HyperlinkedIdentityField(
        lookup_url_kwarg='asset_id',
        view_name='rest_api:asset-image'
    )
    download_url = serializers.HyperlinkedIdentityField(
        lookup_url_kwarg='asset_id',
        view_name='rest_api:asset-download'
    )

    class Meta:
        extra_kwargs = {
            'url': {
                'lookup_url_kwarg': 'asset_id',
                'view_name': 'rest_api:asset-detail'
            },
        }
        fields = (
            'file', 'label', 'id', 'image_url', 'internal_name', 'url', 'download_url'
        )
        model = Asset
