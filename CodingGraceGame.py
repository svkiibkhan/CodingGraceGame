#!/usr/bin/env python3
"""
CodingGrace: Text-Based Adventure Game
=======================================
A text-based adventure game with three rooms, a Rock-Paper-Scissors
mini-game, ASCII art, and a player-state dictionary that tracks the
player's name, health, inventory, and choices throughout the game.

Game structure
--------------
    - Three rooms: Red (Painful Truth), Blue (Blissful Ignorance),
      Green (Magic / Rock-Paper-Scissors).
    - A guard encounter in the Blue Room that requires the correct
      sequence of actions to escape.
    - A global player_info dictionary, passed explicitly to every
      function, that holds the player's state.

Key programming concepts illustrated
-------------------------------------
    - Dictionaries for structured data
    - Functions with parameters and return values
    - While-loops for repeated interaction
    - Custom exception classes for control flow
    - Input validation and string matching
    - Floating-point comparison with math.isclose()
    - f-strings for formatted output
"""

# ---------------------------------------------------------------------------
# IMPORTS
# ---------------------------------------------------------------------------
# `random` provides functions for generating pseudo-random numbers.
# We use random.choices() in the Rock, Paper, Scissors mini-game to let
# the computer pick its move according to weighted probabilities.
import random

# `math` provides mathematical functions and constants.
# We use math.isclose() to safely compare floating-point sums (see rps()).
import math


# ---------------------------------------------------------------------------
# CUSTOM EXCEPTION FOR GAME-ENDING EVENTS
# ---------------------------------------------------------------------------
# When the player dies or wins, the game needs to stop immediately — even if
# execution is deep inside nested function calls.  A custom exception is
# well suited for this purpose because raising it unwinds the entire call
# stack back to wherever it is caught.
#
# This approach is preferable to calling exit() because exit() terminates
# the entire Python process.  In environments like Jupyter or Google Colab,
# that produces an unwanted SystemExit traceback instead of a clean ending.
#
# KEY CONCEPT: Exception classes inherit from Python's built-in Exception.
# You can attach any data you want — here we store a message string.

class GameOver(Exception):
    """Raised when the game ends, whether by death or victory."""
    pass


# ---------------------------------------------------------------------------
# INITIALIZE PLAYER STATE
# ---------------------------------------------------------------------------
# We store all player information in a single dictionary.  This makes it
# easy to pass the entire game state to any function that needs it.
#
# KEY CONCEPT: A dictionary is a collection of key-value pairs.
# Here the keys are strings ("name", "level", etc.) and the values are
# different types — a string, integers, and lists.

player_info = {
    "name": "",           # Will be set by get_player_name()
    "level": 1,           # Tracks how far the player has progressed
    "inventory": [],      # Items the player has collected
    "location": "Starting Room",
    "health": 100,        # Hit points; reduced by damage, restored by healing
    "choices": []         # History of rooms the player has visited
}


# ---------------------------------------------------------------------------
# HELPER: DISPLAY PLAYER INFO
# ---------------------------------------------------------------------------
# Rather than repeating the same for-loop every time we want to show the
# player's status, we put it in its own function.  This is the DRY
# principle: "Don't Repeat Yourself."

def show_player_info(player_info_arg):
    """Prints the current state of the player_info dictionary."""
    print("\nPlayer Info:")
    for key, value in player_info_arg.items():
        # .capitalize() makes the first letter uppercase: "name" -> "Name"
        print(f"  {key.capitalize()}: {value}")


# ===========================================================================
# ACTION FUNCTIONS
# ===========================================================================
# These functions handle game-ending events and the RPS mini-game.

def you_died(why):
    """Ends the game with a death message.

    Raises the custom GameOver exception so that main() can catch it
    and shut down cleanly, regardless of how deeply nested the call is.
    """
    print_game_over()
    print(f"{why}. Too bad!")

    # "raise" immediately stops the current function and jumps to the
    # nearest try/except block that handles this type of exception.
    raise GameOver("Player died")


def you_won(how):
    """Ends the game with a victory message."""
    print_game_over()
    print(f"{how}. The game is over. You won!")
    raise GameOver("Player won")


