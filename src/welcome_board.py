import time
import os

def clear_screen():
    # This works for both Windows ('cls') and Mac/Linux/WSL ('clear')
    os.system('cls' if os.name == 'nt' else 'clear')

def welcome_board():
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
            # "ON" frame
            print(art)
        else:
            # "OFF" frame: Print empty lines so the terminal doesn't jump around
            print("\n" * 16) 
            
        # 0.2 is a great speed for a glitchy flicker
        time.sleep(0.2)
        
    clear_screen()
    # Print it one last time so it stays on the screen when the flicker is done
    print(art)
    print("System booting...\n")

welcome_board()