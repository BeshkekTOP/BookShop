from rest_framework import serializers
from .models import Category, Author, Book, BookAuthors, Inventory


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name", "slug")


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ("id", "first_name", "last_name")


class InventorySerializer(serializers.ModelSerializer):
    available = serializers.IntegerField(read_only=True, source='available')

    class Meta:
        model = Inventory
        fields = ("stock", "reserved", "available")


class BookAuthorNestedSerializer(serializers.ModelSerializer):
    author = AuthorSerializer()

    class Meta:
        model = BookAuthors
        fields = ("author",)


class BookSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    authors = serializers.SerializerMethodField()
    inventory = InventorySerializer(read_only=True)
    average_rating = serializers.ReadOnlyField()

    class Meta:
        model = Book
        fields = (
            "id",
            "title",
            "isbn",
            "description",
            "category",
            "price",
            "rating",
            "average_rating",
            "pages",
            "publication_date",
            "cover_image",
            "is_active",
            "created_at",
            "updated_at",
            "authors",
            "inventory",
        )

    def get_authors(self, obj):
        qs = obj.book_authors.select_related("author")
        return AuthorSerializer([ba.author for ba in qs], many=True).data


class BookWriteSerializer(serializers.ModelSerializer):
    author_ids = serializers.ListField(child=serializers.IntegerField(), write_only=True)

    class Meta:
        model = Book
        fields = ("title", "isbn", "description", "category", "price", "author_ids")

    def create(self, validated_data):
        author_ids = validated_data.pop("author_ids", [])
        book = Book.objects.create(**validated_data)
        if author_ids:
            BookAuthors.objects.bulk_create([
                BookAuthors(book=book, author_id=aid) for aid in author_ids
            ])
        Inventory.objects.get_or_create(book=book, defaults={"stock": 0, "reserved": 0})
        return book

    def update(self, instance, validated_data):
        author_ids = validated_data.pop("author_ids", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if author_ids is not None:
            BookAuthors.objects.filter(book=instance).delete()
            BookAuthors.objects.bulk_create([
                BookAuthors(book=instance, author_id=aid) for aid in author_ids
            ])
        return instance




