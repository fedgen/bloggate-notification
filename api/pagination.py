from rest_framework import pagination
from rest_framework.response import Response

class CustomResponsePagination(pagination.PageNumberPagination):
    page_size = 10
    max_page_size = 50
    
    def get_paginated_response(self, data):
        count = self.page.paginator.count
        if count % self.page_size != 0:
            self.last_page = (count // self.page_size) + 1
        elif count % self.page_size == 0:
            self.last_page = count / self.page_size

        return Response({
            'links': {
                'next': self.get_next_link().replace('http://', 'https://') if self.get_next_link() else None,
                'previous': self.get_previous_link().replace('http://', 'https://') if self.get_previous_link() else None,
            },
            'count': self.page.paginator.count,
            'results': data,
            'pages': {
                'next_page': self.page.next_page_number() if self.get_next_link() else None,
                'current_page': self.page.number,
                'previous_page': self.page.previous_page_number() if self.get_previous_link() else None,
                'last_page': self.last_page
            }
        })
