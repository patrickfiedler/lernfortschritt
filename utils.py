import random

# English adjectives (at least one per letter A-Z)
ADJECTIVES = [
    # A
    'active', 'alert', 'awesome', 'agile', 'amazing',
    # B
    'brave', 'bright', 'bold', 'bouncy', 'brilliant',
    # C
    'calm', 'clever', 'cool', 'cheerful', 'creative', 'curious', 'cozy',
    # D
    'daring', 'dazzling', 'delightful', 'dizzy', 'dreamy',
    # E
    'eager', 'enchanting', 'energetic', 'excited',
    # F
    'free', 'fine', 'friendly', 'funny', 'fuzzy', 'fearless', 'fantastic',
    # G
    'gentle', 'great', 'gleeful', 'glowing', 'golden', 'graceful',
    # H
    'happy', 'honest', 'hopeful', 'humble', 'heroic',
    # I
    'inventive', 'incredible', 'imaginative', 'inspired',
    # J
    'jolly', 'joyful', 'jazzy', 'jovial',
    # K
    'kind', 'keen', 'knightly',
    # L
    'lively', 'lucky', 'lovely', 'loyal', 'luminous',
    # M
    'merry', 'magical', 'majestic', 'mindful', 'mighty',
    # N
    'nice', 'noble', 'nimble', 'neat', 'nifty',
    # O
    'optimistic', 'original', 'outstanding', 'open',
    # P
    'proud', 'patient', 'peaceful', 'playful', 'plucky',
    # Q
    'quick', 'quiet', 'quirky',
    # R
    'radiant', 'relaxed', 'reliable', 'remarkable', 'royal',
    # S
    'strong', 'swift', 'smart', 'soft', 'sweet', 'sporty', 'sunny', 'splendid',
    # T
    'talented', 'thoughtful', 'trusty', 'terrific', 'tranquil',
    # U
    'unique', 'upbeat', 'unstoppable',
    # V
    'valiant', 'vibrant', 'vivid', 'versatile',
    # W
    'wild', 'warm', 'wonderful', 'witty', 'wise', 'whimsical',
    # X
    'xenial',
    # Y
    'young', 'youthful', 'yearning',
    # Z
    'zany', 'zealous', 'zen', 'zippy', 'zesty'
]

# English animal names (at least one per letter A-Z)
ANIMALS = [
    # A
    'antelope', 'alpaca', 'armadillo', 'alligator',
    # B
    'bear', 'bird', 'beaver', 'badger', 'bunny', 'butterfly', 'buffalo',
    # C
    'cat', 'cheetah', 'chipmunk', 'crab', 'crane', 'cricket',
    # D
    'dog', 'deer', 'dolphin', 'dove', 'duck', 'dragonfly',
    # E
    'eagle', 'elephant', 'elk', 'emu',
    # F
    'fox', 'fish', 'frog', 'falcon', 'flamingo', 'firefly', 'finch',
    # G
    'goose', 'giraffe', 'gorilla', 'gazelle', 'gecko',
    # H
    'hedgehog', 'horse', 'hamster', 'heron', 'hummingbird', 'hippo', 'hawk',
    # I
    'ibis', 'iguana', 'impala',
    # J
    'jaguar', 'jellyfish', 'jackrabbit', 'jay',
    # K
    'koala', 'kangaroo', 'kiwi', 'kingfisher',
    # L
    'lion', 'leopard', 'lemur', 'llama', 'lobster', 'lark',
    # M
    'mouse', 'moose', 'meerkat', 'macaw', 'mantis', 'mongoose',
    # N
    'narwhal', 'newt', 'nightingale', 'numbat',
    # O
    'owl', 'otter', 'ostrich', 'octopus', 'ocelot', 'oriole',
    # P
    'panda', 'penguin', 'parrot', 'peacock', 'pelican', 'puma', 'porcupine',
    # Q
    'quail', 'quokka',
    # R
    'rabbit', 'raven', 'raccoon', 'reindeer', 'robin', 'rooster',
    # S
    'swan', 'seal', 'sparrow', 'stork', 'salmon', 'squirrel', 'starfish', 'sloth',
    # T
    'tiger', 'turtle', 'toucan', 'tapir', 'termite',
    # U
    'urchin', 'urial',
    # V
    'viper', 'vulture', 'vicuna',
    # W
    'wolf', 'whale', 'walrus', 'wombat', 'woodpecker', 'wren',
    # X
    'xerus',
    # Y
    'yak', 'yellowjacket',
    # Z
    'zebra', 'zebrafish'
]

CONSONANTS = 'bcdfghjklmnprstvw'
VOWELS = 'aeiou'


# Index adjectives and animals by first letter for matching initials
ADJECTIVES_BY_LETTER = {}
for adj in ADJECTIVES:
    letter = adj[0].lower()
    if letter not in ADJECTIVES_BY_LETTER:
        ADJECTIVES_BY_LETTER[letter] = []
    ADJECTIVES_BY_LETTER[letter].append(adj)

ANIMALS_BY_LETTER = {}
for animal in ANIMALS:
    letter = animal[0].lower()
    if letter not in ANIMALS_BY_LETTER:
        ANIMALS_BY_LETTER[letter] = []
    ANIMALS_BY_LETTER[letter].append(animal)


def generate_username(existing_usernames=None, vorname=None, nachname=None):
    """Generate a unique username like 'happypanda'.

    If vorname (first name) and nachname (last name) are provided,
    tries to match initials (e.g., 'Max Müller' -> 'merrymoose').
    """
    if existing_usernames is None:
        existing_usernames = set()

    # Try to match initials if name is provided
    if vorname and nachname:
        vorname_initial = vorname[0].lower()
        nachname_initial = nachname[0].lower()

        # Get adjectives and animals matching the initials
        matching_adjs = ADJECTIVES_BY_LETTER.get(vorname_initial, [])
        matching_animals = ANIMALS_BY_LETTER.get(nachname_initial, [])

        # If we have matches for both, try those first
        if matching_adjs and matching_animals:
            shuffled_adjs = matching_adjs.copy()
            shuffled_animals = matching_animals.copy()
            random.shuffle(shuffled_adjs)
            random.shuffle(shuffled_animals)

            for adj in shuffled_adjs:
                for animal in shuffled_animals:
                    username = f"{adj}{animal}"
                    if username not in existing_usernames:
                        return username

    # Fallback: random selection
    attempts = 0
    while attempts < 1000:
        adj = random.choice(ADJECTIVES)
        animal = random.choice(ANIMALS)
        username = f"{adj}{animal}"
        if username not in existing_usernames:
            return username
        attempts += 1

    # Last resort: add number
    return f"{adj}{animal}{random.randint(1, 999)}"


def generate_password():
    """Generate password in cvcvcvnn format (e.g., 'bacado42')."""
    password = ''
    password += random.choice(CONSONANTS)
    password += random.choice(VOWELS)
    password += random.choice(CONSONANTS)
    password += random.choice(VOWELS)
    password += random.choice(CONSONANTS)
    password += random.choice(VOWELS)
    password += str(random.randint(0, 9))
    password += str(random.randint(0, 9))
    return password


def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'pdf', 'png', 'jpg', 'jpeg', 'gif'}