def next_level(player_info_arg):
    """Advances the player to the next level and prints a congratulations.

    Args:
        player_info_arg: The player state dictionary.

    Returns:
        The updated dictionary (same object, since dictionaries are mutable,
        but returning it makes the data flow explicit and readable).
    """
    player_info_arg["level"] += 1
    print(f"\nCongratulations! You have advanced to Level {player_info_arg['level']}")
    return player_info_arg


def rps(user_wins=True):
    """Plays one round of Rock, Paper, Scissors.

    Args:
        user_wins: Controls the computer's strategy.
            True  -> computer always loses (good for testing)
            False -> computer always wins
            list of 3 floats summing to ~1.0 -> weighted random choice

    Returns:
        A tuple of three strings: (label, user_choice, result)
        where result is one of: "win", "lose", "tie", "exit", "invalid"

    DESIGN NOTE — floating-point comparison:
        When user_wins is a list, we need to verify that its elements sum
        to 1.0.  However, floating-point arithmetic is imprecise:
            >>> 0.1 + 0.2 + 0.7
            0.9999999999999999
        That is *not* equal to 1.0, so a simple == check would wrongly
        reject valid weights.  math.isclose() allows a small tolerance and
        handles these rounding differences correctly.

    DESIGN NOTE — structured return values:
        The third element of the returned tuple is always one of the fixed
        strings "win", "lose", "tie", "exit", or "invalid".  Callers can
        compare against these constants directly (e.g., result == "win")
        rather than searching inside display-oriented phrases, which would
        be fragile and error-prone.
    """

    # --- Constants ---
    CHOICES = ["Rock", "Paper", "Scissors"]

    # Each key beats its value: Rock beats Scissors, Paper beats Rock, etc.
    WIN_SCENARIOS = {
        "Rock": "Scissors",
        "Paper": "Rock",
        "Scissors": "Paper"
    }

    EXIT_OPTIONS = ["No thanks", "Done"]

    # --- Get user input ---
    print("Let's play Rock, Paper, Scissors!")
    prompt = ("Choose rock, paper, or scissors by entering the word "
              "(or type 'no thanks' or 'done' to exit): ")
    user_input = input(prompt).strip().capitalize()

    # --- Handle exit ---
    if user_input in EXIT_OPTIONS:
        print("Maybe next time! Exiting the game.")
        return ("You chose not to play", user_input, "exit")

    # --- Validate ---
    if user_input not in CHOICES:
        print("Invalid choice. Please enter Rock, Paper, or Scissors.")
        return ("Invalid choice", user_input, "invalid")

    # --- Determine computer choice ---
    if (isinstance(user_wins, list)
            and len(user_wins) == 3
            and all(isinstance(w, (int, float)) for w in user_wins)
            and math.isclose(sum(user_wins), 1.0)):
        # Weighted random selection using the provided probabilities.
        # random.choices() returns a list; [0] gets the single element.
        computer_choice = random.choices(CHOICES, weights=user_wins, k=1)[0]
    elif user_wins:
        # Deterministic: computer picks the choice that LOSES to the user.
        computer_choice = WIN_SCENARIOS[user_input]
    else:
        # Deterministic: computer picks the choice that BEATS the user.
        # We search WIN_SCENARIOS for the key whose value equals user_input.
        computer_choice = next(
            choice for choice, beats in WIN_SCENARIOS.items()
            if beats == user_input
        )

    # --- Determine result ---
    if WIN_SCENARIOS[user_input] == computer_choice:
        result = "win"
        display = "You win!"
    elif WIN_SCENARIOS[computer_choice] == user_input:
        result = "lose"
        display = "You lose!"
    else:
        result = "tie"
        display = "It's a tie!"

    print(f"{computer_choice}. {display}")
    return ("You typed", user_input, result)


# ===========================================================================
# CHARACTER FUNCTIONS
# ===========================================================================

