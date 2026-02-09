# type: ignore  # Management command - type safety not critical for seeding script
"""Management command to seed database with sample products."""

from decimal import Decimal

from django.core.management.base import BaseCommand

from products.models import Category, Product


class Command(BaseCommand):
    """Seed the database with sample archive products."""

    help = "Populate database with sample archives for testing"

    def handle(self, *args, **options):
        """Execute the seed command."""
        self.stdout.write("Starting database seed...")

        categories_data = [
            {"name": "Ancient Texts", "slug": "ancient-texts"},
            {"name": "Historical Documents", "slug": "historical-documents"},
            {"name": "Scientific Research", "slug": "scientific-research"},
            {"name": "Art Collections", "slug": "art-collections"},
        ]

        categories = {}
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(**cat_data)
            categories[cat_data["slug"]] = category
            status = "Created" if created else "Already exists"
            self.stdout.write(f"  {status}: {category.name}")

        products_data = [
            {
                "title": "The Lost Manuscripts of Alexandria",
                "slug": "lost-manuscripts-alexandria",
                "tagline": "Recovered texts from the ancient library",
                "description": (
                    "A comprehensive collection of manuscripts believed to "
                    "have been lost in the fire of the Library of Alexandria."
                ),
                "category": "ancient-texts",
                "price": Decimal("29.99"),
                "is_featured": True,
            },
            {
                "title": "Da Vinci's Secret Notebooks",
                "slug": "da-vinci-secret-notebooks",
                "tagline": "Unpublished sketches and notes",
                "description": (
                    "Recently discovered notebooks containing "
                    "Leonardo da Vinci's private observations and "
                    "experimental designs."
                ),
                "category": "historical-documents",
                "price": Decimal("39.99"),
                "is_featured": True,
            },
            {
                "title": "Einstein's Personal Letters",
                "slug": "einstein-personal-letters",
                "tagline": "Correspondence with fellow scientists",
                "description": (
                    "A collection of letters exchanged between Einstein and "
                    "other prominent scientists of his time."
                ),
                "category": "scientific-research",
                "price": Decimal("24.99"),
                "is_featured": False,
            },
            {
                "title": "Renaissance Art Collection",
                "slug": "renaissance-art-collection",
                "tagline": "High-resolution scans of masterpieces",
                "description": (
                    "Digitally restored images of Renaissance paintings and "
                    "sculptures from private collections."
                ),
                "category": "art-collections",
                "price": Decimal("19.99"),
                "is_featured": True,
            },
            {
                "title": "Mayan Codices Translation",
                "slug": "mayan-codices-translation",
                "tagline": "Complete translations with annotations",
                "description": (
                    "Scholarly translation of the four surviving "
                    "Mayan codices with historical context."
                ),
                "category": "ancient-texts",
                "price": Decimal("34.99"),
                "is_featured": False,
            },
        ]

        for prod_data in products_data:
            category_slug = prod_data.pop("category")
            prod_data["category"] = categories.get(category_slug)

            product, created = Product.objects.get_or_create(
                slug=prod_data.get("slug", ""),
                defaults=prod_data,
            )

            status = "Created" if created else "Already exists"
            self.stdout.write(f"  {status}: {product.title}")

        self.stdout.write(
            self.style.SUCCESS("\nDatabase seeded successfully!")
        )
