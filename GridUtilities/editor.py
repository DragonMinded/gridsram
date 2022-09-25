#! /usr/bin/env python3
import argparse
import curses
import os
import sys
import time
from typing import Any, Callable, Dict, List, Optional, TypeVar, Union, cast

from dragoncurses.component import (
    Component,
    DeferredInput,
    LabelComponent,
    BorderComponent,
    DialogBoxComponent,
    StickyComponent,
    TextInputComponent,
    PaddingComponent,
    ListComponent,
    ClickableComponent,
    SelectInputComponent,
    PopoverMenuComponent,
    TabComponent,
)
from dragoncurses.context import RenderContext, BoundingRectangle, Color
from dragoncurses.scene import Scene
from dragoncurses.loop import MainLoop, loop_config
from dragoncurses.input import (
    InputEvent,
    KeyboardInputEvent,
    MouseInputEvent,
    ScrollInputEvent,
    Buttons,
    Directions,
    Keys,
)
from dragoncurses.settings import Settings
from profile import Profile, ProfileCollection, TowerCollection, SRAM


CursesContext = Any


Settings.enable_unicode = True


class ClickableTextInputComponent(ClickableComponent, TextInputComponent):
    def __repr__(self) -> str:
        return "ClickableTextInputComponent(text={}, focused={})".format(
            repr(self.text),
            "True" if self.focus else "False",
        )


class ClickableSelectInputComponent(ClickableComponent, SelectInputComponent):
    def __repr__(self) -> str:
        return (
            "ClickableSelectInputComponent(selected={}, options={}, focused={})".format(
                repr(self.selected),
                repr(self.options),
                "True" if self.focus else "False",
            )
        )


ClickableLabelComponentT = TypeVar(
    "ClickableLabelComponentT", bound="ClickableLabelComponent"
)


class ClickableLabelComponent(LabelComponent):

    callback: Optional[Callable[[Component, MouseInputEvent], bool]] = None

    def on_click(
        self: ClickableLabelComponentT,
        callback: Callable[[Component, MouseInputEvent], bool],
    ) -> ClickableLabelComponentT:
        self.callback = callback
        return self

    def handle_input(self, event: "InputEvent") -> Union[bool, DeferredInput]:
        # Overrides handle_input instead of _handle_input because this is
        # meant to be used as either a mixin. This handles input entirely,
        # instead of intercepting it, so thus overriding the public function.
        if isinstance(event, MouseInputEvent):
            if self.callback is not None:
                handled = self.callback(self, event)
                # Fall through to default if the callback didn't handle.
                if bool(handled):
                    return handled
            else:
                # We still handled this regardless of notification
                return True

        return super().handle_input(event)


