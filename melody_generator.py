import wave
import os
import json
import random

from synthesizer import Synthesizer, Player, Waveform, Writer

with open('notes.json') as notes:
    NOTES = json.load(notes)

NOTES_VALUE = NOTES["notes"]
NOTES_LENGHT = NOTES["lenghts"]

REST_CHANCE = 10  # Every note has 10% chance of being a rest

MAX_INTERVAL = 5  # Max interval is 5 semitones higher or lower than the previous note
NUMBER_OF_BARS = 2
BEATS_PER_MINUTE = 120

BAR_LENGHT = 64  # The duration of a bar is 4 whole notes(16 time units)
OSCILLATOR = "sawtooth"

WAVEFORM = {
    "sine": Waveform.sine,
    "sawtooth": Waveform.sawtooth,
    "square": Waveform.square,
    "triangle": Waveform.triangle
}


class MusicalNote(object):
    """
    A class used to represent a musical note

    Attributes
    ----------
    is_played : bool
        determines if the note is played or is a rest
    note : dict
        key -> "name" : str
            American notation of the note
        key -> "frequency" : float
            Frequency of the note in Hz
        key -> "value" : int
            Value that represents the note
    lenght : dict
        key -> "duration": int
            The duration of a note
        key -> "name": str
            American notation of the lenght
    """

    def __init__(self):
        """
        Randomly chooses the attributes of the object
        """

        self.is_played = True if random.randrange(100) >= REST_CHANCE else False
        self.note = random.choice(NOTES_VALUE)
        self.lenght = random.choice(NOTES_LENGHT)

    def is_on_time(self, lenght_bar, number_bars):
        """
        Verfy if the note exceeds the lenght of the bar

        Parameters
        ----------
        lenght_bar : int
            The current lenght of the melody bar
        number_bars : int
            The number of bars especified in generate_melody

        Returns
        -------
        bool
            True if the current lenght is not bigger than the maximum lenght,
            else False
        """

        max_leght = BAR_LENGHT * number_bars
        current_lenght = self.lenght["duration"] + lenght_bar

        return True if current_lenght <= max_leght else False

    def is_on_interval(self, max_interval, previous_note):
        """
        Verfy if the note exceeds the maximum interval

        Parameters
        ----------
        max_interval : int
            the maximum interval higher or lower than the note
        previous_note : MusicalNote
            the previous note used to calculate the current interval

        Returns
        -------
        bool
            True if the interval is inside the maximum interval,
            else False
        """

        high_interval = previous_note.note["value"] + max_interval
        low_interval = previous_note.note["value"] - max_interval

        return True if low_interval <= self.note["value"] <= high_interval else False

    def is_valid(self, lenght_bar, number_bars, previous_note, max_interval):
        """
        Tests if the note is valid by calling verification methods

        Parameters
        ----------
        lenght_bar : int
            The current lenght of the melody bar
        number_bars : int
            The number of bars especified in generate_melody
        max_interval : int
            the maximum interval higher or lower than the note
        previous_note : MusicalNote
            the previous note used to calculate the current interval

        Returns
        -------
        bool
            True if the note is valid,
            else False
        """

        # Prevents two rests in a row
        if previous_note.is_played is False and self.is_played is False:
            return False

        # Check if the note is inside of the interval
        if self.is_on_time(lenght_bar, number_bars) is False:
            return False

        # Test if the note fits in the bar lenght
        if self.is_on_interval(max_interval, previous_note) is False:
            return False

        return True


class Melody(object):
    """
    A class used to represent a melody

    Attributes
    ----------
    notes : list
        array of MusicalNote objects
    lenght : int
        the current lenght of the melody
    """

    def __init__(self):
        """
        Initialize the empty array of notes and melody lenght as 0
        """

        self.notes = list()
        self.lenght = 0

    def generate_melody(self, number_bars, max_interval):
        """
        Generates a melody by creating random notes and adding to the array

        Parameters
        ----------
        number_bars : int
            The number of bars of this melody
        max_interval : int
            the maximum interval of this melody
        """

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
        """
        Generates the first note of a melody, this note can't be a rest

        Returns
        -------
        MusicalNote
            The first note of the melody
        """

        first_note = MusicalNote()

        while first_note.is_played is False:  # Prevents the first note from being a rest
            first_note = MusicalNote()

        self.add_note_to_melody(first_note)

        return first_note

    def add_note_to_melody(self, note):
        """
        Adds the note to melody and its lenght to the current lenght

        Parameters
        ----------
        note : MusicalNote
            the note to be add to the melody
        """

        self.notes.append(note)
        self.lenght += note.lenght["duration"]

    def print_melody(self):
        """
        Prints the melody stored in the notes attribute
        """

        for note in self.notes:
            if note.is_played:
                print(f'{note.note["name"]}\t\t{note.lenght["duration"]}\t{note.lenght["name"]}')
            else:
                print(f'Rest\t{note.lenght["duration"]}\t{note.lenght["name"]}')


class MelodyPlayer(object):
    """
    A class used to play the melody generated by Melody

    Attributes
    ----------
    player : Player
        an object that plays the melody
    synthesizer : Synthesizer
        an object that characterizes the sound of the melody
    """

    def __init__(self, oscillator):
        """
        Instantiate the synthesizer and the player

        Parameters
        ----------
        oscillator : str
            defines the shape of the Waveform
        """

        self.player = Player()

        self.synthesizer = Synthesizer(osc1_waveform=WAVEFORM[oscillator])

    def play_melody(self, melody, bpm):
        """
        Plays the melody in a certain bpm

        Parameters
        ----------
        melody : Melody
            the melody that will be played
        bpm : int
            beats per minute that determine the speed the melody is played
        """

        self.player.open_stream()

        for note in melody.notes:
            wave_sound = self.generate_waves(note, bpm)
            self.player.play_wave(wave_sound)

    def save_melody(self, melody, bpm):
        """
        Saves the melody as WAV

        Saves each note individually and then concatenate then
        in a sigle WAV file

        Parameters
        ----------
        melody : Melody
            the melody that will be played
        bpm : int
            beats per minute that of the melody
        """

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
        """
        Auxiliary method for save_melody

        Code found on https://bit.ly/2EoFjIU

        Parameters
        ----------
        outfile : str
            path to output file
        data : list
            an array of WAV parameters
        """

        with wave.open(outfile, 'wb') as output:
            output.setparams(data[0][0])
            output.writeframes(data[0][1])
            output.writeframes(data[1][1])

        data.clear()

    def generate_waves(self, note, bpm):
        """
        Generate the wave that represents a note

        Parameters
        ---------
        note : MusicalNote
            The note that will be turned into wave
        bpm : int
            beats per minute that determines the lenght

        Returns
        -------
        ndarray
            an array that represents the normalized wave
        """

        lenght = note.lenght["duration"] / 16 * 60 / bpm

        # If the note is not played, the frequency is 0
        frequency = note.note["frequency"] if note.is_played else 0

        return self.synthesizer.generate_constant_wave(frequency, lenght)


if __name__ == "__main__":
    melody_bar = Melody()
    melody_bar.generate_melody(NUMBER_OF_BARS, MAX_INTERVAL)
    melody_bar.print_melody()

    melody_player = MelodyPlayer(OSCILLATOR)
    melody_player.play_melody(melody_bar, BEATS_PER_MINUTE)

    melody_player.save_melody(melody_bar, BEATS_PER_MINUTE)