def guard():
    """Handles the guard encounter in the Blue Room.

    The guard puzzle has two states controlled by the boolean `guard_moved`:
        - If the guard has NOT moved, running distracts him (safe) but
          going for the door is fatal (he catches you).
        - If the guard HAS moved, the door is safe but running again
          is fatal (he is now alert).

    The player must first "run" (to distract), then "door" (to escape).
    """
    print_guard()
    print("You approach the guard, he's still sleeping.")
    print("Suddenly you knocked a wooden cask with a mug on it... CRASSH!")
    print("\n'Hey, you! What you doing 'ere?'")

    guard_moved = False  # Tracks whether the guard has been distracted

    # This is an "infinite loop" that keeps asking for input until the
    # player either escapes (return) or dies (GameOver exception).
    while True:
        next_action = input("[run | door] > ").lower()

        if next_action == "run" and guard_moved:
            you_died("The guard was faster than he looks and your world goes dark...")

        elif next_action == "run" and not guard_moved:
            print("Guard jumps up and looks the other way, missing you entirely.")
            guard_moved = True  # The guard is now distracted

        elif next_action == "door" and guard_moved:
            print("You just slipped through the door before the guard realised it.")
            print("You are now outside, home free! Congratulations!")
            return  # Success — control returns to the calling room function

        elif next_action == "door" and not guard_moved:
            you_died("The guard was faster than he looks and your world goes dark...")

        else:
            print("Not sure what you meant there... try again.")


# ===========================================================================
# ROOM FUNCTIONS
# ===========================================================================
# Each room function receives and returns the player_info dictionary.
# Returning it explicitly (even though dictionaries are mutable and the
# caller already has a reference to the same object) makes the data flow
# visible, which is helpful when reading the code.

def blissful_ignorance_of_illusion_room(player_info_arg):
    """The Blue Room: treasure chest and guard encounter."""
    print_chest()
    print("\nYou have entered the Blue Room.")

    # --- Update player state ---
    player_info_arg["location"] = "Blue Room"

    healing = 30
    illusion = "Crystal Mirror"
    player_info_arg["health"] += healing

    # Only add the item if the player does not already have it.
    # This prevents duplicates if the player re-enters the room.
    if illusion not in player_info_arg["inventory"]:
        player_info_arg["inventory"].append(illusion)
        print(f"The blissful ignorance restores {healing} health "
              f"and grants you the {illusion}.")

    player_info_arg["choices"].append("Blue Room")
    show_player_info(player_info_arg)

    # --- Treasure chest ---
    treasure_chest = ["diamonds", "gold", "silver", "sword"]
    print("You see a room with a wooden treasure chest on the left, "
          "and a sleeping guard on the right in front of the door.")

    action = input("\nWhat do you do? > ")

    if action.lower() in ["treasure", "chest", "left"]:
        print("Oh, it's full of treasure!")

        print("Open it?  Press '1'")
        print("Leave it alone.  Press '2'")
        choice = input("> ")

        if choice == "1":
            print("Let's see what's in here... /grins")
            print("The chest creaks open, and the guard is still sleeping. "
                  "That's one heavy sleeper!")

            # ", ".join(list) combines list elements into a single string
            # separated by ", ".  Example: ["a","b","c"] -> "a, b, c"
            print(f"You find: {', '.join(treasure_chest)}.")

            print("\nWhat do you want to do?")
            print(f"Take all {len(treasure_chest)} treasure, press '1'")
            print("Leave it, press '2'")

            treasure_choice = input("> ")
            if treasure_choice == "1":
                print("\tAmazing! Bounty and a shiney new sword. "
                      "/drops your crappy sword in the empty treasure chest.")
                print(f"\tYou just received [{', '.join(treasure_chest)}]")
            elif treasure_choice == "2":
                print("It will still be here (I hope), right after "
                      "I get past this guard.")
            # Note: if the player types something other than "1" or "2",
            # we simply skip ahead to the guard encounter.

        elif choice == "2":
            print("Who needs treasure, let's get out of here.")

    else:
        print("The guard is more interesting, let's go that way!")

    # Regardless of the treasure decision, the player now faces the guard.
    guard()
    return player_info_arg


