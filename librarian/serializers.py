from rest_framework import serializers
from .models import BorrowRequest, ApprovedRequest, DeclinedRequest

class BorrowRequestSerializer(serializers.ModelSerializer):
    book_title = serializers.CharField(source='book.BookTitle', read_only=True)
    requested_by_name = serializers.CharField(source='requested_by.username', read_only=True)
    requested_at = serializers.SerializerMethodField()
    expires_at = serializers.SerializerMethodField()
    file_type = serializers.CharField(source='book.get_file_type', read_only=True)

    class Meta:
        model = BorrowRequest
        fields = '__all__'

    def get_requested_at(self, obj):
        return obj.requested_at.strftime('%Y-%m-%d')

    def get_expires_at(self, obj):
        return obj.expires_at.strftime('%Y-%m-%d')

class ApprovedRequestSerializer(serializers.ModelSerializer):
    book_title = serializers.CharField(source='book.BookTitle', read_only=True)
    requested_by_name = serializers.CharField(source='requested_by.username', read_only=True)
    requested_at = serializers.SerializerMethodField()
    file_type = serializers.CharField(source='book.get_file_type', read_only=True)

    class Meta:
        model = ApprovedRequest
        fields = '__all__'

    def get_requested_at(self, obj):
        return obj.requested_at.strftime('%Y-%m-%d')

class DeclinedRequestSerializer(serializers.ModelSerializer):
    book_title = serializers.CharField(source='book.BookTitle', read_only=True)
    requested_by_name = serializers.CharField(source='requested_by.username', read_only=True)
    requested_at = serializers.SerializerMethodField()
    file_type = serializers.CharField(source='book.get_file_type', read_only=True)

    class Meta:
        model = DeclinedRequest
        fields = '__all__'

    def get_requested_at(self, obj):
        return obj.requested_at.strftime('%Y-%m-%d')