class EditProfileComponent(Component):

    NAME = 0
    PIN = 1
    CALLSIGN = 2
    TOTALWINS = 3
    TOTALPLAYS = 4
    TOTALPOINTS = 5
    STREAK = 6
    HIGHSCORE = 7
    TOTALCASH = 8
    TOWERPOSITION = 9
    TOWERCLEARS = 10
    CONTROLMODE = 11

    def __init__(self, profile: Profile, *, padding: int = 5) -> None:
        super().__init__()
        self.profile = profile
        self.__padding = padding
        self.__save_callback: Optional[Callable[[], None]] = None
        self.__cancel_callback: Optional[Callable[[], None]] = None

        def get_control_mode() -> str:
            if profile.freelook:
                if profile.invertaim:
                    return "free + inverted"
                else:
                    return "free look"
            else:
                return "assist"

        # Set up inputs
        self.__inputs: List[
            Union[ClickableTextInputComponent, ClickableSelectInputComponent]
        ] = [
            ClickableTextInputComponent(
                profile.name,
                max_length=7,
                allowed_characters="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 ",
                focused=True,
            ).on_click(self.__click_select),
            ClickableTextInputComponent(
                profile.pin,
                max_length=10,
                allowed_characters="0123456789",
                focused=False,
            ).on_click(self.__click_select),
            ClickableSelectInputComponent(
                profile.callsign or "No Call Sign",
                ["No Call Sign"] + sorted(profile.callsigns),
                focused=False,
            ).on_click(self.__click_select),
            ClickableTextInputComponent(
                str(profile.totalwins),
                max_length=5,
                allowed_characters="0123456789",
                focused=False,
            ).on_click(self.__click_select),
            ClickableTextInputComponent(
                str(profile.totalplays),
                max_length=5,
                allowed_characters="0123456789",
                focused=False,
            ).on_click(self.__click_select),
            ClickableTextInputComponent(
                str(profile.totalpoints),
                max_length=10,
                allowed_characters="0123456789",
                focused=False,
            ).on_click(self.__click_select),
            ClickableTextInputComponent(
                str(profile.streak),
                max_length=3,
                allowed_characters="0123456789",
                focused=False,
            ).on_click(self.__click_select),
            ClickableTextInputComponent(
                str(profile.highscore),
                max_length=3,
                allowed_characters="0123456789",
                focused=False,
            ).on_click(self.__click_select),
            ClickableTextInputComponent(
                str(profile.totalcash),
                max_length=10,
                allowed_characters="0123456789",
                focused=False,
            ).on_click(self.__click_select),
            ClickableTextInputComponent(
                str(profile.towerposition[0]) + ", " + str(profile.towerposition[1]),
                max_length=6,
                allowed_characters="0123456789, ",
                focused=False,
            ).on_click(self.__click_select),
            ClickableTextInputComponent(
                str(profile.towerclears),
                max_length=3,
                allowed_characters="0123456789",
                focused=False,
            ).on_click(self.__click_select),
            ClickableSelectInputComponent(
                get_control_mode(),
                ["assist", "free look", "free + inverted"],
                focused=False,
            ).on_click(self.__click_select),
        ]
        self.__errors = [LabelComponent("", textcolor=Color.RED) for _ in self.__inputs]
        self.__validators = [
            self.__validate_name,
            self.__validate_pin,
            self.__validate_callsign,
            self.__validate_totalwins,
            self.__validate_totalplays,
            self.__validate_totalpoints,
            self.__validate_streak,
            self.__validate_highscore,
            self.__validate_totalcash,
            self.__validate_towerposition,
            self.__validate_towerclears,
            self.__validate_controlmode,
        ]
        # Run initial validation (we might have a new/blank profile)
        self.__validate()

        self.__component = PaddingComponent(
            BorderComponent(
                PaddingComponent(
                    StickyComponent(
                        ClickableLabelComponent(
                            "<invert> up/down - select input </invert> "
                            + "<invert> enter - save changes and close </invert> "
                            + "<invert> esc - discard changes and close </invert>",
                            formatted=True,
                        ).on_click(self.__handle_label_click),
                        StickyComponent(
                            ListComponent(
                                [
                                    LabelComponent("Name"),
                                    LabelComponent("PIN"),
                                    LabelComponent("Call Sign"),
                                    LabelComponent("Games Won"),
                                    LabelComponent("Games Played"),
                                    LabelComponent("Total Points"),
                                    LabelComponent("Longest Streak"),
                                    LabelComponent("High Score"),
                                    LabelComponent("Total Cash"),
                                    LabelComponent("Tower Progress"),
                                    LabelComponent("Tower Clears"),
                                    LabelComponent("Control Mode"),
                                ],
                                direction=ListComponent.DIRECTION_TOP_TO_BOTTOM,
                                size=2,
                            ),
                            StickyComponent(
                                ListComponent(
                                    self.__inputs,
                                    direction=ListComponent.DIRECTION_TOP_TO_BOTTOM,
                                    size=2,
                                ),
                                ListComponent(
                                    self.__errors,
                                    direction=ListComponent.DIRECTION_TOP_TO_BOTTOM,
                                    size=2,
                                ),
                                location=StickyComponent.LOCATION_LEFT,
                                size=20,
                            ),
                            location=StickyComponent.LOCATION_LEFT,
                            size=20,
                        ),
                        location=StickyComponent.LOCATION_BOTTOM,
                        size=1,
                    ),
                    horizontalpadding=1,
                ),
                style=(
                    BorderComponent.DOUBLE
                    if Settings.enable_unicode
                    else BorderComponent.SOLID
                ),
            ),
            padding=self.__padding,
        )

    def on_save(self, callback: Optional[Callable[[], None]]) -> "EditProfileComponent":
        self.__save_callback = callback
        return self

    def on_cancel(
        self, callback: Optional[Callable[[], None]]
    ) -> "EditProfileComponent":
        self.__cancel_callback = callback
        return self

    @property
    def dirty(self) -> bool:
        return self.__component.dirty

    def attach(self, scene: "Scene", settings: Dict[str, Any]) -> None:
        self.__component._attach(scene, settings)

    def detach(self) -> None:
        self.__component._detach()

    def tick(self) -> None:
        self.__component.tick()

    def render(self, context: RenderContext) -> None:
        self.__component._render(context, context.bounds)

    def __validate(self) -> bool:
        valid = True

        for i, validator in enumerate(self.__validators):
            error = validator()
            if error:
                valid = False
                # We could pad during control setup but I'm lazy
                self.__errors[i].text = " " + error
            else:
                self.__errors[i].text = ""
        return valid

    def __validate_name(self) -> Optional[str]:
        name = cast(ClickableTextInputComponent, self.__inputs[self.NAME]).text
        if len(name) < 1:
            return "Must be at least one character!"
        if len(name) > 7:
            return "Must be at most seven characters!"
        return None

    def __validate_pin(self) -> Optional[str]:
        pin = cast(ClickableTextInputComponent, self.__inputs[self.PIN]).text
        if len(pin) < 5:
            return "Must be at least five digits!"
        if len(pin) > 10:
            return "Must be at most ten digits!"
        return None

    def __validate_callsign(self) -> Optional[str]:
        # Its a select box so its always valid
        return None

    def __validate_totalwins(self) -> Optional[str]:
        wins = cast(ClickableTextInputComponent, self.__inputs[self.TOTALWINS]).text
        plays = cast(ClickableTextInputComponent, self.__inputs[self.TOTALPLAYS]).text
        if len(plays) == 0:
            plays = "0"

        if len(wins) < 1:
            return "Must be at least one digit!"
        if int(wins) > 0xFFFF:
            return "Must be at most 65535!"
        if int(wins) > int(plays):
            return "Must be less than or equal to plays!"
        return None

    def __validate_totalplays(self) -> Optional[str]:
        plays = cast(ClickableTextInputComponent, self.__inputs[self.TOTALPLAYS]).text

        if len(plays) < 1:
            return "Must be at least one digit!"
        if int(plays) > 0xFFFF:
            return "Must be at most 65535!"
        return None

    def __validate_totalpoints(self) -> Optional[str]:
        points = cast(ClickableTextInputComponent, self.__inputs[self.TOTALPOINTS]).text

        if len(points) < 1:
            return "Must be at least one digit!"
        if int(points) > 0xFFFFFFFF:
            return "Try to be a bit less greedy!"
        return None

    def __validate_streak(self) -> Optional[str]:
        streak = cast(ClickableTextInputComponent, self.__inputs[self.STREAK]).text

        if len(streak) < 1:
            return "Must be at least one digit!"
        if int(streak) > 0xFF:
            return "Must be at most 255!"
        return None

    def __validate_highscore(self) -> Optional[str]:
        highscore = cast(
            ClickableTextInputComponent, self.__inputs[self.HIGHSCORE]
        ).text

        if len(highscore) < 1:
            return "Must be at least one digit!"
        if int(highscore) > 0xFF:
            return "Must be at most 255!"
        return None

    def __validate_totalcash(self) -> Optional[str]:
        cash = cast(ClickableTextInputComponent, self.__inputs[self.TOTALCASH]).text

        if len(cash) < 1:
            return "Must be at least one digit!"
        if int(cash) > 0xFFFFFFFF:
            return "Try to be a bit less greedy!"
        if (int(cash) % 200) != 0:
            return "Must be in increments of $200!"
        return None

    def __validate_towerposition(self) -> Optional[str]:
        towerposition = cast(
            ClickableTextInputComponent, self.__inputs[self.TOWERPOSITION]
        ).text

        if len(towerposition.split(",")) != 2:
            return "Must be in the form <tower>, <level>!"
        tower, level = towerposition.split(",")
        tower = tower.strip()
        level = level.strip()
        if len(tower) == 0 or int(tower) < 1 or int(tower) > 10:
            return "Tower must be between 1-10!"
        if len(level) == 0 or int(level) < 1 or int(level) > 6:
            return "Level must be between 1-6!"
        return None

    def __validate_towerclears(self) -> Optional[str]:
        towerclears = cast(
            ClickableTextInputComponent, self.__inputs[self.TOWERCLEARS]
        ).text

        if len(towerclears) < 1:
            return "Must be at least one digit!"
        if int(towerclears) > 0xFF:
            return "Must be at most 255!"
        return None

    def __validate_controlmode(self) -> Optional[str]:
        # Can't be invalid, its a select
        return None

    def __click_select(self, component: Component, button: Buttons) -> bool:
        if button == Buttons.LEFT:
            for inp in self.__inputs:
                inp.focus = inp is component
        # Allow this input to continue propagating, so we can focus on and also click
        # the select option dialog.
        return False

    def __handle_label_click(
        self, component: Component, event: MouseInputEvent
    ) -> bool:
        # This is hacky, we really should define a component and just handle click
        # events without checking position. However, I don't want to work on a
        # list component that sizes each entry to the entry's width/height so instead
        # I just check the mouse position.
        if event.button == Buttons.LEFT:
            location = component.location
            if location is not None:
                click_x = event.x - location.left
                click_y = event.y - location.top

                if click_y == 0:
                    if click_x >= 25 and click_x <= 56:
                        if self.__validate():
                            self.__save_and_close()
                        return True

                    if click_x >= 58 and click_x <= 90:
                        if self.__cancel_callback:
                            self.__cancel_callback()
                        self.scene.unregister_component(self)
                        return True

        return False

    def __save_and_close(self) -> None:
        self.profile.name = cast(
            ClickableTextInputComponent, self.__inputs[self.NAME]
        ).text
        self.profile.pin = cast(
            ClickableTextInputComponent, self.__inputs[self.PIN]
        ).text
        callsign = cast(
            ClickableSelectInputComponent, self.__inputs[self.CALLSIGN]
        ).selected
        self.profile.callsign = None if callsign == "No Call Sign" else callsign
        self.profile.totalwins = int(
            cast(ClickableTextInputComponent, self.__inputs[self.TOTALWINS]).text,
        )
        self.profile.totalplays = int(
            cast(ClickableTextInputComponent, self.__inputs[self.TOTALPLAYS]).text,
        )
        self.profile.totalpoints = int(
            cast(ClickableTextInputComponent, self.__inputs[self.TOTALPOINTS]).text,
        )
        self.profile.streak = int(
            cast(ClickableTextInputComponent, self.__inputs[self.STREAK]).text,
        )
        self.profile.highscore = int(
            cast(ClickableTextInputComponent, self.__inputs[self.HIGHSCORE]).text,
        )
        self.profile.totalcash = int(
            cast(ClickableTextInputComponent, self.__inputs[self.TOTALCASH]).text
        )
        tower, level = cast(
            ClickableTextInputComponent, self.__inputs[self.TOWERPOSITION]
        ).text.split(",")
        self.profile.towerposition = (
            int(tower.strip()),
            int(level.strip()),
        )
        self.profile.towerclears = int(
            cast(ClickableTextInputComponent, self.__inputs[self.TOWERCLEARS]).text
        )
        if (
            cast(
                ClickableSelectInputComponent,
                self.__inputs[self.CONTROLMODE],
            ).selected
            == "assist"
        ):
            self.profile.freelook = False
            self.profile.invertaim = False
        elif (
            cast(
                ClickableSelectInputComponent,
                self.__inputs[self.CONTROLMODE],
            ).selected
            == "free look"
        ):
            self.profile.freelook = True
            self.profile.invertaim = False
        elif (
            cast(
                ClickableSelectInputComponent,
                self.__inputs[self.CONTROLMODE],
            ).selected
            == "free + inverted"
        ):
            self.profile.freelook = True
            self.profile.invertaim = True
        else:
            raise Exception("Logic error, unrecognized option!")
        if not self.profile.valid:
            raise Exception("Logic error, profile must be valid on save!")
        if self.__save_callback:
            self.__save_callback()
        self.scene.unregister_component(self)

    def handle_input(self, event: "InputEvent") -> bool:
        if isinstance(event, KeyboardInputEvent):
            # Handle return/esc keys to save/cancel input
            if event.character == Keys.ENTER:
                if self.__validate():
                    self.__save_and_close()
                return True
            if event.character == Keys.ESCAPE:
                if self.__cancel_callback:
                    self.__cancel_callback()
                self.scene.unregister_component(self)
                return True
            if event.character == Keys.UP:
                for i, component in enumerate(self.__inputs):
                    if i != 0 and component.focus:
                        component.focus = False
                        self.__inputs[i - 1].focus = True
                        break
                return True
            if event.character == Keys.DOWN:
                for i, component in enumerate(self.__inputs):
                    if i != (len(self.__inputs) - 1) and component.focus:
                        component.focus = False
                        self.__inputs[i + 1].focus = True
                        break
                return True

        # Pass input onward to sub-components
        self.__component._handle_input(event)

        # Validate now that subcomponents might have changed
        self.__validate()

        # Swallow events, since we don't want this to be closeable or to
        # allow clicks behind it.
        return True

    def __repr__(self) -> str:
        return "EditProfileComponent({})".format(
            ", ".join(str(i) for i in self.__inputs)
        )