def painful_truth_of_reality_room(player_info_arg):
    """The Red Room: a fearsome creature that may devour the player.

    Returns:
        "flee" if the player chose to flee (so the adventure loop continues),
        or raises GameOver if the player dies.
    """
    print_monster()
    print("\nYou have entered the Red Room.")

    # --- Update player state ---
    player_info_arg["location"] = "Red Room"

    damage = 20
    knowledge = "Truth Scroll"
    player_info_arg["health"] -= damage
    if knowledge not in player_info_arg["inventory"]:
        player_info_arg["inventory"].append(knowledge)
        print(f"The painful truth costs you {damage} health "
              f"but grants you the {knowledge}.")

    player_info_arg["choices"].append("Red Room")
    show_player_info(player_info_arg)

    print("You see the great evil Melon Usk.")
    print("He, it, whatever stares at you and you go insane.")
    print("Do you flee for your life or eat your head?")

    next_move = input("> ")

    # Using `in` lets the player type "flee now" or "I flee" and still match.
    if "flee" in next_move:
        # Returning "flee" tells the loop in start_new_adventure() to
        # present the door choice again.  This avoids using recursion,
        # which would add a new stack frame every time the player flees
        # and could eventually cause a RecursionError.
        return "flee"
    else:
        you_died("You died. Well, that was tasty!")


def green_magic_room(player_info_arg):
    """The Green Room: play Rock, Paper, Scissors against a magician.

    Returns:
        "flee" if the player lost RPS (so the adventure loop continues),
        or raises GameOver (victory) if the player won.
    """
    print_magician()
    print("Welcome to the green magic room.")
    print("Prepare yourself to play a magic game of Rock, Paper, Scissors.")
    print("If you win, you will receive a gold coin.")
    print("If you do not win, you will return to the start of the game.\n")

    # --- Update player state ---
    player_info_arg["location"] = "Green Room"

    special_item = "Emerald Amulet"
    if special_item not in player_info_arg["inventory"]:
        player_info_arg["inventory"].append(special_item)
        print(f"You found a {special_item} and added it to your inventory!")

    player_info_arg["choices"].append("Green Room")
    show_player_info(player_info_arg)

    # --- Play RPS until the result is not a tie ---
    # We initialize result to "tie" so the while-loop runs at least once.
    result = "tie"
    while result == "tie":
        # Weighted probabilities: [Rock=0.3, Paper=0.4, Scissors=0.3]
        _label, _choice, result = rps([0.3, 0.4, 0.3])

        if result == "tie":
            print("You tied and can play Rock, Paper, Scissors again.\n")

        elif result in ("exit", "invalid"):
            # The player declined to play or entered invalid input.
            # Treat this the same as a loss: return to the adventure loop.
            print("The magician frowns. You must try again later.\n")
            return "flee"

    if result == "win":
        you_won("The magician gave you a gold coin. Congratulations!")
    else:
        # The player lost — return to the adventure loop.
        print("The magician waves his hand and you are whisked away...\n")
        return "flee"


# ===========================================================================
# CONTROL FUNCTIONS
# ===========================================================================

def get_player_name(player_info_arg):
    """Prompts the player for their name and optionally assigns a nickname.

    The game playfully suggests an alternative name ("Rainbow Unicorn").
    The player can accept it, reject it, or give an unexpected answer —
    each path produces different output.

    Args:
        player_info_arg: The player state dictionary to update.

    Returns:
        The updated player_info dictionary.
    """
    player_info_arg["name"] = input("Enter your player name: ").strip()

    alt_name = "Rainbow Unicorn"
    answer = input(f"Your name is {alt_name.upper()}, is that correct? [Y|N] > ")

    if answer.lower() in ["y", "yes"]:
        player_info_arg["name"] = alt_name
        print(f"You are fun, {player_info_arg['name'].upper()}! "
              f"Let's begin our adventure!")

    elif answer.lower() in ["n", "no"]:
        print(f"Ok, picky. {player_info_arg['name'].upper()} it is. "
              f"Let's get started on our adventure.")

    else:
        print(f"Trying to be funny? Well, you will now be called "
              f"{alt_name.upper()} anyway.")
        player_info_arg["name"] = alt_name
        print_smiley_face()

    return player_info_arg


