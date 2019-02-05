import argparse
import curses
import os
import sys
import time

from dragoncurses.component import (
    Component,
    LabelComponent,
    BorderComponent,
    DialogBoxComponent,
    StickyComponent,
)
from dragoncurses.context import RenderContext, BoundingRectangle
from dragoncurses.scene import Scene
from dragoncurses.loop import MainLoop, loop_config
from dragoncurses.input import InputEvent, KeyboardInputEvent, Keys
from dragoncurses.settings import Settings
from profile import Profile, ProfileCollection


Settings.enable_unicode = True


class ProfileListComponent(Component):

    PANEL_SIZE = 35

    def __init__(self, profiles: ProfileCollection) -> None:
        super().__init__()
        self.profiles = profiles
        self.cursor = 0 if self._valid_profiles() > 0 else -1
        self.window = 0
        self.changed = False

    def _valid_profiles(self) -> int:
        cnt = 0
        for profile in self.profiles:
            if profile.valid:
                cnt += 1
        return cnt

    def _current_profile(self) -> Profile:
        return self._profile_at(self.cursor)

    def _profile_at(self, pos: int) -> Profile:
        cnt = 0
        for profile in self.profiles:
            if profile.valid:
                if cnt == pos:
                    return profile
                cnt += 1
        raise Exception(
            "Logic error, somehow let the cursor get out of bounds!"
        )

    def render(self, context: RenderContext) -> None:
        if (
            context.bounds.width > self.PANEL_SIZE and
            self._valid_profiles() > 0
        ):
            # Make room for right panel
            with context.clip(
                BoundingRectangle(
                    top=0,
                    left=0,
                    bottom=context.bounds.bottom,
                    right=context.bounds.right - self.PANEL_SIZE,
                )
            ) as listcontext:
                self._render_list(listcontext)

            # Draw the divider
            for y in range(context.bounds.height):
                context.draw_string(
                    y,
                    context.bounds.right - self.PANEL_SIZE,
                    "\u2502" if Settings.enable_unicode else "|",
                    wrap=False,
                )

            # Draw the right side panel
            with context.clip(
                BoundingRectangle(
                    top=0,
                    left=context.bounds.right - (self.PANEL_SIZE - 1),
                    bottom=context.bounds.bottom,
                    right=context.bounds.right,
                )
            ) as panelcontext:
                self._render_panel(panelcontext)

        else:
            # No room for right panel
            self._render_list(context)
        self.changed = False

    def _render_list(self, context: RenderContext) -> None:
        # TODO: Handle window positioning here

        top = self.window
        bottom = min(
            self.window + context.bounds.height,
            self._valid_profiles(),
        )
        for i in range(top, bottom):
            profile = self._profile_at(i)
            display = " " + profile.name + " (" + profile.callsign + ")"
            if len(display) < context.bounds.width:
                display = display + " " * (context.bounds.width - len(display))

            context.draw_string(i - top, 0, display, invert=(i == self.cursor))

    def _render_panel(self, context: RenderContext) -> None:
        profile = self._current_profile()
        with context.clip(
            BoundingRectangle(
                top=0,
                left=1,
                bottom=context.bounds.bottom,
                right=context.bounds.right - 1,
            )
        ) as bufferedcontext:
            bufferedcontext.draw_string(0, 0, str(profile), wrap=True)

    @property
    def dirty(self) -> bool:
        return self.changed

    def handle_input(self, event: InputEvent) -> bool:
        if isinstance(event, KeyboardInputEvent):
            if event.character == Keys.UP:
                if self.cursor > 0:
                    self.cursor -= 1
                    self.changed = True
                return True
            if event.character == Keys.DOWN:
                if self.cursor < (self._valid_profiles() - 1):
                    self.cursor += 1
                    self.changed = True
                return True
            if event.character == "d":
                if self.cursor > -1:
                    self._current_profile().clear()
                    if self._valid_profiles() == 0:
                        self.cursor = -1
                    elif self.cursor > 0:
                        self.cursor -= 1
                    self.changed = True
                return True
        return False


class ListProfilesScene(Scene):

    def create(self) -> Component:
        return StickyComponent(
            LabelComponent(
                "<invert> up/down - select profile </invert> " +
                "<invert> enter - edit selected profile </invert> " +
                "<invert> a - add new profile </invert> " +
                "<invert> d - delete selected profile </invert> " +
                "<invert> esc/q - quit </invert>",
                formatted=True,
            ),
            BorderComponent(
                ProfileListComponent(self.settings['profiles']),
                style=BorderComponent.SINGLE,
            ),
            location=StickyComponent.LOCATION_BOTTOM,
            size=1,
        )

    def save_profiles(self) -> None:
        with open(self.settings['file'], 'wb') as fp:
            fp.write(self.settings['profiles'].data)
        self.main_loop.exit()

    def handle_input(self, event: InputEvent) -> bool:
        if isinstance(event, KeyboardInputEvent):
            if event.character in [Keys.ESCAPE, 'q']:
                self.register_component(
                    DialogBoxComponent(
                        'Write back changes to SRAM file?',
                        [
                            (
                                '&Yes',
                                lambda c, o: self.save_profiles(),
                            ),
                            (
                                '&No',
                                lambda c, o: self.main_loop.exit(),
                            ),
                            (
                                '&Cancel',
                                lambda c, o: self.unregister_component(c),
                            ),
                        ],
                    )
                )

                return True
        return False


def idle(mainloop: MainLoop) -> None:
    # My curses library turns out to spin-loop and I am not in the mood to
    # fix it ATM.
    time.sleep(0.005)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="A text-based profile editor for The Grid."
    )
    parser.add_argument(
        "file",
        metavar="FILE",
        type=str,
        help="SRAM file to edit.",
    )
    parser.add_argument(
        "--mame-compat",
        action="store_true",
        help="SRAM file is from MAME instead of a dump.",
    )
    args = parser.parse_args()

    # Load the SRAM file
    with open(args.file, "rb") as fp:
        profiles = ProfileCollection(
            fp.read(),
            is_mame_format=args.mame_compat,
        )

    def wrapped(context) -> None:
        # Run the main program loop
        with loop_config(context):
            loop = MainLoop(
                context,
                {'file': args.file, 'profiles': profiles},
                idle,
            )
            loop.change_scene(ListProfilesScene)
            loop.run()

    os.environ.setdefault('ESCDELAY', '0')
    curses.wrapper(wrapped)

    return 0


if __name__ == "__main__":
    sys.exit(main())
