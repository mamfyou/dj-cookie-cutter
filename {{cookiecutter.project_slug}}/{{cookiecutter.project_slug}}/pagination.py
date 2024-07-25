from rest_framework.pagination import PageNumberPagination


class MainPagination(PageNumberPagination):
    page_size_query_param = 'page_size'
    max_page_size = 50
    choices = [num for num in range(5, 51)]

    def get_page_size(self, request):
        if self.page_size_query_param:
            choices = self.choices
            try:
                page_size = int(request.query_params.get(self.page_size_query_param, 10))
            except ValueError:
                page_size = 10
            if page_size not in choices:
                page_size = 10
            return page_size
