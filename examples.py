import json
import random
import time

from dal.dal import Source
from enums import PLATFORM_TYPE
from singletons import manager, source_dao


def create_new_source(fixed_id=None):
    id = fixed_id if fixed_id is not None else random.randint(10000, 99999)
    source = Source(id=id, name=f"Source {id}", external_id=str(id), platform=PLATFORM_TYPE.TELEGRAM.name, is_hidden=False)
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


def process_file(path, fixed_source_id=None):
    start_time = time.perf_counter()
    file = read_file(path)
    
    # Use fixed_source_id if provided, otherwise check file, otherwise create new
    source_id = fixed_source_id or file.get("source_id") or create_new_source()
    
    # Ensure source exists in DB (especially for fixed IDs)
    if not source_dao.get_by_id(source_id):
        create_new_source(source_id)
        
    title = file.get("title", "")
    content = file.get("content", "")
    reposted_from = file.get("repostedFrom")
    word_count = count_words(content)
    result = manager.process(title, content, source_id, "english", reposted_from)
    elapsed_time = time.perf_counter() - start_time
    speed = word_count / elapsed_time if elapsed_time > 0 else 0
    print_processing_metadata(path, word_count, elapsed_time, speed)
    return result


def demonstrate_repost_depth():
    """Demonstrates the depth of reposts feature by processing a chain of related notes."""
    print("\n" + "="*60)
    print("🚀 DEMONSTRATING REPOST DEPTH FEATURE")
    print("="*60)
    
    # Process the chain in order
    process_file("data/examples/chain_1_original.json")
    process_file("data/examples/chain_2_repost.json")
    process_file("data/examples/chain_3_repost.json")
    
    print("\n✅ Repost chain processed.")
    print("Check Neo4j for the following chain:")
    print("Source 103 (Note) -> Source 102 (Source) <- Source 102 (Note) -> Source 101 (Source)")
    print("="*60 + "\n")


if __name__ == "__main__":
    # Original examples
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

    # New Repost Depth Example
    demonstrate_repost_depth()