class ProfileListComponent(Component):

    PANEL_SIZE = 35

    def __init__(self, profiles: ProfileCollection) -> None:
        super().__init__()
        self.profiles = profiles
        self.__invalidate_cache()
        self.cursor = 0 if self._valid_profiles() > 0 else -1
        self.window = 0
        self.changed = False
        self.__last_click = (-1, -1, -1.0)

    def __invalidate_cache(self) -> None:
        self.__count: Optional[int] = None
        self.__profcache: Dict[int, int] = {}
        self.changed = True

    def __invalidate_and_recount(self) -> None:
        self.__invalidate_cache()
        if self._valid_profiles() > 0 and self.cursor == -1:
            self.cursor = 0

    def _valid_profiles(self) -> int:
        if self.__count is not None:
            return self.__count

        cnt = 0
        for profile in self.profiles:
            if profile.valid:
                cnt += 1
        self.__count = cnt
        return cnt

    def _new_profile(self) -> Profile:
        for profile in self.profiles:
            if not profile.valid:
                return profile
        raise Exception("Could not find a spot to add a new profile!")

    def _current_profile(self) -> Profile:
        return self._profile_at(self.cursor)

    def _profile_at(self, pos: int) -> Profile:
        if pos in self.__profcache:
            return self.profiles[self.__profcache[pos]]

        cnt = 0
        for i, profile in enumerate(self.profiles):
            if profile.valid:
                if cnt == pos:
                    self.__profcache[pos] = i
                    return profile
                cnt += 1
        raise Exception("Logic error, somehow let the cursor get out of bounds!")

    def render(self, context: RenderContext) -> None:
        if context.bounds.width > self.PANEL_SIZE and self._valid_profiles() > 0:
            # Make room for right panel
            with context.clip(
                BoundingRectangle(
                    top=0,
                    left=0,
                    bottom=context.bounds.bottom - 1,
                    right=context.bounds.right - self.PANEL_SIZE,
                )
            ) as listcontext:
                self._render_list(listcontext)

            # Draw the divider
            for y in range(context.bounds.height - 1):
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
                    bottom=context.bounds.bottom - 1,
                    right=context.bounds.right,
                )
            ) as panelcontext:
                self._render_panel(panelcontext)

        else:
            # No room for right panel
            self._render_list(context)

        # Draw the horizontal label divider
        for x in range(context.bounds.width):
            context.draw_string(
                context.bounds.height - 1,
                x,
                "\u2500" if Settings.enable_unicode else "-",
                wrap=False,
            )

        self.changed = False

    def _render_list(self, context: RenderContext) -> None:
        # No artifacts, please!
        context.clear()

        # Handle scrolling up with some buffer.
        if (self.cursor - 4) < self.window:
            self.window = self.cursor - 4
            if self.window < 0:
                self.window = 0
        # Handle scrolling down with some buffer.
        if (self.cursor + 5) > (self.window + context.bounds.height):
            self.window = (self.cursor + 5) - context.bounds.height
            if self.window > (self._valid_profiles() - context.bounds.height):
                self.window = self._valid_profiles() - context.bounds.height

        top = self.window
        bottom = min(
            self.window + context.bounds.height,
            self._valid_profiles(),
        )
        for i in range(top, bottom):
            profile = self._profile_at(i)
            display = (
                " " + profile.name + " (" + (profile.callsign or "No Call Sign") + ")"
            )
            if len(display) < context.bounds.width:
                display = display + " " * (context.bounds.width - len(display))

            context.draw_string(i - top, 0, display, invert=(i == self.cursor))

    def _render_panel(self, context: RenderContext) -> None:
        # No artifacts, please!
        context.clear()

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

    def __edit_current_profile(self) -> None:
        if self.cursor > -1:
            self.scene.register_component(
                EditProfileComponent(self._current_profile()).on_save(
                    self.__invalidate_cache
                )
            )

    def __add_new_profile(self) -> None:
        self.scene.register_component(
            EditProfileComponent(self._new_profile()).on_save(
                self.__invalidate_and_recount
            )
        )

    def __delete_current_profile(self) -> None:
        if self.cursor > -1:
            self._current_profile().clear()
            if self._valid_profiles() == 0:
                self.cursor = -1
            elif self.cursor > 0:
                self.cursor -= 1
            self.__invalidate_cache()
            self.changed = True

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
            if event.character in ["d", Keys.DELETE]:
                self.__delete_current_profile()
                return True
            if event.character == Keys.ENTER:
                self.__edit_current_profile()
                return True
            if event.character == "a":
                self.__add_new_profile()
                return True
            if event.character == Keys.HOME:
                if self._valid_profiles() > 0:
                    self.cursor = 0
                    self.changed = True
                return True
            if event.character == Keys.END:
                if self._valid_profiles() > 0:
                    self.cursor = self._valid_profiles() - 1
                    self.changed = True
                return True
            if event.character == Keys.PGDN:
                if self._valid_profiles() > 0:
                    self.cursor += (
                        self.location.height if self.location is not None else 1
                    )
                    if self.cursor >= self._valid_profiles():
                        self.cursor = self._valid_profiles() - 1
                    self.changed = True
                return True
            if event.character == Keys.PGUP:
                if self._valid_profiles() > 0:
                    self.cursor -= (
                        self.location.height if self.location is not None else 1
                    )
                    if self.cursor < 0:
                        self.cursor = 0
                    self.changed = True
                return True
        if isinstance(event, MouseInputEvent):
            if self.location is not None:
                xposition = event.x - self.location.left
                if self.location.width > self.PANEL_SIZE and self._valid_profiles() > 0:
                    xmax = self.location.width - self.PANEL_SIZE
                else:
                    xmax = self.location.width

                if xposition < xmax:
                    if event.button in [Buttons.LEFT, Buttons.RIGHT]:
                        newcursor = (event.y - self.location.top) + self.window
                        if newcursor >= 0 and newcursor < self._valid_profiles():
                            self.cursor = newcursor
                            self.changed = True
                            if event.button == Buttons.LEFT:
                                if (
                                    self.__last_click[0] == event.y
                                    and self.__last_click[1] == event.x
                                    and (time.time() - self.__last_click[2]) <= 1.0
                                ):
                                    # A double click!
                                    self.__last_click = (-1, -1, -1.0)
                                    self.__edit_current_profile()
                                else:
                                    self.__last_click = (event.y, event.x, time.time())
                            if event.button == Buttons.RIGHT:
                                menu = PopoverMenuComponent(
                                    [
                                        (
                                            "&Edit This Profile",
                                            lambda menuentry, option: self.__edit_current_profile(),
                                        ),
                                        (
                                            "&Delete This Profile",
                                            lambda menuentry, option: self.__delete_current_profile(),
                                        ),
                                        ("-", None),
                                        (
                                            "&Add New Profile",
                                            lambda menuentry, option: self.__add_new_profile(),
                                        ),
                                    ],
                                )
                                self.register(
                                    menu,
                                    menu.bounds.offset(
                                        event.y - self.location.top,
                                        event.x - self.location.left,
                                    ),
                                )
                    return True
        if isinstance(event, ScrollInputEvent):
            if event.direction == Directions.UP:
                if self.cursor > 0:
                    self.cursor -= 3
                    if self.cursor < 0:
                        self.cursor = 0
                    self.changed = True
                return True
            if event.direction == Directions.DOWN:
                if self.cursor < (self._valid_profiles() - 1):
                    self.cursor += 3
                    if self.cursor > (self._valid_profiles() - 1):
                        self.cursor = self._valid_profiles() - 1
                    self.changed = True
                return True

        return False

    def __repr__(self) -> str:
        return "ProfileListComponent()"