def purple_waterfall_room(player_info_arg):
    """A room that is a halleway that leads to a massive waterfall."""

    # 2. Announce the room
    print("\nYou have entered the Purple Room.")
    print("A massive intense waterfall is at the end of the hall.")

    # 3. Update player state ─── REQUIRED ────────────────────────────────────
    player_info_arg["location"] = "Purple Room"

    damage_or_healing = 15   # positive = heal, negative = damage
    player_info_arg["health"] += damage_or_healing

    item = "Aqua Trident"
    if item not in player_info_arg["inventory"]:
        player_info_arg["inventory"].append(item)
        print(f"You found a {item}!")

    player_info_arg["choices"].append("Purple Room")

    # 4. Display state ─── REQUIRED ──────────────────────────────────────────
    show_player_info(player_info_arg)

    # 5. Room narrative and interaction
    print("You should head towards the waterfall.")
    print("Type 'drink' to drink from the waterfall or type 'flee' to escape.")

    action = input("> ").strip().lower()

    if action == "drink":
        print("The magical water restores your energy.")
        return player_info_arg

    elif action == "jump":
        you_died("You jump into the waterfall and are crushed by the current.")

    elif "flee" in action:
        return "flee"

    return player_info_arg



def orange_flame_room(player_info_arg):
    """The Orange Flame Room: survive a fiery chamber by making the right choice."""

# 1. Announce the room
    print("\nYou have entered the Orange Flame Room.")
    print("The room glows with fierce orange fire and the air feels impossible to breathe.")

# 2. Update player state
    player_info_arg["location"] = "Orange Flame Room"

    #Player takes fire damage
    damage = 10
    player_info_arg["health"] -= damage

    # Add special item if not already in inventory
    item = "Flame Shield"
    if item not in player_info_arg["inventory"]:
        player_info_arg["inventory"].append(item)
        print(f"You found a {item}!")

    # Record that the player visited this room
    player_info_arg["choices"].append("Orange Flame Room")

# 3. Display player status
    show_player_info(player_info_arg)

# 4. Room narrative and player interaction
    print("A wall of fire rises in front of you.")
    print("Type 'shield' to push through the flames, 'jump' to leap into them, or 'flee' to escape.")

    action = input("> ").strip().lower()

    # Player survives using the shield
    if action == "shield":
        print("You raise the Flame Shield and force your way through safely.")
        return player_info_arg
    
    # Player dies by jumping into the fire
    elif action == "jump":
        you_died("You jump straight into the flames and are swallowed by the fire")

     # Player flees and returns to the dungeon doors
    elif "flee" in action:
        return "flee"
    
    # Any other input leads to death
    else:
        you_died("You freeze for too long and the fire closes in around you")




def start_new_adventure(player_info_arg):
    """Presents the three-door choice and routes to the selected room.

    A while-loop drives the game flow: each iteration shows the dungeon,
    asks the player to pick a door, and dispatches to the corresponding
    room function.  If the room returns the string "flee", the loop
    continues and the doors are presented again.  If the room completes
    normally (or raises GameOver), the loop ends.

    Using a loop rather than recursion is important here.  If each flee
    called start_new_adventure() again, every cycle would add a new frame
    to the call stack, and after enough cycles Python would raise a
    RecursionError.

    Args:
        player_info_arg: The player state dictionary.
    """

    while True:
        print_new_dungeon()
        print("You enter a room, and you see a red door to your left "
              "and blue and green doors to your right.")
        door_picked = input("Do you pick the red door, blue door, "
                            "or green door? > ")

        # We compare only the first few characters so that inputs like
        # "red door", "blue", or "green one" all work.
        door = door_picked.strip().lower()

        if door.startswith("red"):
            room_result = painful_truth_of_reality_room(player_info_arg)
        elif door.startswith("blue"):
            room_result = blissful_ignorance_of_illusion_room(player_info_arg)
        elif door.startswith("green"):
            room_result = green_magic_room(player_info_arg)
        else:
            print("Sorry, it's either 'red', 'blue', or 'green' as the "
                  "answer. You're the weakest link, goodbye!")
            # Continue the loop so the player can try again.
            continue

        # If the room returned "flee", we loop back to the door choice.
        # If it returned normally (Blue Room after the guard), we break out.
        if room_result != "flee":
            break

    return player_info_arg


def main(player_info_main):
    """Main entry point: greets the player, runs the adventure, says goodbye.

    The try/except block catches the GameOver exception that you_died() or
    you_won() may raise, ensuring that the farewell message is always printed
    regardless of whether the game ended in death, victory, or a normal exit.
    """
    print("\nWelcome to the game!")

    player_info_main = get_player_name(player_info_main)

    # If the player dies or wins, the corresponding function raises GameOver.
    # The except clause catches it so execution can continue to the farewell.
    try:
        player_info_main = start_new_adventure(player_info_main)
    except GameOver:
        pass  # The death/victory message was already printed.

    print("\nThe end\n")
    print(f"Thanks for playing, {player_info_main['name'].upper()}")

    # Returning the dictionary lets the caller at the bottom of the script
    # capture the final state (e.g., for testing or post-game display).
    return player_info_main


