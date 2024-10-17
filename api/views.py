from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Bundle, Product
from .serializers import ProductDataSerializer
from .serializers import ProductListSerializer
from .ai_service import ProductBundleGenerator


@api_view(['POST'])
def recommend_bundles(request):

    products_data = request.data
    generator = ProductBundleGenerator()

    try:
        # Generate recommended bundles using the AI model
        ai_bundles = generator.generate_bundles(products_data)

        if 'error' in ai_bundles:
            return Response(ai_bundles['error'], status=status.HTTP_400_BAD_REQUEST)

        return Response({'bundles': ai_bundles}, status=200)

    except Exception as e:
        return Response({'error': str(e)}, status=500)
