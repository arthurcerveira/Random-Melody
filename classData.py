from random import randint
from auxData import notes_lenght, notes_value


class MusicalNote(object):
    def __init__(self):
        self.on_or_off = True if randint(1, 10) < 10 else False
        if self.on_or_off:
            self.value = notes_value[randint(0, 6)]
        self.lenght = notes_lenght[randint(0, 4)]


class MelodyBar(object):
    def __init__(self):
        self.notes = []

    def generate_melody(self, number_bars):
        lenght_bar = 0
        while lenght_bar != 64 * number_bars:
            note = MusicalNote()
            if note.lenght[1] + lenght_bar <= 64 * number_bars:
                self.notes.append(note)
                lenght_bar += note.lenght[1]
                # print(note.lenght[1])
                # print(lenght_bar)

    def print_melody(self):
        for note in self.notes:
            if note.on_or_off:
                print(str(note.value) + " " + str(note.lenght[1]))
            else:
                print("Break " + str(note.lenght[1]))
