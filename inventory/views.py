# inventory/views.py
import logging
from django.core.cache import cache
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from .models import Item
from .serializers import ItemSerializer

logger = logging.getLogger(__name__)

class ItemView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            logger.info(f"Item created: {serializer.data}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        logger.error("Item creation failed")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, item_id):
        cache_key = f"item_{item_id}"
        item = cache.get(cache_key)
        if not item:
            try:
                item = Item.objects.get(id=item_id)
                cache.set(cache_key, item, timeout=60*15)  # Cache for 15 minutes
            except Item.DoesNotExist:
                logger.error(f"Item {item_id} not found")
                return Response({'detail': 'Item not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ItemSerializer(item)
        logger.info(f"Item retrieved: {serializer.data}")
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, item_id):
        try:
            item = Item.objects.get(id=item_id)
        except Item.DoesNotExist:
            logger.error(f"Item {item_id} not found for update")
            return Response({'detail': 'Item not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ItemSerializer(item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            cache.set(f"item_{item_id}", item, timeout=60*15)
            logger.info(f"Item updated: {serializer.data}")
            return Response(serializer.data, status=status.HTTP_200_OK)
        logger.error("Item update failed")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, item_id):
        try:
            item = Item.objects.get(id=item_id)
            item.delete()
            cache.delete(f"item_{item_id}")
            logger.info(f"Item {item_id} deleted")
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Item.DoesNotExist:
            logger.error(f"Item {item_id} not found for deletion")
            return Response({'detail': 'Item not found'}, status=status.HTTP_404_NOT_FOUND)
