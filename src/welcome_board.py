import time
import os


def clear_screen() -> None:
    """Clear the terminal screen, cross-platform.

    Uses 'cls' on Windows and 'clear' on Mac/Linux/WSL.
    """
    # This works for both Windows ('cls') and Mac/Linux/WSL ('clear')
    os.system('cls' if os.name == 'nt' else 'clear')


def welcome_board() -> None:
    """Print an animated ASCII welcome banner before the pipeline starts."""
    art = r"""
                .---------------------------.
                |   Can you call me maybe   |
                '---------------------------'
                        \
                            \
                        .----====-----------.
                        |                   |
                        |    {_}     {_}    |
                        |                   |
                        |    |_________|    |
                        |                   |
                        '----====-----------'
                            ||
                        .---==---.
                        |________|
    """

    # Increased the range slightly so you have time to see it flicker!
    for i in range(7):
        clear_screen()
        if i % 2 == 0:
            print(art)
        else:
            print("\n" * 16)
        time.sleep(0.2)

    clear_screen()
    print(art)
    print("System booting...\n")


if __name__ == "__main__":
    welcome_board()