# ===========================================================================
# ASCII ART FUNCTIONS
# ===========================================================================
# Each function below prints a decorative text image to the console.
# These use raw strings (r"...") so that backslashes are treated literally
# and we do not need to double-escape them.

def print_monster():
    print()
    print(r"                           |                     | ")
    print(r"                        \     /               \     / ")
    print(r"                       -= .'> =-             -= <'. =- ")
    print(r"                          '.'.                 .'.' ")
    print(r"                            '.'.             .'.' ")
    print(r"                              '.'.----^----.'.' ")
    print(r"                               /'==========='\ ")
    print(r"                           .  /  .-.     .-.  \  . ")
    print(r"                           :'.\ '.O.') ('.O.' /.':   ")
    print(r"                           '. |               | .'   ")
    print(r"                             '|      / \      |' ")
    print(r"                              \     (o'o)     / ")
    print(r"                              |\             /| ")
    print(r"                              \('._________.')/ ")
    print(r"                               '. \/|_|_|\/ .'                ")
    print(r"                                /'._______.'\  ")
    print()


def print_chest():
    print()
    print(r"                      _.--. ")
    print(r"                  _.-'_:-'|| ")
    print(r"              _.-'_.-::::'|| ")
    print(r"         _.-:'_.-::::::'  || ")
    print(r"       .'`-.-:::::::'     || ")
    print(r"      /.'`;|:::::::'      ||_ ")
    print(r"     ||   ||::::::'     _.;._'-._ ")
    print(r"     ||   ||:::::'  _.-!oo @.!-._'-. ")
    print(r"     ('.  ||:::::.-!()oo @!()@.-'_.| ")
    print(r"      '.'-;|:.-'.&$@.& ()$%-'o.'-U|| ")
    print(r"        `>'-.!@%()@'@_%-'_.-o _.|'|| ")
    print(r"         ||-._'-.@.-'_.-' _.-o  |'|| ")
    print(r"         ||=[ '-._.-+U/.-'    o |'|| ")
    print(r"         || '-.]=|| |'|      o  |'|| ")
    print(r"         ||      || |'|        _| '; ")
    print(r"         ||      || |'|    _.-'_.-' ")
    print(r"         |'-._   || |'|_.-'_.-' ")
    print(r"          '-._'-.|| |' `_.-' ")
    print(r"              '-.||_/.-' ")
    print()


def print_guard():
    print()
    print(r"                                                  ___I___ ")
    print(r"                                                 /=  |  #\ ")
    print(r"                                                /.__-| __ \ ")
    print(r"                                                |/ _\_/_ \| ")
    print(r"                                                (( __ \__)) ")
    print(r"                                             __ ((()))))()) __ ")
    print(r"                                           ,'  |()))))(((()|# `. ")
    print(r"                                          /    |^))()))))(^|   =\ ")
    print(r"                                         /    /^v^(())()()v^;'  .\ ")
    print(r"                                         |__.'^v^v^))))))^v^v`.__| ")
    print(r"                                        /_ ' \______(()_____(   | ")
    print(r"                                   _..-'   _//_____[xxx]_____\.-| ")
    print(r"                                  /,_#\.=-' /v^v^v^v^v^v^v^v^| _| ")
    print(r"                                  \)|)      v^v^v^v^v^v^v^v^v| _| ")
    print(r"                                   ||       :v^v^v^v^v^v`.-' |#  \, ")
    print(r"                                   ||       v^v^v^v`_/\__,--.|\_=_/ ")
    print(r"                                   ><       :v^v____|  \_____|_ ")
    print(r"                                ,  ||       v^      /  \       / ")
    print(r"                               //\_||_)\    `/_..-._\   )_...__\ ")
    print(r"                              ||   \/  #|     |_='_(     |  =_(_ ")
    print(r"                              ||  _/\_  |    /     =\    /  '  =\ ")
    print(r"                               \\\/ \/ )/    |=____#|    '=....#| ")
    print()


