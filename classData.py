from random import randint
from auxData import notes_lenght, notes_value
from synthesizer import Synthesizer, Player, Waveform


class MusicalNote(object):
    def __init__(self):
        self.on_or_off = True if randint(1, 10) < 10 else False
        if self.on_or_off:
            # Notas de C3 a B4
            self.value = randint(0, 13)
            self.note = notes_value[self.value]
        self.lenght_float = notes_lenght[randint(0, 4)]


class MelodyBar(object):
    def __init__(self):
        self.notes = []

    def generate_melody(self, number_bars, max_interval):
        lenght_bar = 0
        last_note = 0

        # A duração de um tempo é 64
        while lenght_bar != 64 * number_bars:
            note = MusicalNote()
            # Testa se a nota ultrapassa o limite de tempo
            if note.lenght_float + lenght_bar <= 64 * number_bars:
                if note.on_or_off:
                    # Não permite que a nota seja tenha um intervalo maior que o intervalo maximo
                    if last_note - max_interval < note.value < last_note + max_interval:
                        self.notes.append(note)
                        lenght_bar += note.lenght_float
                        last_note = note.value
                else:
                    self.notes.append(note)
                    lenght_bar += note.lenght_float
                    
    def print_melody(self):
        for note in self.notes:
            if note.on_or_off:
                print(str(note.note[0]) + " " + str(note.lenght_float))
            else:
                print("Break " + str(note.lenght_float))


class MelodyPlayer(object):
    def __init__(self):
        self.player = Player()
        self.synthesizer = Synthesizer(osc1_waveform=Waveform.sine, osc1_volume=1.0, use_osc2=False)

    def play_melody(self, melody, bpm):
        self.player.open_stream()

        for note in melody.notes:
            time = note.lenght_float/16 * 60/bpm

            if note.on_or_off:
                frequency = note.note[1]
                self.player.play_wave(self.synthesizer.generate_constant_wave(frequency, time))
            else:
                # caso seja uma pausa, não toca nota
                self.player.play_wave(self.synthesizer.generate_constant_wave(0, time))
