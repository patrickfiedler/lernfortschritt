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


def generate_credentials_pdf(students, klasse_name):
    """Generate a PDF with student credentials.

    Args:
        students: List of dicts with 'nachname', 'vorname', 'username', 'password'
        klasse_name: Name of the class

    Returns:
        BytesIO object containing the PDF
    """
    from io import BytesIO
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from datetime import datetime

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=2*cm, bottomMargin=2*cm)
    elements = []
    styles = getSampleStyleSheet()

    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=12
    )
    elements.append(Paragraph(f"Zugangsdaten: {klasse_name}", title_style))
    elements.append(Paragraph(f"Erstellt am {datetime.now().strftime('%d.%m.%Y %H:%M')}", styles['Normal']))
    elements.append(Spacer(1, 0.5*cm))

    # Warning
    warning_style = ParagraphStyle(
        'Warning',
        parent=styles['Normal'],
        textColor=colors.red,
        fontSize=10
    )
    elements.append(Paragraph(
        "VERTRAULICH - Diese Zugangsdaten sicher aufbewahren und nach Verteilung vernichten!",
        warning_style
    ))
    elements.append(Spacer(1, 0.5*cm))

    # Table header
    data = [['Name', 'Benutzername', 'Passwort']]

    # Table rows
    for s in students:
        data.append([
            f"{s['nachname']}, {s['vorname']}",
            s['username'],
            s['password']
        ])

    # Create table
    table = Table(data, colWidths=[8*cm, 5*cm, 4*cm])
    table.setStyle(TableStyle([
        # Header
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        # Body
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ALIGN', (1, 1), (-1, -1), 'LEFT'),
        ('FONTNAME', (1, 1), (2, -1), 'Courier'),  # Monospace for credentials
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        # Grid
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        # Alternating row colors
        *[('BACKGROUND', (0, i), (-1, i), colors.Color(0.95, 0.95, 0.95))
          for i in range(2, len(data), 2)]
    ]))

    elements.append(table)
    elements.append(Spacer(1, 1*cm))

    # Footer
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.grey
    )
    elements.append(Paragraph(
        f"Anzahl Schueler: {len(students)} | Lernmanager",
        footer_style
    ))

    doc.build(elements)
    buffer.seek(0)
    return buffer