def print_game_over():
    print()
    print(r"   _____          __  __ ______    ______      ________ _____  ")
    print(r"  / ____|   /\   |  \/  |  ____|  / __ \ \    / /  ____|  __ \ ")
    print(r" | |  __   /  \  | \  / | |__    | |  | \ \  / /| |__  | |__) |")
    print(r" | | |_ | / /\ \ | |\/| |  __|   | |  | |\ \/ / |  __| |  _  / ")
    print(r" | |__| |/ ____ \| |  | | |____  | |__| | \  /  | |____| | \ \ ")
    print(r"  \_____/_/    \_\_|  |_|______|  \____/   \/   |______|_|  \_\\")
    print()


def print_smiley_face():
    print()
    print(r"       *****       ")
    print(r"    **       **    ")
    print(r"  **  O   O   **   ")
    print(r" **     \_/     **  ")
    print(r" **              **  ")
    print(r"  **   \___/   **   ")
    print(r"    **       **    ")
    print(r"       *****       ")
    print()


def print_magician():
    print()
    print(r"                                                  _____ ")
    print(r"                                                 /     \ ")
    print(r"                                                /       \ ")
    print(r"                                               /_________\ ")
    print(r"                                              |         | ")
    print(r"                                              |  () ()  | ")
    print(r"                                               \   ^   / ")
    print(r"                                                \_____/ ")
    print(r"                                                 ||||| ")
    print(r"                                                 ||||| ")
    print(r"                                             ____/  _  \____ ")
    print(r"                                            /    |       |   \ ")
    print(r"                                           /     |       |    \ ")
    print(r"                                          |      |       |     | ")
    print(r"                                           \_____|_______|_____/ ")
    print(r"                                             /   _______   \ ")
    print(r"                                            /               \ ")
    print(r"                                           |    O     O     | ")
    print(r"                                            \_______________/ ")
    print(r"                                             |||         ||| ")
    print(r"                                             |||         ||| ")
    print(r"                                             |||         ||| ")
    print(r"                                            (___)       (___) ")
    print()


def print_new_dungeon():
    print()
    print(r"   _____________________________________________________________________________")
    print(r" /|     -_-                                                           _-      |\ ")
    print(r"/ |_-_- _                                                     -_- _-   -_-   -| \   ")
    print(r"  |                                  _-  _--                                     | ")
    print(r"  |                                  ,                                           |")
    print(r"  |      .-'  '-.        '(        .-'  '-.       '(        .-'  '-.            |")
    print(r"  |    . |        .      )'      . |        .    )'      . |        .          |")
    print(r"  |   /   |   ()    \      U      /   |   ()    \      U      /   |   ()    \   |")
    print(r"  |  |    |    ;     | o   T   o |    |    ;     | o   T   o |    |    ;     |  |")
    print(r"  |  |    |     ;    |  .  |  .  |    |     ;    |  .  |  .  |    |     ;    |  |")
    print(r"  |  |    |     ;    |   . | .   |    |     ;    |   . | .   |    |     ;    |  |")
    print(r"  |  |    |     ;    |    .|.    |    |     ;    |    .|.    |    |     ;    |  |")
    print(r"  |  |    |____;_____|     |     |    |____;_____|     |     |    |____;_____|  |  ")
    print(r"  |  |   /  __ ;  -  |     !     |   /     '() _-|     !     |  /     '() _-  |  |")
    print(r"  |  |  / __  ()     |  -      - |  /  __--    -|  -      -  | /  __--     -  |  |")
    print(r"  |  | /        __-- |    _- _   | /        __--|    _- _   | /        __--_  |  |")
    print(r"  |__|/________________|_________|/________________|_________|/________________|__|")
    print(r" /                                                        _ -                      \ ")
    print(r"/   -_- _ -                  _- _---                             -_-  -_-         \ ")
    print()


# ===========================================================================
# ENTRY POINT
# ===========================================================================
# The `if __name__ == '__main__':` guard ensures this block only runs when
# the script is executed directly (e.g., `python3 game.py`).  If someone
# imports this file as a module, the game will NOT start automatically —
# they can call main(player_info) themselves when ready.

if __name__ == '__main__':
    player_info = main(player_info)
