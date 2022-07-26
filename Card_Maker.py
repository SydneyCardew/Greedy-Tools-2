import csv
from Game_Classes import Card


def make_deck():
    deck = []
    csv.register_dialect('greedily', quoting=csv.QUOTE_ALL)
    with open('Data/cards.csv', newline='\n') as csv_file:
        csv_object = csv.reader(csv_file, dialect='greedily')
        for index, row in enumerate(csv_object):
            if index > 0:
                deck.append(Card(index + 2, row))
    return deck


def main():
    make_deck()


if __name__ == "__main__":
    main()
