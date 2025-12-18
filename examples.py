import json
import random
import time

from dal.dal import Source
from enums import PLATFORM_TYPE
from singletons import manager, source_dao


def create_new_source():
    id = random.randint(10000, 99999)
    source = Source(id=id, name=str(id), external_id=str(id), platform=PLATFORM_TYPE.TELEGRAM.name, is_hidden=False)
    source_dao.save(source)
    return id


def read_file(path):
    with open(path, 'r', encoding='utf-8') as file:
        return json.load(file)


def count_words(content: str, title: str = '') -> int:
    """Count words in content only (excluding title/headline)."""
    if not content:
        return 0
    words = content.split()
    return len(words)


def format_time(seconds: float) -> str:
    """Format time in a human-readable way."""
    if seconds < 1:
        milliseconds = int(seconds * 1000)
        return f"{milliseconds} ms"
    elif seconds < 60:
        return f"{seconds:.2f} seconds"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = seconds % 60
        if secs < 1:
            return f"{minutes} minute{'s' if minutes != 1 else ''}"
        else:
            return f"{minutes} minute{'s' if minutes != 1 else ''} {secs:.1f} second{'s' if secs != 1 else ''}"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60
        parts = [f"{hours} hour{'s' if hours != 1 else ''}"]
        if minutes > 0:
            parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
        if secs > 0 and minutes == 0:
            parts.append(f"{secs:.1f} second{'s' if secs != 1 else ''}")
        return " ".join(parts)


def print_processing_metadata(path: str, word_count: int, elapsed_time: float, speed: float):
    """Print colored metadata block with processing information."""
    # ANSI color codes
    RESET = '\033[0m'
    BOLD = '\033[1m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    
    time_str = format_time(elapsed_time)
    speed_str = f"{speed:.1f} words/sec" if speed >= 1 else f"{speed * 1000:.0f} words/ms"
    
    # Create metadata block
    print(f"\n{CYAN}{'='*60}{RESET}")
    print(f"{BOLD}{CYAN}📄 Processing Metadata{RESET}")
    print(f"{CYAN}{'='*60}{RESET}")
    print(f"{GREEN}File:{RESET}        {path}")
    print(f"{YELLOW}Words:{RESET}        {word_count:,} words")
    print(f"{BLUE}Time:{RESET}         {time_str}")
    print(f"{MAGENTA}Speed:{RESET}       {speed_str}")
    print(f"{CYAN}{'='*60}{RESET}\n")


def process_file(path):
    start_time = time.perf_counter()
    source_id = create_new_source()
    file = read_file(path)
    title = file.get("title", "")
    content = file.get("content", "")
    reposted_from = file.get("repostedFrom")
    word_count = count_words(content)
    result = manager.process(title, content, source_id, "english", reposted_from)
    elapsed_time = time.perf_counter() - start_time
    speed = word_count / elapsed_time if elapsed_time > 0 else 0
    print_processing_metadata(path, word_count, elapsed_time, speed)
    return result

process_file("data/examples/putin_address_to_general_assambly.json")
process_file("data/examples/macron_vision.json")
process_file("data/examples/trump_tulsa.json")
process_file("data/examples/trump_we_will_never_give_up.json")
process_file("data/examples/hitler_proclamation_to_german_nation.json")
process_file("data/examples/hitler_sportpalats_speech.json")
process_file("data/examples/linear_geometry.json")
process_file("data/examples/magic_of_math.json")
process_file("data/examples/ocean_investigations.json")
process_file("data/examples/farming_apples.json")
