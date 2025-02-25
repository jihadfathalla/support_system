from django.core.paginator import Paginator
from rest_framework.response import Response

from .constants import COUNT, DATA, LIMIT, PAGE


def paginate_queryset(request, queryset, serializer, context=None):
    items_per_page = 10
    if request.GET.get(LIMIT):
        items_per_page = request.GET.get(LIMIT)
    if request.GET.get("all"):
        items_per_page = max(len(queryset), 10)
    paginator = Paginator(queryset, items_per_page)
    page_number = request.GET.get(PAGE)

    page_obj = paginator.get_page(page_number)
    serializer = serializer(
        page_obj, many=True, context=context or {"action": "list", "request": request}
    )
    return Response(
        {
            COUNT: paginator.count,
            PAGE: page_obj.number if page_obj else None,
            DATA: serializer.data,
        }
    )
