from random import randint
from auxData import notes_lenght, notes_value
from synthesizer import Synthesizer, Player, Waveform, Writer
import wave, os


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

            if self.note_is_valid(lenght_bar, note.on_or_off, last_note.on_or_off) is False:
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

    @staticmethod
    def note_is_valid(lenght_bar, note_on_or_off, last_note_on_or_off):
        # Impede que a primeira nota seja uma pausa
        if lenght_bar == 0 and not note_on_or_off:
            return False

        # Impede que ocorram duas pausas seguidas
        if last_note_on_or_off is False and note_on_or_off is False:
            return False


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
