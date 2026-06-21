"""Main game — loop, top-level wiring, and the transitions between modes."""
import pygame
import sys
from config import (DEV, SCREEN_WIDTH, SCREEN_HEIGHT, VB_MUSIC, KING_ST_MUSIC,
                    GYM_MUSIC, SALUTATION_MUSIC, GARDEN_MUSIC, LATIMER_MUSIC,
                    WETHERSPOONS_MUSIC, DIVE_MUSIC, GAME_OVER_MUSIC,
                    CHARACTER_MUSIC, CHAPTER_END_MUSIC, INTERLUDE_MUSIC,
                    PHONE_THREAD_W1, PHONE_THREAD_W2, PHONE_THREAD_W3, PHONE_THREAD_W4)
from entities import Player
from scenes import (Gym, KingSt, Salutation, Garden, Corridor, Reception,
                    Courtyard, Passage, Courts, WilliamMorris, VolleyCourt,
                    DiveGame)
from systems.scene_manager import SceneManager
from systems import input_handler
from systems.input_handler import event_to_action
from systems.audio import MusicPlayer, SoundBank
from systems.dialogue import DialogueBox
from systems.story import StoryManager
from systems import save, screens
from systems.party import Party
from systems.cutscene import Cutscene
from systems.lighting import Lighting
from systems.modes import (TitleMode, PlayMode, GameOverMode, ResultsMode,
                           PhoneMode, InterludeMode, ChapterCardMode, GameEndMode)
from systems.menu_flow import MenuFlow


_SCENE_NAMES = {1: "Gym", 2: "King Street", 3: "The Salutation", 4: "Beer Garden",
                5: "Corridor", 6: "Reception", 7: "Courtyard",
                8: "Passage", 9: "Netball Courts", 10: "Wetherspoons",
                11: "Volleyball", 12: "Diving"}


