from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from shops.models import Shop


USERS = [
    {
        'username': 'muskan',
        'password': 'muskan123',
        'first_name': 'Muskan',
        'last_name': 'Sharma',
        'shop_id': 'SS001',
        'shop_name': 'StepStyle Footwear',
        'shop_location': 'Mumbai, Maharashtra',
        'shop_category': 'Footwear',
    },
    {
        'username': 'ritesh',
        'password': 'ritesh123',
        'first_name': 'Ritesh',
        'last_name': 'Sharma',
        'shop_id': 'TF001',
        'shop_name': 'Trend Fashion',
        'shop_location': 'Delhi, NCR',
        'shop_category': 'Clothing',
    },
    {
        'username': 'priya',
        'password': 'priya123',
        'first_name': 'Priya',
        'last_name': 'Patel',
        'shop_id': 'PF001',
        'shop_name': 'Priya Fresh Mart',
        'shop_location': 'Ahmedabad, Gujarat',
        'shop_category': 'Grocery',
    },
]


class Command(BaseCommand):
    help = 'Seed 3 users with their shops'

    def handle(self, *args, **options):
        for u in USERS:
            user, created = User.objects.get_or_create(
                username=u['username'],
                defaults={
                    'first_name': u['first_name'],
                    'last_name':  u['last_name'],
                },
            )
            if created:
                user.set_password(u['password'])
                user.save()
                self.stdout.write(f"  Created user: {u['username']}")
            else:
                self.stdout.write(f"  User exists:  {u['username']}")

            shop, s_created = Shop.objects.get_or_create(
                owner=user,
                defaults={
                    'shop_id':  u['shop_id'],
                    'name':     u['shop_name'],
                    'location': u['shop_location'],
                    'category': u['shop_category'],
                },
            )
            if s_created:
                self.stdout.write(f"    Created shop: {u['shop_name']}")
            else:
                self.stdout.write(f"    Shop exists:  {u['shop_name']}")

        self.stdout.write(self.style.SUCCESS('\nDone. 3 users + shops seeded.'))
        self.stdout.write('\nLogin credentials:')
        for u in USERS:
            self.stdout.write(f"  {u['username']} / {u['password']}  ->  {u['shop_name']}")
