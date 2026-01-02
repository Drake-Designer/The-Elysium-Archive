from django.core.management.base import BaseCommand
from products.models import Product


class Command(BaseCommand):
    """Seed the database with sample archive entries."""

    help = "Create sample archive entries for testing and demonstration"

    def handle(self, *args, **options):
        """Execute the seed command."""
        # Check if products already exist to avoid duplicates
        if Product.objects.exists():
            self.stdout.write(
                self.style.WARNING("Archive entries already exist. Skipping seed.")
            )
            return

        # Sample products inspired by Bloodlines: The Masquerade - Clan Archives
        products_data = [
            # CLAN ARCHIVES SECTION (10 products)
            {
                "title": "The Brujah Chronicles: Strength and Rebellion",
                "slug": "brujah-chronicles-strength-rebellion",
                "tagline": "Warrior philosophers who defy authority and embrace raw power",
                "description": "The archive of the Brujah clan reveals the fierce legacy of the ancient warriors who refuse to bow to anyone. Masters of combat and physical prowess, they are the rebels of Camarilla society.",
                "content": "The Brujah are descended from the ancient warrior caste, warriors who were embraced by Caine himself. Their blood runs hot with the hunger for combat and dominion. In ancient times, the Brujah were philosophers and generals. In the modern nights, they are street fighters and revolutionaries.\n\nDisciplines: Celerity allows enhanced speed beyond mortal comprehension. Potence grants superhuman strength. Fortitude provides unnatural endurance and resilience.\n\nThe Brujah Weakness: All Brujah suffer from a violent temper and struggle with containing their rage. Even minor insults can trigger berserker rages that cause them to lose control.\n\nFamous Brujah: Brujah Justicars have hunted Elders for centuries. The clan produced some of the greatest generals in human history before the Embrace.",
                "category": "Clans",
                "price": "16.99",
                "image_alt": "Muscular figure in combat stance with glowing red eyes, urban background",
                "is_featured": True,
            },
            {
                "title": "The Tremere Grimoire: Blood Sorcery Unveiled",
                "slug": "tremere-grimoire-blood-sorcery",
                "tagline": "Arcane masters who bend reality through forbidden blood magic",
                "description": "The Tremere are the sorcerers of the vampire world, wielding powers that defy natural law. This grimoire contains the secrets of their blood sorcery arts and their mysterious origins.",
                "content": "The Tremere are unique among the clans: they were originally mortal mages who sought immortality through sacrifice and dark rituals. United House Tremere rules from the Vienna Chantry, orchestrating vampire politics from the shadows.\n\nDisciplines: Auspex grants psychic awareness and supernatural perception. Celerity provides supernatural speed. Thaumaturgy is their signature discipline, allowing control over blood itself and the forces of magic.\n\nThe Tremere Weakness: All Tremere carry a blood curse that causes them to be enslaved to their Elders through the hierarchy of their House. True free will is impossible for those of Tremere blood.\n\nSecret Knowledge: The origins of House Tremere trace back to the Order of Hermes, and their blood magic draws from sources older than the Camarilla itself.",
                "category": "Clans",
                "price": "19.99",
                "image_alt": "Magical circle with blood runes glowing in darkness",
                "is_featured": True,
            },
            {
                "title": "The Toreador Archives: Beauty, Art, and Damnation",
                "slug": "toreador-archives-beauty-art",
                "tagline": "Refined aesthetes obsessed with beauty, passion, and creation",
                "description": "The Toreador are the artists and sensualists of the vampire world, forever cursed to appreciate beauty while spreading darkness. This archive documents their greatest works and deepest passions.",
                "content": "The Toreador are the clan of passion and beauty. They are patrons of the arts, creators of masterpieces, and deadly seducers. Many of history's greatest artists, musicians, and lovers were secretly Toreador, their works immortalized for eternity.\n\nDisciplines: Auspex grants supernatural awareness and perception. Celerity provides enhanced speed. Presence allows them to inspire or terrify through sheer force of personality.\n\nThe Toreador Weakness: All Toreador suffer from a paralyzing fascination with beauty. Faced with anything truly beautiful, they become transfixed and unable to act. This weakness has caused the downfall of many.\n\nLegacy: The Toreador have produced some of history's most celebrated artists. Many masterpieces hanging in the world's finest museums were created by Toreador hands.",
                "category": "Clans",
                "price": "17.50",
                "image_alt": "Renaissance painting of ethereal figure surrounded by golden light and rose petals",
                "is_featured": True,
            },
            {
                "title": "The Ventrue Code: Lords of Commerce and Empire",
                "slug": "ventrue-code-lords-commerce",
                "tagline": "Natural rulers who command wealth, influence, and absolute authority",
                "description": "The Ventrue are the elder statesmen of vampire society, the clan of kings and merchant princes. They rule the Camarilla through wealth and political maneuvering, their influence extending into every level of mortal society.",
                "content": "The Ventrue are born leaders and natural aristocrats. Descended from the royal houses of Europe, they claim dominion over the organization and direction of Camarilla society. Most Princes are Ventrue. Most Camarilla laws favor their interests.\n\nDisciplines: Fortitude grants enhanced endurance and resilience. Presence allows command and inspiration of others. Dominate grants control over the wills of lesser beings.\n\nThe Ventrue Weakness: All Ventrue have strict dietary restrictions. Each Ventrue can only feed from one specific type of blood, a limitation that varies from individual to individual. Some feed only on aristocrats, others only on virgins, others only on specific professions.\n\nPolitical Control: The Ventrue effectively control the Camarilla inner circle. The Justicars who enforce law, the Archons who hunt threats, and the leaders of every major city are predominantly Ventrue.",
                "category": "Clans",
                "price": "18.75",
                "image_alt": "Aristocratic figure in royal attire seated on throne of black marble and gold",
                "is_featured": True,
            },
            {
                "title": "The Nosferatu Codex: Beasts in the Shadows",
                "slug": "nosferatu-codex-beasts-shadows",
                "tagline": "Hideous creatures whose very appearance breaks the Masquerade",
                "description": "The Nosferatu are cursed with unnatural deformity, their monstrous forms forever barring them from mortal society. Yet in their hideous forms lies extraordinary power and ancient wisdom.",
                "content": "The Nosferatu are marked by the blood curse of their antediluvian progenitor. All Nosferatu are hideously deformed, bearing bestial features that mark them as demons to human eyes. They are the clan of shadows, sewers, and forgotten places.\n\nDisciplines: Potence grants superhuman strength. Obfuscate allows them to fade from perception and become invisible. Animalism grants command over rats and other vermin.\n\nThe Nosferatu Weakness: All Nosferatu suffer from terrible physical deformity that makes them instantly recognizable as inhuman. They cannot appear human no matter how carefully they dress or present themselves. This curse drives many to madness or despair.\n\nHidden Strengths: The Nosferatu have created a vast network of tunnels and hidden places beneath major cities. They control information flow through whispers and shadows. Many elder Nosferatu have lived for centuries unseen.",
                "category": "Clans",
                "price": "16.50",
                "image_alt": "Monstrous figure in sewers surrounded by rats and shadows",
                "is_featured": False,
            },
            {
                "title": "The Gangrel Howl: Beasts of the Wild",
                "slug": "gangrel-howl-beasts-wild",
                "tagline": "Feral nomads who command the animal world and savage fury",
                "description": "The Gangrel are the untamed clan, animalistic and independent, more beast than man. They roam the wilderness and the outskirts of civilization, commanding the animal world.",
                "content": "The Gangrel are the outcasts who reject Camarilla conventions and city life. They are the wandering hunters, the tribal elders, the primal force of nature given immortal form. They claim descent from the ancient druids and shamans of prehistory.\n\nDisciplines: Animalism grants control over beasts and creatures of the wild. Fortitude provides enhanced endurance. Protean allows transformation into animal forms and elements.\n\nThe Gangrel Weakness: All Gangrel gradually lose their humanity and develop animalistic features with each beast form they assume. Over centuries, many Gangrel become more beast than vampire, losing their morality and human nature.\n\nIndependence: The Gangrel famously rejected the Camarilla in recent nights, declaring themselves independent. Many actively oppose Camarilla authority, making them dangerous wildcards in vampire politics.",
                "category": "Clans",
                "price": "17.25",
                "image_alt": "Feral figure surrounded by wolves in moonlit forest",
                "is_featured": False,
            },
            {
                "title": "The Malkavian Visions: Madness and Prophecy",
                "slug": "malkavian-visions-madness-prophecy",
                "tagline": "Insane visionaries cursed with terrible truths and fractured minds",
                "description": "The Malkavian are all cursed with madness, yet within their delusion lies prophetic insight and hidden truths. They see the world through fractured lenses that reveal what sane minds cannot perceive.",
                "content": "Every Malkavian shares a unique bond: all members of the clan are insane. This is not a weakness they fight but a blessing that grants them insight into truth beyond mortal comprehension. Malkavians are prophets and seers, their ravings containing kernels of absolute truth.\n\nDisciplines: Auspex grants supernatural perception. Dementation is their signature discipline, allowing them to inflict madness or grant visions. Obfuscate allows them to hide and deceive.\n\nThe Malkavian Weakness: All Malkavians are eternally insane. Each member of the clan suffers from a unique form of madness that shapes their entire existence. Some are catatonic, others are violently delusional.\n\nProphetic Power: Malkavian prophecies are never clear, but they are always accurate in some way. Many Camarilla Princes consult with Malkavian advisors despite their seeming madness, trusting in their hidden wisdom.",
                "category": "Clans",
                "price": "18.50",
                "image_alt": "Unhinged figure surrounded by fractured mirrors and symbols",
                "is_featured": False,
            },
            {
                "title": "The Caitiff Testament: Clanless and Outcast",
                "slug": "caitiff-testament-clanless-outcast",
                "tagline": "Those without clan, lacking discipline and heritage, rejected by all",
                "description": "The Caitiff are vampires without clan affiliation, outcastes who lack the prestigious bloodlines of the great clans. They are seen as inferior, unworthy, yet many have proven themselves formidable.",
                "content": "Caitiff are thin-bloods and failures, vampires who lack connection to the great antediluvians. They were often embraced by lesser vampires or embraced by mistake. The Camarilla views them as less than fully vampire, lesser beings without clan protection or heritage.\n\nDisciplines: Caitiff lack specific discipline specialties and instead learn general vampire arts. They have access to a broader range of disciplines but rarely master any.\n\nThe Caitiff Weakness: All Caitiff lack true discipline mastery and clan identity. They are not recognized as full members of vampire society and receive no protection from clan laws or traditions. They stand alone.\n\nUnderdogs: Many Caitiff compensate for lack of heritage through cunning, determination, and improvisation. Some of the greatest vampire hunters and rebels have been Caitiff who rose above their station.",
                "category": "Clans",
                "price": "15.99",
                "image_alt": "Solitary figure standing alone in rain, watched from shadows",
                "is_featured": False,
            },
            {
                "title": "The Giovanni Mysteries: Necromancy and Family Darkness",
                "slug": "giovanni-mysteries-necromancy-family",
                "tagline": "Merchant princes who command death itself and guard terrible secrets",
                "description": "The Giovanni are a family clan of necromancers, controlling vast commercial empires while practicing forbidden death magic. They are united by blood ties and dark rituals that bind them to their Antediluvian.",
                "content": "The Giovanni are unique among clans: they are a single extended family, all descended from Giovanni the Maltese. They are merchant princes who control shipping, banking, and commerce across the globe. They are also necromancers who have mastered the arts of death magic.\n\nDisciplines: Celerity provides enhanced speed. Potence grants strength. Necromancy is their signature discipline, allowing control over death, spirits, and the dead.\n\nThe Giovanni Weakness: All Giovanni are bound by blood oath to serve the Giovanni family interests. They cannot refuse orders from family superiors. The clan is rife with internal politics and Byzantine power structures.\n\nSecret Allegiance: Many suspect the Giovanni secretly serve a different master than the Camarilla, with loyalties extending far beyond the organization of the undead. The truth of their true allegiance remains hidden.",
                "category": "Clans",
                "price": "19.50",
                "image_alt": "Merchant in opulent setting with ghostly figures surrounding them",
                "is_featured": False,
            },
            {
                "title": "The Assamite Legends: Assassins and Blood Sorcerers",
                "slug": "assamite-legends-assassins-blood",
                "tagline": "Ancient blood sorcerers bound by oath to the Camarilla through chains of magic",
                "description": "The Assamite are legendary assassins from the Middle East, bound by blood oath to the Camarilla. They are masterful warriors and sorcerers, feared throughout the vampire world for their deadly efficiency.",
                "content": "The Assamite were originally the enemies of the Camarilla, a powerful clan that resisted European vampire dominance. In recent nights, the Camarilla placed an unbreakable blood curse on all Assamite that prevents them from killing Camarilla vampires. This ancient curse has bound the proud clan into servitude.\n\nDisciplines: Celerity grants enhanced speed. Obfuscate allows invisibility and deception. Quietus is their signature discipline, granting blood sorcery and mastery over death.\n\nThe Assamite Weakness: All Assamite are magically bound by blood oath to the Camarilla, unable to harm even the lowest Camarilla member. This curse is absolute and cannot be broken. The proud clan is enslaved by magical compulsion.\n\nAncient Rivalry: The Assamite once ruled vast territories in North Africa and the Middle East. The Camarilla's subjugation of the Assamite represents one of the greatest political victories in Camarilla history.",
                "category": "Clans",
                "price": "18.99",
                "image_alt": "Shadowy figure in Middle Eastern setting with curved blade and mystical symbols",
                "is_featured": True,
            },
            # MISCELLANEOUS ARCHIVES SECTION (10 products)
            {
                "title": "Sabbat Doctrines: The Path of Caine",
                "slug": "sabbat-doctrines-path-of-caine",
                "tagline": "The heretical teachings of vampire rebels who reject Camarilla authority",
                "description": "The Sabbat represent an alternative path for vampires, rejecting Camarilla laws and embracing their bestial nature. This archive contains their dark doctrines and revolutionary manifestos.",
                "content": "The Sabbat are the Camarilla's greatest enemy, a movement of vampires who reject the Masquerade and refuse to hide their true nature. They embrace the curse of Caine and see vampires as the apex of existence, superior to all creatures.\n\nCore Beliefs: The Sabbat believes the Masquerade is a cage. They practice ritus and ceremony to celebrate their nature. They seek to awaken the Antediluvians and bring about a new age of vampire supremacy.\n\nOrganization: Unlike the Camarilla's formal hierarchy, the Sabbat operates through packs, small groups bonded by blood ritual and shared purpose. Packs often operate independently, creating a decentralized and unpredictable threat.\n\nHeresy: The Camarilla considers Sabbat knowledge heretical. Possession of Sabbat documents can result in Final Death. Yet many vampires are fascinated by the Sabbat alternative, wondering if the Camarilla's way is truly the only path.",
                "category": "Factions",
                "price": "17.75",
                "image_alt": "Chaotic ritual scene with fire and symbols in underground cavern",
                "is_featured": True,
            },
            {
                "title": "The Masquerade Maintenance Manual",
                "slug": "masquerade-maintenance-manual",
                "tagline": "Practical guide to maintaining the deception that hides the supernatural",
                "description": "A comprehensive manual for maintaining the Masquerade in the modern world. Detailed techniques for avoiding detection, managing witnesses, and covering tracks in an age of surveillance.",
                "content": "The Masquerade is more fragile than ever. Security cameras, DNA testing, social media networks, and instant communication have made maintaining the deception exponentially harder.\n\nChapter One: Digital Footprints\nCreating believable online personas, maintaining consistent false identities across platforms, and avoiding digital traceability. Methods for hacking security systems and erasing digital evidence.\n\nChapter Two: Witness Management\nHandling accidental witnesses range from memory manipulation to far more permanent solutions. The ethics of witness elimination versus containment discussed from practical perspective.\n\nChapter Three: Feeding in the Modern Age\nHuman disappearances are now investigated with scientific rigor. This section covers feeding methods that minimize detection risk while satisfying the Beast's hunger.\n\nChapter Four: Law Enforcement Evasion\nUnderstanding how police investigate crimes, using technology against investigators, and knowing when to hide versus when to act.",
                "category": "Survival",
                "price": "16.99",
                "image_alt": "Computer screens showing surveillance footage and digital traces",
                "is_featured": False,
            },
            {
                "title": "Gehenna Prophesies: The Final Night Approaches",
                "slug": "gehenna-prophesies-final-night",
                "tagline": "Ancient prophecies of the world's end and the return of the Antediluvians",
                "description": "Gehenna is the prophesied end times when the Antediluvians awaken and bring about the final night. This archive contains ancient prophecies, interpretations, and warning signs.",
                "content": "Gehenna is not a distant threat. Signs suggest the Final Night draws near. Antediluvians who have slept for millennia are stirring. The barriers between the spirit world and material world weaken. Ancient vampires grow in power while younger generations struggle.\n\nWarning Signs: Increased appearance of Caitiff and thin-bloods suggests the Embrace is weakening. Unusual animal behavior suggests the spirit world intrudes. Earthquakes in traditionally stable regions suggest the earth itself reacts to coming change.\n\nAntediluvian Theories: Each clan's Antediluvian is said to manifest different apocalyptic signs. Caine himself may walk the earth again. Some theorists believe Gehenna has already begun, merely taking a form no one recognizes.\n\nSurvival Strategies: Gehenna cannot be prevented, only survived. This section covers how individual vampires might preserve themselves through the final night when all human civilization crumbles.",
                "category": "Prophecy",
                "price": "18.50",
                "image_alt": "Apocalyptic vision with ruins and ominous red sky",
                "is_featured": False,
            },
            {
                "title": "The Camarilla Hierarchy: Power Structure Exposed",
                "slug": "camarilla-hierarchy-power-structure",
                "tagline": "The invisible empire that rules the vampire world through law and politics",
                "description": "An insider's guide to the Camarilla structure, the Secret Societies that control it, and how power truly flows through the vampire underworld.",
                "content": "The Camarilla presents itself as an organization of law and order, but the truth is far more complex. Multiple secret societies operate within the Camarilla, each with their own agenda.\n\nThe Primogen Council: In each city, the Primogen Council consists of representatives from each clan. In theory, they advise the Prince. In practice, they compete for advantage.\n\nThe Justicars: The Camarilla's enforcers, Justicars are ancient vampires empowered to hunt down threats to Camarilla security. They answer to no Prince, only to the Inner Circle.\n\nThe Inner Circle: The true power of the Camarilla, the Inner Circle consists of the most ancient and powerful vampires, most of Ventrue clan. They meet in secret and make decisions that affect all vampire-kind.\n\nSecret Agendas: Every member of the hierarchy pursues personal agendas while serving the Camarilla. Personal power, clan dominance, and factional advantage drive all decisions.",
                "category": "Politics",
                "price": "19.25",
                "image_alt": "Ornate council chamber with shadowy figures in discussion",
                "is_featured": True,
            },
            {
                "title": "Chronicles of the Vampire Wars",
                "slug": "chronicles-vampire-wars",
                "tagline": "History of conflicts between vampire factions spanning centuries",
                "description": "Documentation of the great wars between vampire factions: Camarilla versus Sabbat, Anarch versus Established Order, and the conflicts that shaped the modern vampire world.",
                "content": "The War of the Princes, 1940-1960: As vampires emerged in greater numbers and cities grew crowded, territorial disputes erupted into open conflict. The Camarilla struggled to maintain order as younger vampires challenged established Princes.\n\nThe Anarch Revolt, 1960-1980: Young vampires demanded independence and democratic representation. The Camarilla's response was brutal suppression, creating a permanent underclass of rebellious vampires.\n\nThe Sabbat Crusades, 1970-1990: As the Sabbat grew in power, they launched coordinated attacks on Camarilla territories. Entire cities fell. The Camarilla fought desperately to contain the Sabbat threat.\n\nModern Tensions: The vampire world remains unstable. Camarilla power weakens as age-old structures crumble. The Sabbat repositions. Anarchs grow bolder. A new vampire war may be inevitable.",
                "category": "History",
                "price": "17.50",
                "image_alt": "Medieval battle scene reimagined with vampires in modern setting",
                "is_featured": False,
            },
            {
                "title": "The Anarch Free States: Revolution and Rebellion",
                "slug": "anarch-free-states-revolution-rebellion",
                "tagline": "Documents of the vampire resistance movement fighting against tyranny",
                "description": "The Anarch movement represents vampire rebellion against Camarilla oppression. This archive contains manifestos, tactical guides, and revolutionary doctrine.",
                "content": "The Anarchs are young vampires who rejected the Camarilla's hierarchical control. They established free states where vampires govern themselves through consensus rather than autocratic rule.\n\nAnarch Principles: Freedom from ancient tyranny. Equality among vampires regardless of age or power. Decentralized governance through consensus. The right to refuse orders from Elders.\n\nFamous Anarch Leaders: Nines Rodriguez of Los Angeles led the most successful Anarch free state. His charisma and tactical genius created a functioning alternative to Camarilla rule.\n\nThe Camarilla Response: The Camarilla views Anarchs as dangerous revolutionaries threatening the established order. Many Camarilla Princes have declared war on Anarch settlements.\n\nRecent Developments: Some Anarchs have begun cooperating with each other, suggesting an Anarch Nation might be forming. This threatens both Camarilla and Sabbat interests.",
                "category": "Factions",
                "price": "16.75",
                "image_alt": "Graffiti-covered walls with revolutionary symbols and gathering crowds",
                "is_featured": False,
            },
            {
                "title": "Bloodline Secrets: The Hidden Clans Revealed",
                "slug": "bloodline-secrets-hidden-clans",
                "tagline": "Records of the minor bloodlines that hide in the shadows of vampire society",
                "description": "Not all vampires belong to the Great Clans. Lesser bloodlines, heresies, and secret societies operate in the shadows, their true natures concealed from most of vampire-kind.",
                "content": "Beyond the ten Great Clans exist other vampire bloodlines, some ancient and powerful, others recent offshoots of greater lines.\n\nThe Gargoyles: Created as servants by the Tremere, Gargoyles are now free from their masters but still bear the curse of enslavement in their blood.\n\nThe Daughters of Cacophony: Vampire musicians who claim connection to mystical frequencies that predate human history. They maintain their own society separate from Camarilla.\n\nThe Wan: Ethereal vampires who exist partially in the spirit world. Some claim they are the true original vampires, preceding even the Antediluvians.\n\nThin-Bloods: The weakest vampires, Thin-bloods are barely more powerful than humans but often creative and resourceful in compensation.\n\nThe Panders: Vampires without clear clan affiliation, often embraced through mistake or chaos. They form their own communities and cultures.",
                "category": "Lore",
                "price": "17.99",
                "image_alt": "Silhouettes of mysterious figures in various poses against abstract background",
                "is_featured": False,
            },
            {
                "title": "The Second Inquisition: Modern Hunters and Their Methods",
                "slug": "second-inquisition-modern-hunters",
                "tagline": "Documentation of mortal agencies hunting and exterminating vampires",
                "description": "The Second Inquisition is real. Government agencies, religious organizations, and secret societies have organized to hunt and destroy vampires. This archive documents their methods and capabilities.",
                "content": "The hunter threat has evolved beyond amateur vampire slayers. Modern enemies are trained, equipped, and coordinated.\n\nUS Government Programs: The FBI maintains classified files on vampire activity. Certain black ops divisions are authorized to execute vampires operating on American soil.\n\nVatican's Shadow: The Catholic Church has maintained vampire-hunting traditions for centuries. Modern Vatican intelligence agencies continue this work in secret.\n\nMilitary Applications: Vampires have been identified and catalogued by military intelligence agencies worldwide. Some nations actively recruit vampire soldiers for special operations.\n\nTech Companies: Silicon Valley billionaires fund vampire research, developing technological countermeasures. UV weapons, GPS tracking, and surveillance systems specifically designed to detect and contain vampires.\n\nGrowing Threat: The Second Inquisition grows stronger each year. Vampire losses mount. The balance of power between hunter and hunted shifts dangerously.",
                "category": "Threats",
                "price": "18.75",
                "image_alt": "High-tech surveillance facility with maps and targeting systems",
                "is_featured": True,
            },
            {
                "title": "Beast Within: The Struggle Against Frenzy and Hunger",
                "slug": "beast-within-frenzy-hunger",
                "tagline": "Psychological guide to resisting the animal nature within all vampires",
                "description": "Every vampire carries the Beast, an animalistic hunger and rage that grows stronger with age. This archive documents the psychological struggle and methods of maintaining humanity.",
                "content": "The Beast is not a separate entity but an inherent part of vampire nature. It grows stronger with every night of existence, constantly hungry, constantly violent, constantly demanding.\n\nFrenzy: When the Beast takes control, a vampire enters frenzy, a state of berserker rage where they lose all human rationality. A frenzied vampire is a killing machine, unstoppable until sated.\n\nHumanity: The only defense against the Beast is Humanity, a vampire's connection to their former mortal self. As Humanity diminishes, the Beast grows stronger.\n\nThe Cycle: With each act of violence, each kill, each feeding, a vampire loses Humanity. Eventually, even the most moral vampires become monsters. This is not punishment but inevitable decay.\n\nSurvival Strategies: Methods for maintaining Humanity through philosophy, morality, and discipline. Accepting the Beast rather than fighting it. Embracing the nature of predator.",
                "category": "Philosophy",
                "price": "16.50",
                "image_alt": "Tormented figure with shadow and light playing across anguished face",
                "is_featured": False,
            },
            {
                "title": "The Crimson Gutter: Street Vampire Survival",
                "slug": "crimson-gutter-street-vampire-survival",
                "tagline": "Tales of survival for vampires living on the margins of society",
                "description": "Life on the streets for a vampire is brutal, dangerous, and often short. This archive documents survival strategies for those who exist outside clan protection and organized vampire society.",
                "content": "Street vampires, Caitiff, thin-bloods, and exiled clan members must survive without the protection of formal vampire society. They live in abandoned buildings, subway tunnels, and forgotten places.\n\nFinding Food Without Clan Support: Hunting alone requires different techniques than hunting in organized groups. Smaller meals taken carefully, hunting in unfamiliar territories to avoid territorial conflicts.\n\nAvoiding Hunters: Street vampires are vulnerable to both vampire hunters and other predatory vampires. This section covers defensive techniques, safe houses, and escape routes in various urban environments.\n\nBuilding Alliances: Many street vampires form small packs for mutual protection and hunting advantages. Alliances built on survival rather than bloodline or clan affiliation.\n\nRising From the Gutter: Some street vampires eventually rise to power and influence. Their lack of clan restrictions allows them freedom that might be impossible for their more privileged cousins.",
                "category": "Survival",
                "price": "15.50",
                "image_alt": "Gritty urban street scene at night with vampire figures in shadows",
                "is_featured": False,
            },
        ]

        # Create products in database
        created_count = 0
        for data in products_data:
            product, created = Product.objects.get_or_create(
                slug=data["slug"], defaults=data
            )
            if created:
                created_count += 1

        self.stdout.write(
            self.style.SUCCESS(f"Successfully created {created_count} archive entries")
        )
