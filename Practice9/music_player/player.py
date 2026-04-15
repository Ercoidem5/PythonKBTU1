import pygame
import os

class Player:
    def __init__(self, music_folder):
        pygame.mixer.init()
        self.tracks = []
        self.index = 0
        self.playing = False
        self.paused = False
        for file in os.listdir(music_folder):
                self.tracks.append(os.path.join(music_folder, file))

        self.tracks.sort()

    def get_track_name(self):
        if not self.tracks:
            return "No tracks found"
        return os.path.basename(self.tracks[self.index])

    def play(self):
        if not self.tracks:
            return
        if self.paused:
            pygame.mixer.music.unpause()
            self.paused = False
            self.playing = True
        else:
            pygame.mixer.music.load(self.tracks[self.index])
            pygame.mixer.music.play()
            self.playing = True

    def stop(self):
        pygame.mixer.music.stop()
        self.playing = False
        self.paused = False

    def pause(self):
        if self.playing and not self.paused:
            pygame.mixer.music.pause()
            self.paused = True

    def next_track(self):
        self.index = (self.index + 1) % len(self.tracks)
        self.playing = False
        self.paused = False
        self.play()

    def prev_track(self):
        self.index = (self.index - 1) % len(self.tracks)
        self.playing = False
        self.paused = False
        self.play()

    def get_pos(self):
        pos = pygame.mixer.music.get_pos()
        if pos < 0:
            return "0:00"
        seconds = pos // 1000
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes}:{seconds:02d}"

    def is_track_finished(self):
        return self.playing and not pygame.mixer.music.get_busy() and not self.paused