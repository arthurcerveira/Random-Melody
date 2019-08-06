from random import randint
from auxData import notes_lenght, notes_value
from synthesizer import Synthesizer, Player, Waveform


class MusicalNote(object):
    def __init__(self):
        self.on_or_off = True if randint(1, 10) < 10 else False
        self.value = 0
        if self.on_or_off:
            # Notas de C3 a B4
            self.value = randint(0, 13)
            self.note = notes_value[self.value]
        self.lenght = notes_lenght[randint(0, 4)]


class MelodyBar(object):
    def __init__(self):
        self.notes = []

    def generate_melody(self, number_bars, max_interval):
        self.notes.clear()

        lenght_bar = 0
        last_note = MusicalNote()

        # A duração de um tempo é 64
        while lenght_bar != 64 * number_bars:
            note = MusicalNote()

            # Impede que a primeira nota seja uma pausa
            if lenght_bar == 0 and not note.on_or_off:
                continue

            # Impede que ocorram duas pausas seguidas
            if last_note.on_or_off is False and note.on_or_off is False:
                continue

            # Testa se a nota ultrapassa o limite de tempo
            if note.lenght + lenght_bar <= 64 * number_bars:
                if note.on_or_off:
                    # Não permite que a nota seja tenha um intervalo maior que o intervalo maximo
                    if last_note.value - max_interval < note.value < last_note.value + max_interval:
                        self.notes.append(note)
                        lenght_bar += note.lenght
                        last_note = note
                else:
                    self.notes.append(note)
                    lenght_bar += note.lenght
                    last_note = note

    def print_melody(self):
        for note in self.notes:
            if note.on_or_off:
                print(str(note.note[0]) + " " + str(note.lenght))
            else:
                print("Break " + str(note.lenght))


class MelodyPlayer(object):
    def __init__(self):
        self.player = Player()
        self.synthesizer = Synthesizer(osc1_waveform=Waveform.sine, osc1_volume=1.0, use_osc2=False)

    def play_melody(self, melody, bpm):
        self.player.open_stream()

        for note in melody.notes:
            time = note.lenght/16 * 60/bpm

            if note.on_or_off:
                frequency = note.note[1]
                self.player.play_wave(self.synthesizer.generate_constant_wave(frequency, time))
            else:
                # Caso seja uma pausa, não toca nota
                self.player.play_wave(self.synthesizer.generate_constant_wave(0, time))
