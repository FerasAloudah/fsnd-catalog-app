from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from create_database import Base, Category, Item
import random

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


def empty_database():
    session.query(Category).delete()
    session.query(Item).delete()
    session.commit()


categories = ['PC', 'PS4', 'Xbox One', 'Nintendo Switch']
items = ['Resident Evil 2', 'Bloodborne', 'Super Mario Odyssey',
         'Zelda: Breath of the wild', 'Sekiro', 'Equilinox',
         'Devil May Cry 5', 'Dark Souls', 'Cuphead', 'Terraria']
descriptions = [
    '''
    Donec at rhoncus augue. Nam bibendum tortor ex, vitae porttitor turpis
    dignissim eget. Cras suscipit suscipit nisi
    nec blandit. Suspendisse quis nulla sed nisi mollis consectetur sed ac
    nunc. Ut eu ex nibh. Sed iaculis vestibulum
    commodo. Etiam a nunc vitae nulla interdum aliquam at eget sem.
    ''',
    '''
    Aenean nibh eros, porta non porta vulputate, lacinia nec ex. Duis rutrum
    velit ac felis tristique facilisis. Proin
     ac nulla vel metus vulputate dignissim. Vestibulum ante ipsum primis in
     faucibus orci luctus et ultrices posuere
     cubilia Curae; Aliquam mauris felis, sagittis eu eleifend sit amet,
    ''',
    '''
    Phasellus mollis venenatis semper. Sed mattis tortor at nulla ornare, nec
    dictum quam sodales. Maecenas enim purus,
    imperdiet in magna quis,
    ''',
    '''
    Cras ipsum dui, placerat ut augue nec, condimentum condimentum odio. Duis
    vel sapien ut neque aliquam ultrices quis
    ac mauris. Pellentesque aliquet est odio,
    ''',
    '''
    Quisque sit amet velit at mauris tempor mollis. Aenean facilisis sem non
    vestibulum placerat. Aliquam ac leo nunc.
    Vestibulum sed nibh nulla. Fusce convallis libero sem,
    ''',
    '''
    In convallis, lorem eget finibus varius, lectus felis blandit diam, sed
    convallis lacus ligula id sapien. In
    hendrerit aliquam turpis vitae mollis. Vestibulum a felis et elit suscipit
    venenatis ac ac ligula.
    ''',
    '''
    Duis elementum porttitor pellentesque. Nullam dui erat, condimentum id ante
    sed, consequat porttitor mauris.
    Praesent dolor eros, cursus feugiat egestas vitae, aliquam ac massa.
    '''
]

# Empty database to remove repeated categories and items.
print('Emptying database...')
empty_database()
print('Done!\n')

print('Populating database...')

for category in categories:
    session.add(Category(name=category))

session.commit()


for item in items:
    session.add(Item(name=item, description=random.choice(descriptions),
                     category_id=random.randrange(len(categories))+1))

session.commit()

print('Done!\n')

print('Printing added categories and items:')
categories_ = session.query(Category).all()
items_ = session.query(Item).all()

print('Categories: ')
for i, category in enumerate(categories_):
    print('%d> %s' % (i+1, category.name))

print('')

print('Items: ')
for i, item in enumerate(items_):
    print('%d> %s %s %s' % (i+1, item.name, categories[item.category_id-1],
                            item.description))
