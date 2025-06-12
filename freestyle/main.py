import random
import curses
import time

def load_rhyme_groups(filename):
    """Load rhyming word groups (separated by empty lines)."""
    try:
        with open(filename, "r") as f:
            lines = [line.strip() for line in f.readlines()]
    except FileNotFoundError:
        raise FileNotFoundError("🚨 dictionary.txt not found!")

    rhyme_groups = []
    current_group = []
    
    for line in lines:
        if line:
            current_group.append(line)
        elif current_group:
            rhyme_groups.append(current_group)
            current_group = []
    
    if current_group:
        rhyme_groups.append(current_group)
    
    if not rhyme_groups:
        raise ValueError("😅 No valid word groups in dictionary.txt!")
    
    return rhyme_groups

def save_rhyme_groups(filename, rhyme_groups):
    """Save rhyming word groups back to file."""
    with open(filename, "w") as f:
        for group in rhyme_groups:
            f.write("\n".join(group) + "\n\n")

def safe_addstr(win, y, x, text, attr=0):
    """Safely add string without causing curses errors."""
    max_y, max_x = win.getmaxyx()
    if y < 0 or y >= max_y or x < 0 or x + len(text) >= max_x:
        return
    try:
        win.addstr(y, x, text, attr)
    except curses.error:
        pass

def draw_header(stdscr):
    """Draw the app title and instructions."""
    height, width = stdscr.getmaxyx()
    
    # Title box
    header = "🎤 FREESTYLE TRAINER 🎤"
    safe_addstr(stdscr, 1, width//2 - len(header)//2, header, curses.A_BOLD)
    
    # Instructions
    help_text = [
        "SPACE: New Word",
        "R: Rhyme Help",
        "A: Add Word",
        "Q: Quit"
    ]
    for i, line in enumerate(help_text, start=3):
        safe_addstr(stdscr, i, width//2 - len(line)//2, line, curses.A_DIM)
    
    # Divider line
    try:
        stdscr.hline(5, 1, curses.ACS_HLINE, width - 2)
    except curses.error:
        pass

def flash_word(stdscr, word):
    """Animate word flash with centered styling."""
    height, width = stdscr.getmaxyx()
    y, x = height//2, max(0, width//2 - len(word)//2)
    
    # Clear line
    stdscr.move(y, 0)
    stdscr.clrtoeol()
    
    # Fade-in effect
    colors = [curses.COLOR_YELLOW, curses.COLOR_CYAN, curses.COLOR_MAGENTA, curses.COLOR_GREEN, curses.COLOR_WHITE]
    for i in range(5):
        curses.init_pair(i+1, colors[i], curses.COLOR_BLACK)
        safe_addstr(stdscr, y, x, word, curses.A_BOLD | curses.color_pair(i+1))
        stdscr.refresh()
        time.sleep(0.05)
    
    # Final highlight
    curses.init_pair(6, curses.COLOR_WHITE, curses.COLOR_BLUE)
    safe_addstr(stdscr, y, x, word, curses.A_BOLD | curses.color_pair(6))
    stdscr.refresh()

def show_rhymes_safe(stdscr, word, rhyme_group):
    """Simpler rhyme display that won't crash."""
    height, width = stdscr.getmaxyx()
    y = height // 2 - len(rhyme_group) // 2
    
    # Clear center area
    for i in range(max(0, y-1), min(height, y + len(rhyme_group) + 2)):
        stdscr.move(i, 0)
        stdscr.clrtoeol()
    
    # Display rhyme title
    title = f"Rhymes for: {word}"
    safe_addstr(stdscr, y-1, width//2 - len(title)//2, title, curses.A_BOLD)
    
    # Display rhymes
    for i, rhyme in enumerate(rhyme_group):
        attr = curses.A_BOLD | curses.color_pair(6) if rhyme == word else curses.A_NORMAL
        safe_addstr(stdscr, y+i, width//2 - len(rhyme)//2, rhyme, attr)
    
    stdscr.refresh()
    time.sleep(2)
    
    # Clear rhymes
    for i in range(max(0, y-1), min(height, y + len(rhyme_group) + 2)):
        stdscr.move(i, 0)
        stdscr.clrtoeol()

def get_user_input(stdscr, prompt):
    """Get user input safely with a prompt."""
    curses.echo()
    height, width = stdscr.getmaxyx()
    
    # Clear input area
    for i in range(height-3, height):
        stdscr.move(i, 0)
        stdscr.clrtoeol()
    
    safe_addstr(stdscr, height-2, 1, prompt, curses.A_BOLD)
    stdscr.refresh()
    
    input_str = stdscr.getstr(height-2, len(prompt)+2, 20).decode('utf-8')
    curses.noecho()
    return input_str.strip()

def add_word_to_group(stdscr, rhyme_groups, current_rhyme_group):
    """Add a new word to the current rhyme group."""
    if not current_rhyme_group:
        return
    
    new_word = get_user_input(stdscr, "Enter word to add:")
    if not new_word:
        return
    
    if new_word in current_rhyme_group:
        prompt = f"'{new_word}' already exists!"
        safe_addstr(stdscr, stdscr.getmaxyx()[0]-1, 1, prompt, curses.A_BOLD)
        stdscr.refresh()
        time.sleep(1)
        return
    
    current_rhyme_group.append(new_word)
    save_rhyme_groups("dictionary.txt", rhyme_groups)
    
    prompt = f"Added '{new_word}' to group!"
    safe_addstr(stdscr, stdscr.getmaxyx()[0]-1, 1, prompt, curses.A_BOLD)
    stdscr.refresh()
    time.sleep(1)

def main(stdscr):
    # Init colors
    curses.curs_set(0)
    curses.start_color()
    
    # Load words
    try:
        rhyme_groups = load_rhyme_groups("dictionary.txt")
    except Exception as e:
        stdscr.addstr(0, 0, str(e), curses.A_BOLD)
        stdscr.refresh()
        stdscr.getch()
        return
    
    current_word = None
    current_rhyme_group = None
    
    while True:
        stdscr.clear()
        draw_header(stdscr)
        
        if current_word:
            flash_word(stdscr, current_word)
        
        key = stdscr.getch()
        
        if key == ord(' '):
            current_rhyme_group = random.choice(rhyme_groups)
            current_word = random.choice(current_rhyme_group)
            
        elif key == ord('r'):
            if current_word and current_rhyme_group:
                show_rhymes_safe(stdscr, current_word, current_rhyme_group)
                flash_word(stdscr, current_word)  # Redraw current word
            
        elif key == ord('a'):
            if current_rhyme_group:
                add_word_to_group(stdscr, rhyme_groups, current_rhyme_group)
            
        elif key == ord('q'):
            break

if __name__ == "__main__":
    print("Launching Freestyle Trainer... (press 'q' to exit)")
    curses.wrapper(main)
    print("🔥 Session ended. Keep rhyming!")
