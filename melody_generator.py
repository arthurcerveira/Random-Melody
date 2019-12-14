import wave
import os
import json
from random import randint

from synthesizer import Synthesizer, Player, Waveform, Writer

REST_CHANCE = 10  # Every note has 10% chance of being a rest

with open('notes.json') as notes:
    NOTES = json.load(notes)

NOTES_VALUE = NOTES["frequency"]
NOTES_LENGHT = NOTES["lenght"]
TOTAL_VALUES = len(NOTES_VALUE) - 1
TOTAL_LENGHTS = len(NOTES_LENGHT) - 1

MAX_INTERVAL = 5
NUMBER_OF_BARS = 2
BEATS_PER_MINUTE = 120


class MusicalNote(object):
    def __init__(self):
        self.is_played = True if randint(1, 100) >= REST_CHANCE else False
        self.value = 0
        if self.is_played:
            self.value = randint(0, TOTAL_VALUES)
            self.note = NOTES_VALUE[self.value]
        self.lenght = NOTES_LENGHT[randint(0, TOTAL_LENGHTS)]

    def is_on_time(self, lenght_bar, number_bars):
        # Testa se a nota ultrapassa o limite de tempo
        max_leght = 64 * number_bars
        current_lenght = self.lenght + lenght_bar
        return True if current_lenght <= max_leght else False

    def is_valid(self, lenght_bar, last_note_was_played):
        # Impede que a primeira nota seja uma pausa
        if lenght_bar == 0 and not self.is_played:
            return False

        # Impede que ocorram duas pausas seguidas
        if last_note_was_played is False and self.is_played is False:
            return False

        return True

    def is_on_interval(self, max_interval, last_note_value):
        # Não permite que a nota seja tenha um intervalo maior que o intervalo maximo
        high_interval = last_note_value + max_interval
        low_interval = last_note_value - max_interval

        return True if low_interval < self.value < high_interval else False


class MelodyBar(object):
    def __init__(self):
        self.notes = []

    def generate_melody(self, number_bars, max_interval):
        self.notes.clear()

        lenght_bar = 0
        last_note = MusicalNote()

        # A duração de um tempo é 64 unidades de tempo
        while lenght_bar != 64 * number_bars:
            note = MusicalNote()

            if note.is_valid(lenght_bar, last_note.is_played) and note.is_on_time(lenght_bar, number_bars):
                if note.is_played:
                    if note.is_on_interval(max_interval, last_note.value):
                        lenght_bar = self.add_note_to_melody(note, lenght_bar)
                        last_note = note
                else:
                    lenght_bar = self.add_note_to_melody(note, lenght_bar)
                    last_note = note

    def print_melody(self):
        for note in self.notes:
            if note.on_or_off:
                print(str(note.note[0]) + " " + str(note.lenght))
            else:
                print("Break " + str(note.lenght))

    def add_note_to_melody(self, note, lenght_bar):
        self.notes.append(note)
        lenght_bar += note.lenght
        return lenght_bar


class MelodyPlayer(object):
    def __init__(self):
        self.player = Player()
        self.synthesizer = Synthesizer(osc1_waveform=Waveform.sawtooth, osc1_volume=1.0, use_osc2=False)

    def play_melody(self, melody, bpm):
        self.player.open_stream()

        for note in melody.notes:
            wave_sound = self.generate_waves(note, bpm)
            self.player.play_wave(wave_sound)

    def save_melody(self, melody, bpm):
        writer = Writer()
        outfile = "melody.wav"
        next_note = "note.wav"
        data = []

        for note in melody.notes:
            sound = self.generate_waves(note, bpm)

            if note == melody.notes[0]:
                # Gera a primeira nota
                writer.write_wave(outfile, sound)
                continue

            writer.write_wave(next_note, sound)

            infiles = [outfile, next_note]

            for infile in infiles:
                w = wave.open(infile, 'rb')
                data.append([w.getparams(), w.readframes(w.getnframes())])
                w.close()

            output = wave.open(outfile, 'wb')
            output.setparams(data[0][0])
            output.writeframes(data[0][1])
            output.writeframes(data[1][1])
            output.close()

            # Deleta o arquivo da nota
            os.remove(next_note)

            data.clear()

    def generate_waves(self, note, bpm):
        lenght = note.lenght / 16 * 60 / bpm

        if note.on_or_off:
            frequency = note.note[1]
            return self.synthesizer.generate_constant_wave(frequency, lenght)
        else:
            # Caso seja uma pausa, não toca nota
            return self.synthesizer.generate_constant_wave(0, lenght)


if __name__ == "__main__":
    melody_bar = MelodyBar()
    melody_bar.generate_melody(NUMBER_OF_BARS, MAX_INTERVAL)
    melody_bar.print_melody()

    melody_player = MelodyPlayer()
    melody_player.play_melody(melody_bar, BEATS_PER_MINUTE)

    melody_player.save_melody(melody_bar, BEATS_PER_MINUTE)
