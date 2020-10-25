from rest_framework import routers, serializers, viewsets

from content.models import Category



# class Categoryerializer(serializers.HyperlinkedModelSerializer):
#     elements = serializers.SlugRelatedField(
#         source='categoryprototype_set',
#         many=True,
#         slug_field='prototype_id',
#         read_only=True
#     )
#     class Meta:
#         model = Category
#         fields = ['title', 'elements']
#
# class CategoryViewSet(viewsets.ModelViewSet):
#     queryset = Category.objects.all()
#     serializer_class = Categoryerializer
#
#
#
# router = routers.DefaultRouter()
#
# router.register(r'project', CategoryViewSet)
# router.register(r'project/<int:project_id>', CategoryViewSet)