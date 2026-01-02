from django.core.management.base import BaseCommand
from django.utils.text import slugify

from products.models import Category, Product


class Command(BaseCommand):
    """Seed the database with sample archive entries."""

    help = "Create sample archive entries for testing and demonstration"

    def handle(self, *args, **options):
        """Execute the seed command."""
        categories_info = {
            "Blood Rites": "Liturgies, bindings, and red alchemy used to seal ancient debts.",
            "Shadow Concord": "Treaties and politics that govern the hidden courts of night.",
            "Sanctum Engineering": "Blueprints for fortresses, reliquaries, and relic containment.",
            "Occult Cartography": "Maps of liminal places where the Archive crosses other realms.",
            "Ancestral Pacts": "Blood oaths forged with forgotten lineages and sleeping patrons.",
            "Elysian Protocols": "Rules of conduct for those who enter the Archive and survive.",
        }

        products_data = [
            {
                "title": "The Blood Atlas of House Morvane",
                "slug": "blood-atlas-of-house-morvane",
                "tagline": "A cartography of every oath sealed in vitae across the empire",
                "description": "House Morvane recorded every pact in ink mixed with their own blood. This atlas charts the web of obligations binding nobles, cults, and mercenary orders to the Archive.",
                "content": "Each parchment is stitched with dried crimson thread. The atlas reveals how blood signatures form constellations when viewed under ember light. Following the paths exposes leverage against any name written within."
                "\n\nRitual Use: Touching a marked name with fresh blood renews the debt for another century, but doing so binds the bearer to carry the weight of the oath until paid.\n\nHazard: Some pages hum softly. Those maps indicate bonds linked to entities that never sleep.",
                "category_name": "Blood Rites",
                "price": "18.50",
                "image_alt": "Ancient atlas illuminated by red candlelight with sigils on parchment",
                "is_featured": True,
            },
            {
                "title": "Midnight Concord: Treaty of Silent Courts",
                "slug": "midnight-concord-silent-courts",
                "tagline": "The secret law that keeps rival houses from tearing the Archive apart",
                "description": "When the Archive risked collapse, the six Silent Courts forged a pact under lunar eclipse. This treaty lists every concession, veto, and blood-price negotiated in whispers.",
                "content": "The Concord is written on obsidian plates. Each clause is mirrored in reverse script, visible only when held before cold fire. Breaking a clause summons the Scrivener, a faceless arbiter who collects repayment in memory instead of coin."
                "\n\nClause Highlights: No court may erase another's archives; disputes must be settled with spectral proxies. The Scrivener may declare Nights of Silence, during which no summons or duel may be issued.\n\nCollector's Note: The plates grow heavier with each broken clause, hinting at debts unpaid.",
                "category_name": "Shadow Concord",
                "price": "17.25",
                "image_alt": "Obsidian treaty plates arranged in a circle over a velvet cloth",
                "is_featured": True,
            },
            {
                "title": "Iron Seraph Manuscript",
                "slug": "iron-seraph-manuscript",
                "tagline": "Blueprints for reliquaries that breathe, bleed, and remember",
                "description": "This manuscript teaches how to forge living vaults that protect relics from thieves and from time itself. Each page folds into a paper automaton to demonstrate the design.",
                "content": "The Seraph pattern uses braided silver veins to circulate oil that mimics blood. When a relic is placed inside, the vault learns its weight and scent. Any uninvited hand triggers a mechanical hymn that freezes limbs with resonance."
                "\n\nUsage: Artisans must inscribe the name of the relic on the vault's inner wing. If a relic is removed without consent, the vault follows, leaving metallic feathers that cut like glass.\n\nWarning: Do not use salt in the oil mixture; the vault will corrode and remember who poisoned it.",
                "category_name": "Sanctum Engineering",
                "price": "19.00",
                "image_alt": "Mechanical wings sketched over blueprints with glowing ink",
                "is_featured": False,
            },
            {
                "title": "Cartographer of Hollow Stars",
                "slug": "cartographer-of-hollow-stars",
                "tagline": "Maps leading to rooms that exist only when the moons align",
                "description": "A set of translucent charts etched with star glass. The maps reveal passages to rooms that surface for a single hour each season, storing contraband lore.",
                "content": "Hold the chart above a flame and watch corridors ink themselves into view. Each Hollow Star room remembers the first word spoken inside it; speaking that word on the next visit unlocks a hidden niche."
                "\n\nTraveler's Note: The rooms are lit by cold fire that preserves parchment. Silence is required—sound fractures the star glass and collapses the passage for a year.\n\nRisk: If two visitors speak different words at once, the room mirrors itself, trapping one visitor in a reflection until dawn.",
                "category_name": "Occult Cartography",
                "price": "16.75",
                "image_alt": "Translucent star maps glowing above a candle flame",
                "is_featured": False,
            },
            {
                "title": "The Oath of Ember Brides",
                "slug": "oath-of-ember-brides",
                "tagline": "Ancestral pact binding firekeepers to the Archive's inner hearths",
                "description": "Seven families vowed to keep the Archive's furnaces alight so the halls would never freeze. This oathbook details the rituals, penalties, and rewards granted to those firebound lineages.",
                "content": "Each chapter pairs a vow with a reward: immunity to smoke-born phantoms, the right to kindle ember keys, and a single request to the Archive's steward once per century."
                "\n\nCost: Breaking the oath extinguishes the family flame for five generations, leaving their homes dark and their names erased from all Archive indexes.\n\nMargin Note: A final blank page waits for a new lineage to swear in blood and soot.",
                "category_name": "Ancestral Pacts",
                "price": "17.90",
                "image_alt": "Leather oathbook beside a furnace glowing with embers",
                "is_featured": False,
            },
            {
                "title": "Mirrorglass Inquisitions",
                "slug": "mirrorglass-inquisitions",
                "tagline": "Interrogations conducted through reflective veils to expose falsehood",
                "description": "Investigators of the Archive once questioned suspects through mirrors filled with moonwater. This dossier preserves their methods and the veils used to detect fractured truths.",
                "content": "The inquisitors spoke behind mirrored veils to prevent sympathy bonds. Moonwater inside the glass rippled when lies touched the air, revealing which words were hollow."
                "\n\nProcedure: Begin with the name of the accused written backward on the veil. Ask only three questions; more risks summoning the echo of the accused's fear, which can linger for days.\n\nResult: Confessions gathered this way are admissible to the Courts of Silence only if the veil remains uncracked by dawn.",
                "category_name": "Shadow Concord",
                "price": "15.99",
                "image_alt": "Silver mirror veil hanging above a basin of moonlit water",
                "is_featured": False,
            },
            {
                "title": "Reliquary of the Ashen Choir",
                "slug": "reliquary-of-the-ashen-choir",
                "tagline": "Songs carved into bone that command the loyalty of watch spirits",
                "description": "The Ashen Choir sang without tongues, carving melodies into relic bone. This reliquary carries their score and the instructions to call the choir to guard a vault.",
                "content": "Bone fragments are arranged in a circle and tapped with iron keys. Each strike releases a sung command that only spirits hear. The melody binds any lingering shades in the room to stand sentinel until sunrise."
                "\n\nSafeguard: Once per month, a keeper must retune the bones with consecrated oil or the choir grows restless and follows visitors home.\n\nReward: Vaults guarded by the choir record every attempted breach as faint harmonies etched into nearby walls.",
                "category_name": "Blood Rites",
                "price": "18.20",
                "image_alt": "Bone circle with etched runes beside iron tuning keys",
                "is_featured": True,
            },
            {
                "title": "Thirteen Doors of Vesper Keep",
                "slug": "thirteen-doors-of-vesper-keep",
                "tagline": "A guide to the sealed rooms that test anyone seeking audience with the Archivist",
                "description": "Before meeting the Archivist, petitioners must pass thirteen doors. Each door poses a different trial: memory, resolve, silence, and debt. This guide describes the sequence and safe responses.",
                "content": "Door One asks for your earliest memory; answer truthfully or the door forgets you. Door Five listens to your heartbeat; calm yourself or be turned around. Door Thirteen mirrors your shadow; step through only when it bows."
                "\n\nTraveler's Advice: Carry salt and a single silver coin. Salt pacifies the rustling between Door Seven and Eight. The coin pays the toll at Door Eleven, where unseen hands count the weight of your promises.\n\nOutcome: Those who pass emerge marked with a subtle sigil granting right of entry for fifty years.",
                "category_name": "Elysian Protocols",
                "price": "19.50",
                "image_alt": "Row of sealed iron doors lit by a single lantern",
                "is_featured": True,
            },
        ]

        created_count = 0
        updated_count = 0

        for data in products_data:
            category_name = data.pop("category_name")
            description = categories_info.get(category_name, "")
            category, _ = Category.objects.get_or_create(
                name=category_name,
                defaults={"slug": slugify(category_name), "description": description},
            )

            data["category"] = category

            product, created = Product.objects.update_or_create(
                slug=data["slug"], defaults=data
            )
            if created:
                created_count += 1
            else:
                updated_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Seed completed. Created {created_count} archives and updated {updated_count} entries."
            )
        )