class Game:
    def __init__(self):
        pygame.init()
        input_handler.init_joysticks()           # open any controller already plugged in
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN | pygame.SCALED)
        pygame.display.set_caption("The Story of Us")
        self.clock = pygame.time.Clock()
        self.running = True
        self.music = MusicPlayer()
        self.sfx = SoundBank()                   # shared UI/overworld SFX (dialogue blip, etc.)
        self._scene_music = {                      # scene_id -> looping track (else silence)
            1: GYM_MUSIC, 2: KING_ST_MUSIC,
            3: SALUTATION_MUSIC, 4: GARDEN_MUSIC,
            5: LATIMER_MUSIC, 6: LATIMER_MUSIC, 7: LATIMER_MUSIC,   # school grounds, not the gym
            8: LATIMER_MUSIC, 9: LATIMER_MUSIC,
            10: WETHERSPOONS_MUSIC,
        }
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
        self.dive = DiveGame()

        self._start_col = 9            # top row, just inside the double doors (cols 8-11);
        self._start_row = 1            # Nat spawns beside her at (8, 1)
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
        self.scene_manager.register(12, self.dive)
        self.scene_manager.start(1, self.player)

        self.party = Party()
        king_st.set_party(self.party)      # crossing lights hold green while the crew cross
        self.story = StoryManager()
        self.cutscene = Cutscene()
        self.story.bind(self.dialogue, self.scene_manager, self.player,
                        self.party, self.cutscene)
        self.cutscene.bind(self.dialogue, self.scene_manager, self.player,
                           self.party, self.story)
        self.cutscene.on_game_over = self._game_over
        self.story.on_launch_vb = self._launch_match
        self.story.on_launch_dive = self._launch_dive
        self.story.on_week_end = self._week_end
        self.story.on_phone = self.enter_interlude
        self.story.on_chapter_start = self._chapter_start
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
            if event.type == pygame.JOYDEVICEADDED:        # controller plugged in mid-game
                input_handler.add_joystick(event.device_index)
                continue
            if event.type == pygame.JOYDEVICEREMOVED:
                input_handler.remove_joystick(event.instance_id)
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
        self.music.reset()                 # fresh game -> no stale song resume marks
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
        if data.get('completed'):                # a finished file -> offer a fresh start
            self.active = GameEndMode(self, loaded=True)
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

    def save_to_slot(self, slot, completed=False):
        data = {
            'scene_id': self.scene_manager.current_id,
            'scene_name': _SCENE_NAMES.get(self.scene_manager.current_id, '?'),
            'tile_x': self.player.tile_x,
            'tile_y': self.player.tile_y,
            'facing': self.player.facing,
            'beat_name': self.story.beat['name'],
        }
        data.update(self.story.snapshot())
        if completed:
            data['completed'] = True
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
        """While a character with a theme is talking, play it (resuming where it
        last left off — see MusicPlayer); restore the scene's track once they stop.
        Called each play frame from PlayMode."""
        speaker = self.dialogue.speaker if self.dialogue.active else None
        theme = CHARACTER_MUSIC.get(speaker) if speaker else None
        if theme is not None:
            if speaker != self._speaker_music:
                self.music.play(theme)
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
        """Story hook: drop into the 3v3. Difficulty + roster are set per chapter
        (Ch1 easy, Ch2 medium); Ch1 can run the controls warm-up first if asked."""
        week = self.story.beat.get('week', 1)
        level = {1: 'easy', 2: 'medium', 3: 'hard', 4: 'insane'}.get(week, 'hard')
        if week == 1 and self.story.has('w1_want_tut') and not self.story.has('w1_tut_done'):
            self._launch_tutorial(level)
            return
        self.court.configure('match', level, week)
        self.court.on_finish = self._end_volleyball
        self.music.play(VB_MUSIC)
        self.scene_manager.jump_to(11, self.player)

    def _launch_tutorial(self, level):
        """The warm-up: the 5-step controls tutorial, then straight into the match.
        No vball theme here — that's reserved for the real match; the gym theme
        carries over from the overworld."""
        self.court.configure('tutorial', level, 1)
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
            self.story.set_flag(self.story.beat.get('advance_when'))   # this chapter's win flag
        else:
            self.music.stop()
            self._vb_retry = True                   # relaunch -> _launch_match plays VB theme

    # ---- diving minigame ---------------------------------------------------
    def _launch_dive(self):
        """Story hook: drop into the Ch3 diving drill."""
        self.dive.on_finish = self._end_dive
        self.music.play(DIVE_MUSIC)
        self.scene_manager.jump_to(12, self.player)

    def _end_dive(self):
        self.scene_manager.jump_to(1, self.player)        # back to the gym
        self.play.mark_scene_synced()
        self.update_scene_music(1)
        self.story.set_flag(self.story.beat.get('advance_when'))

    # ---- story interludes --------------------------------------------------
    def _game_over(self, lines):
        self.music.play(GAME_OVER_MUSIC, loop=False)    # plays once, then silence
        self.active = GameOverMode(self, lines)

    def retry_beat(self):
        self.resume()
        self.update_scene_music(self.scene_manager.current_id)   # back to the scene's track
        self.story.replay_beat()

    def debug_cycle(self):
        """Dev only: bail out of whatever's on screen and hop to the next activity."""
        if not DEV:                              # disabled in the shipped build
            return
        self.cutscene.active = False
        self.dialogue.active = False
        self.resume()                            # back to PlayMode before the jump
        self.story.debug_cycle()

    def _week_end(self):
        title = "{0} Complete".format(self.story.week_title or "Week")
        self.active = ResultsMode(self, screens.Results(
            self.story.stars(), max(1, self.story.vb_attempts), title))
        self.music.play(CHAPTER_END_MUSIC)         # end-of-chapter screen theme

    def enter_phone(self):
        threads = {1: PHONE_THREAD_W1, 2: PHONE_THREAD_W2, 3: PHONE_THREAD_W3,
                   4: PHONE_THREAD_W4}
        thread = threads.get(self.story.beat.get('week'), PHONE_THREAD_W1)
        self.active = PhoneMode(self, screens.Phone(thread))

    def finish_week(self):
        self.resume()
        self.music.reset()                          # new chapter -> songs start fresh, not resumed
        self.story.vb_attempts = 0                  # star cards are per-chapter; reset for the next
        self.story.set_flag(self.story.beat.get('advance_when'))   # this chapter's "left" flag
        self.update_scene_music(self.scene_manager.current_id)   # end chapter-end theme

    def _chapter_start(self, week, title, first):
        """A new chapter's first beat was entered (after its goto). Reset the crew
        (last chapter's followers don't carry over — they're back as gym NPCs),
        autosave the fresh chapter, and for Chapter 2+ show a transition card first
        — the chapter's opening cutscene is already queued and plays after it."""
        self.party.clear()
        gym = self.scene_manager.scene(1)
        if gym is not None:
            gym.repopulate()
            gym.remove_named(self.story.beat.get('absent', ()))   # e.g. Nat stays home in Ch4
        self.save_to_slot(save.AUTOSAVE)
        if not first:
            self.active = ChapterCardMode(self, week - 1, week, self.resume)

    def enter_interlude(self, thread, other, flag, title='Interlude', date=''):
        """A between-chapters texts-only beat (e.g. the Scrims interlude): a title
        card announces it, then the text thread plays."""
        kicker, _, name = title.partition('—')
        kicker, name = kicker.strip() or 'Interlude', name.strip()
        self.music.play(CHAPTER_END_MUSIC if kicker == 'Finale' else INTERLUDE_MUSIC)

        def start_phone():
            phone = screens.Phone(thread, other=other)
            self.active = PhoneMode(self, phone,
                                    on_done=lambda: self._finish_interlude(flag))
        self.active = InterludeMode(self, kicker, name or kicker, date, start_phone)

    def _finish_interlude(self, flag):
        if self.story.beat.get('end_game'):         # the finale -> closing card, not the overworld
            self.story.set_flag(flag)
            self._game_complete()
            return
        self.resume()
        self.music.reset()                          # interludes sit between chapters -> reset marks
        self.story.set_flag(flag)
        self.update_scene_music(self.scene_manager.current_id)

    def _game_complete(self):
        """Roll the closing card and stamp the autosave as completed, so loading the
        'continue' file afterwards offers a fresh start from the beginning."""
        self.save_to_slot(save.AUTOSAVE, completed=True)
        self.music.play(CHAPTER_END_MUSIC)
        self.active = GameEndMode(self)

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