class TowerListComponent(Component):
    def __init__(self, towers: TowerCollection) -> None:
        super().__init__()
        self.towers = towers
        self.cursor = 0
        self.window = 0
        self.changed = False

    def render(self, context: RenderContext) -> None:
        # No artifacts, please!
        context.clear()

        # Handle scrolling up with some buffer.
        if (self.cursor - 4) < self.window:
            self.window = self.cursor - 4
            if self.window < 0:
                self.window = 0
        # Handle scrolling down with some buffer.
        if (self.cursor + 5) > (self.window + (context.bounds.height - 1)):
            self.window = (self.cursor + 5) - (context.bounds.height - 1)
            if self.window > (len(self.towers) - (context.bounds.height - 1)):
                self.window = len(self.towers) - (context.bounds.height - 1)

        top = self.window
        bottom = min(
            self.window + context.bounds.height - 1,
            len(self.towers),
        )
        for i in range(top, bottom):
            tower = self.towers[i]
            towerno = int(i / 6)
            levelno = i % 6
            towerstr = ", ".join(str(tower).split("\n"))

            display = f"Tower {towerno + 1}, {levelno + 1} - {towerstr}"
            if len(display) < context.bounds.width:
                display = display + " " * (context.bounds.width - len(display))

            context.draw_string(i - top, 0, display, invert=(i == self.cursor))

        # Draw the horizontal label divider
        for x in range(context.bounds.width):
            context.draw_string(
                context.bounds.height - 1,
                x,
                "\u2500" if Settings.enable_unicode else "-",
                wrap=False,
            )

        self.changed = False

    @property
    def dirty(self) -> bool:
        return self.changed

    def __delete_all_records(self) -> None:
        self.towers.clear()
        self.changed = True

    def __delete_current_record(self) -> None:
        self.towers[self.cursor].clear()
        self.changed = True

    def handle_input(self, event: InputEvent) -> bool:
        if isinstance(event, KeyboardInputEvent):
            if event.character == Keys.UP:
                if self.cursor > 0:
                    self.cursor -= 1
                    self.changed = True
                return True
            if event.character == Keys.DOWN:
                if self.cursor < (len(self.towers) - 1):
                    self.cursor += 1
                    self.changed = True
                return True
            if event.character in ["d", Keys.DELETE]:
                self.__delete_current_record()
                return True
            if event.character == "r":
                self.__delete_all_records()
                return True
            if event.character == Keys.HOME:
                self.cursor = 0
                self.changed = True
                return True
            if event.character == Keys.END:
                self.cursor = len(self.towers) - 1
                self.changed = True
                return True
            if event.character == Keys.PGDN:
                self.cursor += self.location.height if self.location is not None else 1
                if self.cursor >= len(self.towers):
                    self.cursor = len(self.towers) - 1
                self.changed = True
                return True
            if event.character == Keys.PGUP:
                self.cursor -= self.location.height if self.location is not None else 1
                if self.cursor < 0:
                    self.cursor = 0
                self.changed = True
                return True
        if isinstance(event, MouseInputEvent):
            if self.location is not None:
                xposition = event.x - self.location.left
                xmax = self.location.width

                if xposition < xmax:
                    if event.button in [Buttons.LEFT, Buttons.RIGHT]:
                        newcursor = (event.y - self.location.top) + self.window
                        if newcursor >= 0 and newcursor < len(self.towers):
                            self.cursor = newcursor
                            self.changed = True
                            if event.button == Buttons.RIGHT:
                                menu = PopoverMenuComponent(
                                    [
                                        (
                                            "&Delete This Record",
                                            lambda menuentry, option: self.__delete_current_record(),
                                        ),
                                    ],
                                )
                                self.register(
                                    menu,
                                    menu.bounds.offset(
                                        event.y - self.location.top,
                                        event.x - self.location.left,
                                    ),
                                )
                    return True
        if isinstance(event, ScrollInputEvent):
            if event.direction == Directions.UP:
                if self.cursor > 0:
                    self.cursor -= 3
                    if self.cursor < 0:
                        self.cursor = 0
                    self.changed = True
                return True
            if event.direction == Directions.DOWN:
                if self.cursor < (len(self.towers) - 1):
                    self.cursor += 3
                    if self.cursor > (len(self.towers) - 1):
                        self.cursor = len(self.towers) - 1
                    self.changed = True
                return True

        return False

    def __repr__(self) -> str:
        return "TowerListComponent()"


