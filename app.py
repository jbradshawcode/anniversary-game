"""Main game — loop, top-level wiring, and the transitions between modes."""
import pygame
import sys
from config import (SCREEN_WIDTH, SCREEN_HEIGHT, VB_MUSIC, KING_ST_MUSIC,
                    GYM_MUSIC, CHARACTER_MUSIC, CHAPTER_END_MUSIC, PHONE_THREAD)
from entities import Player
from scenes import (Gym, KingSt, Salutation, Garden, Corridor, Reception,
                    Courtyard, Passage, Courts, WilliamMorris, VolleyCourt)
from systems.scene_manager import SceneManager
from systems.input_handler import event_to_action
from systems.audio import MusicPlayer, SoundBank
from systems.dialogue import DialogueBox
from systems.story import StoryManager
from systems import save, screens
from systems.party import Party
from systems.cutscene import Cutscene
from systems.lighting import Lighting
from systems.modes import (TitleMode, PlayMode, GameOverMode, ResultsMode,
                           PhoneMode)
from systems.menu_flow import MenuFlow


_SCENE_NAMES = {1: "Gym", 2: "King Street", 3: "The Salutation", 4: "Beer Garden",
                5: "Corridor", 6: "Reception", 7: "Courtyard",
                8: "Passage", 9: "Netball Courts", 10: "Wetherspoons",
                11: "Volleyball"}


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN | pygame.SCALED)
        pygame.display.set_caption("Modular Game Framework")
        self.clock = pygame.time.Clock()
        self.running = True
        self.music = MusicPlayer()
        self.sfx = SoundBank()                   # shared UI/overworld SFX (dialogue blip, etc.)
        self._scene_music = {1: GYM_MUSIC, 2: KING_ST_MUSIC}   # scene_id -> loop (else silence)
        self._speaker_music = None                # character theme overriding scene music
        self.dialogue = DialogueBox(self.sfx)
        self.lighting = Lighting()

        gym = Gym()
        king_st = KingSt()
        salutation = Salutation()
        garden = Garden()
        corridor = Corridor()
        reception = Reception()
        courtyard = Courtyard()
        passage = Passage()
        courts = Courts()
        wetherspoons = WilliamMorris()
        self.court = VolleyCourt()

        self._start_col = (gym.walkable_cols[0] + gym.walkable_cols[1]) // 2
        self._start_row = (gym.walkable_rows[0] + gym.walkable_rows[1]) // 2
        self.player = Player(self._start_col, self._start_row)

        self.scene_manager = SceneManager()
        self.scene_manager.register(1, gym)
        self.scene_manager.register(2, king_st)
        self.scene_manager.register(3, salutation)
        self.scene_manager.register(4, garden)
        self.scene_manager.register(5, corridor)
        self.scene_manager.register(6, reception)
        self.scene_manager.register(7, courtyard)
        self.scene_manager.register(8, passage)
        self.scene_manager.register(9, courts)
        self.scene_manager.register(10, wetherspoons)
        self.scene_manager.register(11, self.court)
        self.scene_manager.start(1, self.player)

        self.party = Party()
        self.story = StoryManager()
        self.cutscene = Cutscene()
        self.story.bind(self.dialogue, self.scene_manager, self.player,
                        self.party, self.cutscene)
        self.cutscene.bind(self.dialogue, self.scene_manager, self.player,
                           self.party, self.story)
        self.cutscene.on_game_over = self._game_over
        self.story.on_launch_vb = self._launch_match
        self.story.on_week_end = self._week_end
        self.scene_manager.story = self.story
        self._vb_retry = False

        # The loop holds exactly one active Mode. PlayMode is persistent and
        # re-entered after interludes; pause is an overlay drawn on top of it.
        self.play = PlayMode(self)
        self.active = None
        self.pause = None
        self.open_title()

    # ---- top-level loop ----------------------------------------------------
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                continue
            action = event_to_action(event)
            if self.pause is not None:
                self.pause.handle_action(action)
            else:
                self.active.handle_action(action)

    def update(self, dt: float):
        if self.pause is not None:
            return                           # frozen while the pause menu is up
        self.active.update(dt)

    def draw(self):
        self.active.draw(self.screen)
        if self.pause is not None:
            self.pause.current_menu.draw(self.screen, dim=True)
        pygame.display.flip()

    # ---- mode transitions & MenuFlow context -------------------------------
    # The menu sub-state machine lives in MenuFlow; the methods below are the
    # terminal effects it calls back into (the MenuFlow context interface).
    def open_title(self):
        self.active = TitleMode(self)
        self.pause = None

    def open_pause(self):
        self.pause = MenuFlow('pause', self)

    def resume(self):
        self.active = self.play
        self.pause = None

    def quit_game(self):
        self.running = False

    def start_new(self):
        self.cutscene.active = False
        self._vb_retry = False
        self.story.restore(0, [], scene_id=None)
        self.scene_manager.jump_to(1, self.player)
        self.player.teleport(self._start_col, self._start_row)
        self.player.facing = 'down'
        self.play.mark_scene_synced()
        self.update_scene_music(self.scene_manager.current_id)
        self.story.sync_party(self.player)
        self.resume()
        self.story.begin()             # fire the opening cutscene (fade-in + intro)

    def load_slot(self, slot):
        data = save.load_game(slot)
        if not data:
            return
        self.cutscene.active = False
        self._vb_retry = False
        self.story.restore(data['beat'], data['flags'], scene_id=data['scene_id'],
                           vb_attempts=data.get('vb_attempts', 0))
        self.scene_manager.jump_to(data['scene_id'], self.player)
        self.player.teleport(data['tile_x'], data['tile_y'])
        self.player.facing = data['facing']
        self.play.mark_scene_synced()
        self.update_scene_music(self.scene_manager.current_id)
        self.story.sync_party(self.player)
        self.resume()

    def save_to_slot(self, slot):
        data = {
            'scene_id': self.scene_manager.current_id,
            'scene_name': _SCENE_NAMES.get(self.scene_manager.current_id, '?'),
            'tile_x': self.player.tile_x,
            'tile_y': self.player.tile_y,
            'facing': self.player.facing,
            'beat_name': self.story.beat['name'],
        }
        data.update(self.story.snapshot())
        save.save_game(slot, data)

    # ---- helpers PlayMode calls back into -----------------------------------
    def scene_title(self, scene_id):
        return _SCENE_NAMES.get(scene_id, "Scene {0}".format(scene_id))

    def update_scene_music(self, scene_id):
        track = self._scene_music.get(scene_id)
        if track:
            self.music.play(track)
        else:
            self.music.stop()

    def update_speaker_music(self):
        """While a character with a theme is talking, play it (from the start each
        time they begin); restore the scene's track once they stop. Called each
        play frame from PlayMode."""
        speaker = self.dialogue.speaker if self.dialogue.active else None
        theme = CHARACTER_MUSIC.get(speaker) if speaker else None
        if theme is not None:
            if speaker != self._speaker_music:
                self.music.restart(theme)
                self._speaker_music = speaker
        elif self._speaker_music is not None:
            self._speaker_music = None
            self.update_scene_music(self.scene_manager.current_id)

    def poll_vb_retry(self) -> bool:
        if self._vb_retry:
            self._vb_retry = False
            self._launch_match()
            return True
        return False

    # ---- volleyball orchestration ------------------------------------------
    def _launch_match(self):
        """Story hook: drop into the 3v3 (Leonard's lot) at the difficulty Dan
        picked in the vb_setup beat, running the controls warm-up first if asked."""
        level = ('easy' if self.story.has('w1_diff_easy')
                 else 'medium' if self.story.has('w1_diff_medium')
                 else 'hard')
        if self.story.has('w1_want_tut') and not self.story.has('w1_tut_done'):
            self._launch_tutorial(level)
            return
        self.court.configure('match', level)
        self.court.on_finish = self._end_volleyball
        self.music.play(VB_MUSIC)
        self.scene_manager.jump_to(11, self.player)

    def _launch_tutorial(self, level):
        """The warm-up: the 5-step controls tutorial, then straight into the match.
        No vball theme here — that's reserved for the real match; the gym theme
        carries over from the overworld."""
        self.court.configure('tutorial', level)
        self.court.on_finish = self._end_tutorial
        self.scene_manager.jump_to(11, self.player)

    def _end_tutorial(self):
        self.story.set_flag('w1_tut_done')   # records the warm-up; not an advance flag
        self._launch_match()

    def _end_volleyball(self):
        won = self.court.score[0] > self.court.score[1]
        self.story.vb_attempts += 1
        if won:
            self.scene_manager.jump_to(1, self.player)
            self.play.mark_scene_synced()
            self.update_scene_music(1)              # back in the gym -> gym theme
            self.story.set_flag('w1_won_vb')        # -> Dan asks about the pub
        else:
            self.music.stop()
            self._vb_retry = True                   # relaunch -> _launch_match plays VB theme

    # ---- story interludes --------------------------------------------------
    def _game_over(self, lines):
        self.active = GameOverMode(self, lines)

    def retry_beat(self):
        self.resume()
        self.story.replay_beat()

    def _week_end(self):
        self.active = ResultsMode(self, screens.Results(
            self.story.stars(), max(1, self.story.vb_attempts)))
        self.music.play(CHAPTER_END_MUSIC)         # end-of-chapter screen theme

    def enter_phone(self):
        self.active = PhoneMode(self, screens.Phone(PHONE_THREAD))

    def finish_week(self):
        self.resume()
        self.story.set_flag('w1_left')
        self.update_scene_music(self.scene_manager.current_id)   # end chapter-end theme

    def run(self):
        while self.running:
            dt = self.clock.tick(60) / 1000.0
            self.handle_events()
            self.update(dt)
            self.draw()

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()
