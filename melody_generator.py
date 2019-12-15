import wave
import os
import json
import random

from synthesizer import Synthesizer, Player, Waveform, Writer

REST_CHANCE = 10  # Every note has 10% chance of being a rest

with open('notes.json') as notes:
    NOTES = json.load(notes)

NOTES_VALUE = NOTES["notes"]
NOTES_LENGHT = NOTES["lenghts"]

MAX_INTERVAL = 5  # Max interval is 5 semitones higher or lower than the previous note
NUMBER_OF_BARS = 2
BEATS_PER_MINUTE = 120

BAR_LENGHT = 64  # The duration of a bar is 4 whole notes(16 time units)
SHAPE = "sawtooth"

WAVEFORM = {
    "sine": Waveform.sine,
    "sawtooth": Waveform.sawtooth,
    "square": Waveform.square,
    "triangle": Waveform.triangle
}


class MusicalNote(object):
    def __init__(self):
        self.is_played = True if random.randint(1, 100) >= REST_CHANCE else False
        self.note = random.choice(NOTES_VALUE)
        self.lenght = random.choice(NOTES_LENGHT)

    def is_on_time(self, lenght_bar, number_bars):
        max_leght = 64 * number_bars
        current_lenght = self.lenght["duration"] + lenght_bar

        return True if current_lenght <= max_leght else False

    def is_on_interval(self, max_interval, previous_note_value):
        high_interval = previous_note_value + max_interval
        low_interval = previous_note_value - max_interval

        return True if low_interval <= self.note["value"] <= high_interval else False

    def is_valid(self, lenght_bar, number_of_bars, previous_note, max_interval):
        # Prevents two rests in a row
        if previous_note.is_played is False and self.is_played is False:
            return False

        # Check if the note is inside of the interval
        if self.is_on_time(lenght_bar, number_of_bars) is False:
            return False

        # Test if the note fits in the bar lenght
        if self.is_on_interval(max_interval, previous_note.note["value"]) is False:
            return False

        return True


class MelodyBar(object):
    def __init__(self):
        self.notes = []
        self.lenght = 0

    def generate_melody(self, number_bars, max_interval):
        self.notes.clear()
        self.lenght = 0

        first_note = self.generate_first_note()
        previous_note = first_note

        while self.lenght != BAR_LENGHT * number_bars:
            note = MusicalNote()

            if note.is_valid(self.lenght, number_bars, previous_note, max_interval):
                self.add_note_to_melody(note)
                previous_note = note

    def generate_first_note(self):
        first_note = MusicalNote()

        while first_note.is_played is False:  # Prevents the first note from being a rest
            first_note = MusicalNote()

        self.add_note_to_melody(first_note)

        return first_note

    def add_note_to_melody(self, note):
        self.notes.append(note)
        self.lenght += note.lenght["duration"]

    def print_melody(self):
        for note in self.notes:
            if note.is_played:
                print(f'{note.note["name"]}\t\t{note.lenght["duration"]}\t{note.lenght["name"]}')
            else:
                print(f'Rest\t{note.lenght["duration"]}\t{note.lenght["name"]}')


class MelodyPlayer(object):
    def __init__(self):
        self.player = Player()

        self.synthesizer = Synthesizer(osc1_waveform=WAVEFORM[SHAPE], osc1_volume=1.0, use_osc2=False)

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
                # Generates the first note
                writer.write_wave(outfile, sound)
                continue

            writer.write_wave(next_note, sound)

            infiles = [outfile, next_note]

            for infile in infiles:
                with wave.open(infile, 'rb') as w:
                    data.append([w.getparams(), w.readframes(w.getnframes())])

            self.append_note(outfile, data)

            # Deletes the note file
            os.remove(next_note)

    @staticmethod
    def append_note(outfile, data):
        output = wave.open(outfile, 'wb')
        output.setparams(data[0][0])
        output.writeframes(data[0][1])
        output.writeframes(data[1][1])
        output.close()

        data.clear()

    def generate_waves(self, note, bpm):
        lenght = note.lenght["duration"] / 16 * 60 / bpm

        # If the not is not played, the frequency is 0
        frequency = note.note["frequency"] if note.is_played else 0

        return self.synthesizer.generate_constant_wave(frequency, lenght)


if __name__ == "__main__":
    melody_bar = MelodyBar()
    melody_bar.generate_melody(NUMBER_OF_BARS, MAX_INTERVAL)
    melody_bar.print_melody()

    melody_player = MelodyPlayer()
    melody_player.play_melody(melody_bar, BEATS_PER_MINUTE)

    melody_player.save_melody(melody_bar, BEATS_PER_MINUTE)
