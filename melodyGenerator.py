from classData import MelodyBar, MelodyPlayer

melody_bar = MelodyBar()
melody_bar.generate_melody(2, 5)
melody_bar.print_melody()

melody_player = MelodyPlayer()
melody_player.play_melody(melody_bar, 120)