class SRAMEditorScene(Scene):
    def create(self) -> Component:
        return TabComponent(
            [
                (
                    "&Profiles",
                    StickyComponent(
                        ClickableLabelComponent(
                            "<invert> up/down - select profile </invert> "
                            + "<invert> enter - edit selected profile </invert> "
                            + "<invert> a - add new profile </invert> "
                            + "<invert> d - delete selected profile </invert> "
                            + "<invert> esc/q - quit </invert>",
                            formatted=True,
                        ).on_click(self.__handle_profile_click),
                        ProfileListComponent(self.settings["sram"].profiles),
                        location=StickyComponent.LOCATION_BOTTOM,
                        size=1,
                    ),
                ),
                (
                    "&Tower Clears",
                    StickyComponent(
                        ClickableLabelComponent(
                            "<invert> up/down - select record </invert> "
                            + "<invert> d - delete selected record </invert> "
                            + "<invert> r - reset all records </invert> "
                            + "<invert> esc/q - quit </invert>",
                            formatted=True,
                        ).on_click(self.__handle_tower_click),
                        TowerListComponent(self.settings["sram"].towers),
                        location=StickyComponent.LOCATION_BOTTOM,
                        size=1,
                    ),
                ),
            ]
        )

    def __handle_profile_click(
        self, component: Component, event: MouseInputEvent
    ) -> bool:
        # This is hacky, we really should define a component and just handle click
        # events without checking position. However, I don't want to work on a
        # list component that sizes each entry to the entry's width/height so instead
        # I just check the mouse position.
        if event.button == Buttons.LEFT:
            location = component.location
            if location is not None:
                click_x = event.x - location.left
                click_y = event.y - location.top
                if click_y == 0 and click_x >= 111 and click_x <= 124:
                    self.__display_confirm_quit()
                    return True

        return False

    def __handle_tower_click(
        self, component: Component, event: MouseInputEvent
    ) -> bool:
        # This is hacky, we really should define a component and just handle click
        # events without checking position. However, I don't want to work on a
        # list component that sizes each entry to the entry's width/height so instead
        # I just check the mouse position.
        if event.button == Buttons.LEFT:
            location = component.location
            if location is not None:
                click_x = event.x - location.left
                click_y = event.y - location.top
                if click_y == 0 and click_x >= 79 and click_x <= 92:
                    self.__display_confirm_quit()
                    return True

        return False

    def __display_confirm_quit(self) -> None:
        self.register_component(
            DialogBoxComponent(
                "Write back changes to SRAM file?",
                [
                    (
                        "&Yes",
                        lambda c, o: self.save_profiles(),
                    ),
                    (
                        "&No",
                        lambda c, o: self.main_loop.exit(),
                    ),
                    (
                        "&Cancel",
                        lambda c, o: self.unregister_component(c),
                    ),
                ],
            )
        )

    def save_profiles(self) -> None:
        with open(self.settings["file"], "wb") as fp:
            fp.write(self.settings["sram"].data)
        self.main_loop.exit()

    def handle_input(self, event: InputEvent) -> bool:
        if isinstance(event, KeyboardInputEvent):
            if event.character in [Keys.ESCAPE, "q"]:
                self.__display_confirm_quit()

                return True
        return False


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
    try:
        with open(args.file, "rb") as fp:
            data = fp.read()
        sram = SRAM(
            data,
            is_mame_format=args.mame_compat,
        )

    except FileNotFoundError:
        # Assume they meant to create a new file.
        data = b"\xFF" * (131072 if not args.mame_compat else 524288)
        sram = SRAM(
            data,
            is_mame_format=args.mame_compat,
        )
        sram.clear()

    def wrapped(context: CursesContext) -> None:
        # Run the main program loop
        with loop_config(context):
            loop = MainLoop(
                context,
                {"file": args.file, "sram": sram},
            )
            loop.change_scene(SRAMEditorScene)
            loop.run()

    os.environ.setdefault("ESCDELAY", "0")
    curses.wrapper(wrapped)

    return 0


if __name__ == "__main__":
    sys.exit(main())
