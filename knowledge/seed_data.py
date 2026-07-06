"""Seed data for the chess theory knowledge base."""


def get_seed_documents() -> list[dict]:
    """Return all seed documents for the chess theory collection."""
    documents = [
        # =====================================================================
        # OPENING PRINCIPLES (~15 documents)
        # =====================================================================
        {
            "id": "opening_center_control",
            "content": "Controlling the center with pawns (e4, d4) gives your pieces more mobility and restricts your opponent's options. A strong pawn center supports knight outposts and opens lines for bishops. However, a pawn center can become a target if not properly supported — always ensure your central pawns are defended.",
            "metadata": {
                "category": "opening",
                "subcategory": "center_control",
                "difficulty": "beginner",
                "title": "Center Control",
            },
        },
        {
            "id": "opening_development",
            "content": "Develop your minor pieces (knights and bishops) quickly in the opening before moving the same piece twice or launching premature attacks. Knights are generally best developed toward the center (Nf3, Nc3, Nf6, Nc6) where they control the most squares. Each move should contribute to piece activity, center control, or king safety.",
            "metadata": {
                "category": "opening",
                "subcategory": "development",
                "difficulty": "beginner",
                "title": "Piece Development",
            },
        },
        {
            "id": "opening_king_safety",
            "content": "Castling early — usually within the first 10 moves — is essential for king safety and rook activation. Kingside castling is generally safer because fewer pawns are disturbed, but queenside castling can be effective in aggressive setups. Avoid moving pawns in front of your castled king without a concrete reason, as this weakens the king's shelter.",
            "metadata": {
                "category": "opening",
                "subcategory": "king_safety",
                "difficulty": "beginner",
                "title": "King Safety and Castling",
            },
        },
        {
            "id": "opening_tempo",
            "content": "A tempo is a unit of time measured in moves. Gaining a tempo means achieving the same position with one fewer move, often by developing with threats. Losing tempi by moving pieces multiple times in the opening or making unnecessary pawn moves allows your opponent to seize the initiative. In open positions, a single tempo can be the difference between attacking and defending.",
            "metadata": {
                "category": "opening",
                "subcategory": "tempo",
                "difficulty": "intermediate",
                "title": "Tempo in the Opening",
            },
        },
        {
            "id": "opening_italian_game",
            "content": "The Italian Game (1.e4 e5 2.Nf3 Nc6 3.Bc4) aims for rapid development and pressure on f7. White's plan often involves d3 followed by c3 and d4, building a strong center. The Giuoco Piano variation leads to rich middlegame play where both sides have chances, while the Evans Gambit (4.b4) sacrifices a pawn for rapid development and attacking prospects.",
            "metadata": {
                "category": "opening",
                "subcategory": "italian_game",
                "difficulty": "beginner",
                "title": "Italian Game",
            },
        },
        {
            "id": "opening_sicilian_defense",
            "content": "The Sicilian Defense (1.e4 c5) is Black's most aggressive and popular response to 1.e4, creating an asymmetric pawn structure from the start. Black trades a c-pawn for White's e-pawn, gaining a queenside pawn majority and the semi-open c-file. White typically gets attacking chances on the kingside, especially in the Open Sicilian (2.Nf3 and 3.d4), while Black counterattacks on the queenside — this imbalance leads to dynamic, combative play.",
            "metadata": {
                "category": "opening",
                "subcategory": "sicilian_defense",
                "difficulty": "intermediate",
                "title": "Sicilian Defense Overview",
            },
        },
        {
            "id": "opening_french_defense",
            "content": "The French Defense (1.e4 e6) leads to solid but somewhat cramped positions for Black. After 2.d4 d5, the central tension creates clear strategic plans: White often advances e5 to gain space and attack on the kingside, while Black counterattacks with ...c5 against the d4 pawn and seeks play on the queenside. Black's light-squared bishop is often restricted by the e6 pawn and finding an active role for it is a key challenge.",
            "metadata": {
                "category": "opening",
                "subcategory": "french_defense",
                "difficulty": "intermediate",
                "title": "French Defense",
            },
        },
        {
            "id": "opening_caro_kann",
            "content": "The Caro-Kann Defense (1.e4 c6) is a solid and reliable choice for Black, aiming for ...d5 on the next move with pawn support. Unlike the French Defense, Black's light-squared bishop remains unblocked and can develop actively to f5 or g4. The Caro-Kann typically leads to sound, strategic positions where Black has fewer weaknesses but must play accurately to equalize.",
            "metadata": {
                "category": "opening",
                "subcategory": "caro_kann",
                "difficulty": "beginner",
                "title": "Caro-Kann Defense",
            },
        },
        {
            "id": "opening_ruy_lopez",
            "content": "The Ruy Lopez (1.e4 e5 2.Nf3 Nc6 3.Bb5) is one of the oldest and most respected openings, putting immediate pressure on the knight that defends e5. White's long-term plan often involves building a strong center with c3 and d4 while maintaining the bishop pair. The Closed Ruy Lopez leads to deep strategic battles where both sides maneuver for advantages over many moves, making understanding pawn structures and piece placement critical.",
            "metadata": {
                "category": "opening",
                "subcategory": "ruy_lopez",
                "difficulty": "intermediate",
                "title": "Ruy Lopez",
            },
        },
        {
            "id": "opening_queens_gambit",
            "content": "The Queen's Gambit (1.d4 d5 2.c4) is not a true gambit since Black cannot hold the pawn without making concessions. White aims to establish a strong center and gain space. In the Queen's Gambit Declined (2...e6), Black gets a solid but slightly passive position, while the Queen's Gambit Accepted (2...dxc4) gives Black freedom at the cost of temporarily conceding the center. The Slav Defense (2...c6) is a popular alternative that supports d5 while keeping the light-squared bishop unblocked.",
            "metadata": {
                "category": "opening",
                "subcategory": "queens_gambit",
                "difficulty": "beginner",
                "title": "Queen's Gambit",
            },
        },
        {
            "id": "opening_english",
            "content": "The English Opening (1.c4) is a flexible system that can transpose into many d4 openings or maintain its own character. White controls d5 from the flank and often fianchettoes the king's bishop to g2. The English suits players who prefer strategic battles and are comfortable navigating transpositions, as the pawn on c4 can support many different setups depending on Black's response.",
            "metadata": {
                "category": "opening",
                "subcategory": "english_opening",
                "difficulty": "intermediate",
                "title": "English Opening",
            },
        },
        {
            "id": "opening_avoid_traps",
            "content": "In the opening, avoid grabbing pawns at the cost of development or king safety. Many opening traps exploit greed — for example, the poisoned pawn in the Sicilian Najdorf or Scholar's Mate attempts. Before capturing a pawn, always check whether your opponent gets dangerous development, open lines toward your king, or a lasting initiative in return.",
            "metadata": {
                "category": "opening",
                "subcategory": "opening_traps",
                "difficulty": "beginner",
                "title": "Avoiding Opening Traps",
            },
        },
        {
            "id": "opening_pawn_structure_choice",
            "content": "Your opening choice largely determines the pawn structure for the rest of the game. Symmetric structures (e.g., from the Exchange variation of many openings) tend to lead to equal, drawish positions, while asymmetric structures create imbalances and winning chances for both sides. Choose openings whose resulting pawn structures match your playing style — dynamic players may prefer the Sicilian, while solid players may prefer the Caro-Kann.",
            "metadata": {
                "category": "opening",
                "subcategory": "pawn_structure_choice",
                "difficulty": "intermediate",
                "title": "Pawn Structure and Opening Choice",
            },
        },
        {
            "id": "opening_connect_rooks",
            "content": "A key milestone in the opening is connecting your rooks, meaning all minor pieces and the queen have moved off the back rank. Once rooks are connected, they can support each other and contest open files. If you have connected rooks and your opponent does not, you typically have a significant development advantage that should be exploited before they catch up.",
            "metadata": {
                "category": "opening",
                "subcategory": "rook_connection",
                "difficulty": "beginner",
                "title": "Connecting the Rooks",
            },
        },
        {
            "id": "opening_hypermodern",
            "content": "Hypermodern openings (like the King's Indian, Nimzo-Indian, and Grunfeld) challenge the classical idea that the center must be occupied by pawns. Instead, Black allows White to build a pawn center and then undermines it with piece pressure and pawn strikes like ...c5 or ...e5. These openings require precise timing and deep understanding of when to strike the center, but can lead to dynamic positions with clear counterplay.",
            "metadata": {
                "category": "opening",
                "subcategory": "hypermodern",
                "difficulty": "intermediate",
                "title": "Hypermodern Opening Ideas",
            },
        },
        # =====================================================================
        # TACTICAL MOTIFS (~15 documents)
        # =====================================================================
        {
            "id": "tactic_pin",
            "content": "A pin occurs when an attacking piece targets a less valuable piece that is shielding a more valuable piece behind it. The pinned piece cannot move without exposing the piece behind it (absolute pin against the king) or should not move without losing material (relative pin). Pins are most effective when the pinned piece cannot be defended or when you can pile up attackers on the pinned piece to win material.",
            "metadata": {
                "category": "tactic",
                "subcategory": "pin",
                "difficulty": "beginner",
                "title": "The Pin",
            },
        },
        {
            "id": "tactic_fork",
            "content": "A fork attacks two or more pieces simultaneously with a single piece, forcing the opponent to save one while losing the other. Knight forks are especially powerful because knights cannot be blocked, but all pieces including pawns can deliver forks. Always scan for fork possibilities, particularly after checks — a check-fork is especially dangerous because the king must move first.",
            "metadata": {
                "category": "tactic",
                "subcategory": "fork",
                "difficulty": "beginner",
                "title": "The Fork",
            },
        },
        {
            "id": "tactic_skewer",
            "content": "A skewer is the reverse of a pin: a more valuable piece is attacked first and must move, exposing a less valuable piece behind it to capture. Skewers work along lines and diagonals, typically delivered by bishops, rooks, or queens. A common pattern is skewering the king along a rank or file with a rook, winning the rook or queen behind it.",
            "metadata": {
                "category": "tactic",
                "subcategory": "skewer",
                "difficulty": "beginner",
                "title": "The Skewer",
            },
        },
        {
            "id": "tactic_discovered_attack",
            "content": "A discovered attack occurs when moving one piece reveals an attack from another piece behind it. If the piece that moves also delivers a threat — especially a check — the opponent must deal with two threats simultaneously. Discovered checks are particularly devastating because the moving piece can capture freely or create threats while the opponent must address the check.",
            "metadata": {
                "category": "tactic",
                "subcategory": "discovered_attack",
                "difficulty": "beginner",
                "title": "Discovered Attack",
            },
        },
        {
            "id": "tactic_double_attack",
            "content": "A double attack threatens two targets at once, often by moving a piece to a square where it attacks two enemy pieces simultaneously. Unlike a fork, double attacks can also involve two different pieces each threatening something. The key to finding double attacks is looking for moves that combine threats — for instance, a queen moving to a square that attacks both a loose piece and a mating square.",
            "metadata": {
                "category": "tactic",
                "subcategory": "double_attack",
                "difficulty": "beginner",
                "title": "Double Attack",
            },
        },
        {
            "id": "tactic_deflection",
            "content": "Deflection forces a defending piece away from a critical square or defensive duty. By attacking the defender directly, you compel it to abandon its post, leaving the position it was guarding vulnerable. For example, deflecting a queen that guards against back rank mate by attacking it with a rook — the queen must move, and the back rank falls.",
            "metadata": {
                "category": "tactic",
                "subcategory": "deflection",
                "difficulty": "intermediate",
                "title": "Deflection",
            },
        },
        {
            "id": "tactic_decoy",
            "content": "A decoy sacrifice lures an enemy piece to a specific square where it becomes vulnerable to a follow-up tactic. Unlike deflection which drives a piece away, decoy attracts a piece to a bad square. A classic example is sacrificing a queen on a square where the king is forced to capture, walking into a discovered check or fork that wins back more material.",
            "metadata": {
                "category": "tactic",
                "subcategory": "decoy",
                "difficulty": "intermediate",
                "title": "Decoy",
            },
        },
        {
            "id": "tactic_removing_defender",
            "content": "Removing the defender (also called undermining or elimination) captures or drives away a piece that protects a key square or piece. Once the defender is removed, the previously defended target falls. Before executing a combination, always identify what is defending the target — if you can remove that defender at acceptable cost, the combination works.",
            "metadata": {
                "category": "tactic",
                "subcategory": "removing_defender",
                "difficulty": "intermediate",
                "title": "Removing the Defender",
            },
        },
        {
            "id": "tactic_back_rank",
            "content": "Back rank mate occurs when a rook or queen checkmates the king on its first rank, with the king trapped behind its own pawns. This is one of the most common tactical patterns in chess. To prevent back rank threats, create a luft (escape square) by advancing one pawn in front of your castled king (h3 or a3). Always be aware of back rank vulnerability, especially in positions with heavy pieces and few pawns.",
            "metadata": {
                "category": "tactic",
                "subcategory": "back_rank",
                "difficulty": "beginner",
                "title": "Back Rank Patterns",
            },
        },
        {
            "id": "tactic_overloaded_piece",
            "content": "An overloaded piece is one that has too many defensive responsibilities. If a single piece must guard two targets simultaneously, attacking one target forces the defender to abandon the other. To exploit overloading, identify pieces performing multiple defensive duties and then create threats against both targets — the defender cannot cope with both.",
            "metadata": {
                "category": "tactic",
                "subcategory": "overloaded_piece",
                "difficulty": "intermediate",
                "title": "Overloaded Pieces",
            },
        },
        {
            "id": "tactic_interference",
            "content": "Interference disrupts the coordination between enemy pieces by placing a piece on a critical square between them. This blocks a defensive line — such as a rook protecting another rook, or a bishop guarding a key diagonal. Interference often involves a sacrifice on the intersection square where two defensive lines cross, breaking the connection between defenders.",
            "metadata": {
                "category": "tactic",
                "subcategory": "interference",
                "difficulty": "intermediate",
                "title": "Interference",
            },
        },
        {
            "id": "tactic_zwischenzug",
            "content": "A zwischenzug (intermediate move) is an unexpected move inserted before making the expected or obvious recapture. Instead of recapturing immediately, you play a check, threat, or other forcing move first, then recapture on the next move under better conditions. Zwischenzugs are among the most commonly missed tactics — always ask yourself 'do I have to recapture right now, or is there a stronger move first?'",
            "metadata": {
                "category": "tactic",
                "subcategory": "zwischenzug",
                "difficulty": "intermediate",
                "title": "Zwischenzug (Intermediate Move)",
            },
        },
        {
            "id": "tactic_counting",
            "content": "Counting is the fundamental tactical skill of determining whether a sequence of captures on a square results in material gain or loss. When pieces converge on a contested square, count attackers versus defenders and consider the value of each piece involved. Always capture with the least valuable piece first, and remember that the side that runs out of defenders first loses the exchange.",
            "metadata": {
                "category": "tactic",
                "subcategory": "counting",
                "difficulty": "beginner",
                "title": "Counting Attackers and Defenders",
            },
        },
        {
            "id": "tactic_trapped_piece",
            "content": "A trapped piece is one that has no safe squares to retreat to and can be won. Bishops and knights that venture deep into enemy territory are especially vulnerable to being trapped by pawns. A classic example is the bishop trapped on a5 or h4 after overextending — always ensure your pieces have escape routes before advancing them into the opponent's position.",
            "metadata": {
                "category": "tactic",
                "subcategory": "trapped_piece",
                "difficulty": "beginner",
                "title": "Trapped Pieces",
            },
        },
        {
            "id": "tactic_x_ray",
            "content": "An X-ray (or skewer through) attack occurs when a long-range piece exerts influence through an enemy piece to a square behind it. This concept extends pins and skewers — even if a piece is blocked, its latent influence on squares behind the blocker can be tactically significant. X-ray defense similarly means a piece defends a square through an intervening piece.",
            "metadata": {
                "category": "tactic",
                "subcategory": "x_ray",
                "difficulty": "intermediate",
                "title": "X-Ray Attack",
            },
        },
        # =====================================================================
        # STRATEGIC CONCEPTS (~15 documents)
        # =====================================================================
        {
            "id": "strategy_iqp",
            "content": "The Isolated Queen's Pawn (IQP) on d4 provides spatial advantage and supports outposts on e5 and c5, but it can become a weakness in the endgame since it cannot be protected by other pawns. The IQP holder should play actively — piece attacks, central breakthroughs with d4-d5, and kingside initiatives. The opponent should trade pieces to reach an endgame where the isolated pawn becomes a static target.",
            "metadata": {
                "category": "strategy",
                "subcategory": "iqp",
                "difficulty": "intermediate",
                "title": "Isolated Queen's Pawn (IQP)",
            },
        },
        {
            "id": "strategy_carlsbad_structure",
            "content": "The Carlsbad pawn structure arises when White has pawns on c4/d4/e3 against Black's c6/d5/e6, typically from the Queen's Gambit Exchange variation. White's classic plan is the minority attack (b4-b5) to create a weak pawn on c6, while Black should seek kingside play or a central break with ...e5. Understanding who benefits from exchanges in this structure is critical — White often wants to trade pieces to exploit the queenside weakness.",
            "metadata": {
                "category": "strategy",
                "subcategory": "carlsbad_structure",
                "difficulty": "intermediate",
                "title": "Carlsbad Pawn Structure",
            },
        },
        {
            "id": "strategy_french_structure",
            "content": "In the French pawn structure, White typically has a pawn chain e5-d4 against Black's d5-e6. White should attack at the base of Black's chain (...d5) while maintaining the e5 outpost, and Black should attack the base of White's chain (d4) with ...c5 and ...f6. The locked center makes play on the wings essential — White attacks kingside, Black counterattacks queenside. Black's light-squared bishop, blocked by the e6 pawn, is a persistent strategic problem.",
            "metadata": {
                "category": "strategy",
                "subcategory": "french_structure",
                "difficulty": "intermediate",
                "title": "French Pawn Structure",
            },
        },
        {
            "id": "strategy_sicilian_structure",
            "content": "Sicilian pawn structures feature an asymmetry where White has a d-pawn versus Black's c-pawn. In Open Sicilian positions, White often has a central majority and kingside attacking chances, while Black has the semi-open c-file and queenside pawn majority. The d5 square is strategically critical — if a White knight lands there securely, it can dominate the position. Black must time ...d5 carefully to free the position without creating weaknesses.",
            "metadata": {
                "category": "strategy",
                "subcategory": "sicilian_structure",
                "difficulty": "intermediate",
                "title": "Sicilian Pawn Structures",
            },
        },
        {
            "id": "strategy_space_advantage",
            "content": "Space advantage means controlling more territory on the board, typically by advancing pawns beyond the fourth rank. With more space, your pieces have more room to maneuver and reposition, while your opponent's pieces are cramped. The side with less space should seek piece exchanges to alleviate the cramp, while the side with more space should avoid unnecessary trades and build up pressure gradually before breaking through.",
            "metadata": {
                "category": "strategy",
                "subcategory": "space",
                "difficulty": "beginner",
                "title": "Space Advantage",
            },
        },
        {
            "id": "strategy_good_bad_bishop",
            "content": "A 'bad' bishop is one blocked by its own pawns, which sit on the same color squares as the bishop, limiting its scope. A 'good' bishop has open diagonals because its own pawns are on the opposite color. To improve a bad bishop, either trade it, reposition it outside the pawn chain, or advance the pawns that block it. A bishop that appears bad can become powerful if the position opens up.",
            "metadata": {
                "category": "strategy",
                "subcategory": "good_bad_bishop",
                "difficulty": "beginner",
                "title": "Good and Bad Bishops",
            },
        },
        {
            "id": "strategy_outposts",
            "content": "An outpost is a square, typically in the opponent's half of the board, that cannot be attacked by enemy pawns. Knights are ideal outpost pieces because they don't need open lines and their short range is offset by advanced placement. A knight on an outpost in the center or near the enemy king can be worth as much as a rook. To create outposts, provoke or capture enemy pawns so they can no longer control the target square.",
            "metadata": {
                "category": "strategy",
                "subcategory": "outposts",
                "difficulty": "beginner",
                "title": "Outposts",
            },
        },
        {
            "id": "strategy_prophylaxis",
            "content": "Prophylaxis means anticipating and preventing your opponent's plans before improving your own position. Prophylactic thinking asks 'what does my opponent want to do?' before deciding on your own move. Great players like Petrosian and Karpov excelled at prophylaxis — sometimes the best move is not an aggressive one but one that denies the opponent's best reply, gradually squeezing their options until the position collapses.",
            "metadata": {
                "category": "strategy",
                "subcategory": "prophylaxis",
                "difficulty": "intermediate",
                "title": "Prophylaxis",
            },
        },
        {
            "id": "strategy_initiative",
            "content": "The initiative means having the ability to create threats and dictate the flow of the game, forcing your opponent to react to your plans. Maintaining the initiative often requires energetic play — sometimes even sacrificing material to keep the pressure on. Once you lose the initiative, regaining it can be extremely difficult, so think carefully before making passive or defensive moves when you have attacking momentum.",
            "metadata": {
                "category": "strategy",
                "subcategory": "initiative",
                "difficulty": "intermediate",
                "title": "The Initiative",
            },
        },
        {
            "id": "strategy_piece_activity_vs_material",
            "content": "Piece activity can outweigh material advantage. A position where all your pieces are actively placed and coordinated may be worth a pawn or even more compared to a position with extra material but passive pieces. When evaluating a sacrifice, consider whether the resulting activity and initiative compensate for the material investment. In practice, three well-placed pieces coordinating an attack often beat a materially superior but disorganized army.",
            "metadata": {
                "category": "strategy",
                "subcategory": "piece_activity",
                "difficulty": "intermediate",
                "title": "Piece Activity vs Material",
            },
        },
        {
            "id": "strategy_two_bishops",
            "content": "The bishop pair (two bishops against bishop and knight or two knights) is a significant advantage, especially in open positions. Two bishops can control diagonals of both colors and coordinate over long range, covering the entire board. To maximize the bishop pair, open the position by exchanging pawns and avoid blocking the bishops' diagonals. The advantage grows in the endgame as fewer pieces mean fewer obstacles on the bishops' diagonals.",
            "metadata": {
                "category": "strategy",
                "subcategory": "two_bishops",
                "difficulty": "intermediate",
                "title": "The Two Bishops Advantage",
            },
        },
        {
            "id": "strategy_weak_squares",
            "content": "Weak squares are squares that can no longer be defended by pawns, making them vulnerable to enemy piece occupation. Once a pawn advances, the squares it previously controlled become potential weaknesses — for example, playing f3 weakens e3 and g3. Weak squares near the king are especially dangerous, as they provide enemy pieces with invasion routes. Always consider the long-term consequences of pawn moves on square control.",
            "metadata": {
                "category": "strategy",
                "subcategory": "weak_squares",
                "difficulty": "beginner",
                "title": "Weak Squares",
            },
        },
        {
            "id": "strategy_open_files",
            "content": "Rooks need open or semi-open files to be effective. An open file has no pawns of either color, while a semi-open file has only the opponent's pawn. Seizing an open file with a rook — and ideally doubling rooks on it — allows penetration into the enemy position, typically on the 7th or 8th rank. If there are no open files, plan to create one through pawn exchanges.",
            "metadata": {
                "category": "strategy",
                "subcategory": "open_files",
                "difficulty": "beginner",
                "title": "Open Files for Rooks",
            },
        },
        {
            "id": "strategy_piece_coordination",
            "content": "Piece coordination means your pieces work together harmoniously, supporting each other's functions and combining for threats. Poorly coordinated pieces — even if materially equal — lose to well-coordinated ones. Look for ways to improve the worst-placed piece in your position, as a chain is only as strong as its weakest link. Typical coordinating themes include battery formations (queen behind rook or bishop), knight pairs controlling complementary squares, and rooks doubling on files.",
            "metadata": {
                "category": "strategy",
                "subcategory": "piece_coordination",
                "difficulty": "intermediate",
                "title": "Piece Coordination",
            },
        },
        {
            "id": "strategy_pawn_majority",
            "content": "A pawn majority is a numerical advantage of pawns on one side of the board. The strategic goal of a healthy pawn majority is to create a passed pawn by advancing the majority and exchanging pawns. A queenside pawn majority is often more valuable in the middlegame because pawns advance away from the kings, while a kingside majority can support a direct attack. A crippled majority (with doubled or isolated pawns) may be unable to create a passed pawn.",
            "metadata": {
                "category": "strategy",
                "subcategory": "pawn_majority",
                "difficulty": "intermediate",
                "title": "Pawn Majority",
            },
        },
        # =====================================================================
        # ENDGAME PRINCIPLES (~10 documents)
        # =====================================================================
        {
            "id": "endgame_king_activity",
            "content": "In the endgame, the king transforms from a piece that needs protection into a powerful attacking and defending force. Centralize your king as soon as the queens are off the board — a centralized king supports its own pawns, attacks enemy pawns, and controls key squares. The king can often be worth roughly 4 points of piece value in the endgame, so activating it quickly is one of the most important endgame principles.",
            "metadata": {
                "category": "endgame",
                "subcategory": "king_activity",
                "difficulty": "beginner",
                "title": "King Activity in Endgames",
            },
        },
        {
            "id": "endgame_lucena_position",
            "content": "The Lucena position is the most important winning setup in rook endgames. It arises when you have a rook and pawn versus rook, with your king in front of the pawn on the queening square. The winning technique involves building a 'bridge' — moving your rook to the 4th rank (or 5th depending on the pawn), then using it to shield your king from checks as it escorts the pawn to promotion. Every chess player must know this technique by heart.",
            "metadata": {
                "category": "endgame",
                "subcategory": "lucena",
                "difficulty": "intermediate",
                "title": "Lucena Position",
            },
        },
        {
            "id": "endgame_philidor_position",
            "content": "The Philidor position is the key defensive technique in rook endgames with rook and pawn versus rook. The defending side places their rook on the 6th rank (3rd rank for Black) to cut off the enemy king, then switches to giving checks from behind once the pawn advances to the 6th rank. The critical idea is passive defense with the rook on the 6th rank when the pawn is behind the 6th, and active checking from behind when the pawn reaches the 6th rank.",
            "metadata": {
                "category": "endgame",
                "subcategory": "philidor",
                "difficulty": "intermediate",
                "title": "Philidor Position",
            },
        },
        {
            "id": "endgame_passed_pawns",
            "content": "A passed pawn is one with no enemy pawns blocking or guarding its advance to promotion. Passed pawns gain strength as they advance — a passed pawn on the 6th rank ties down enemy pieces significantly. In the endgame, a protected passed pawn (supported by another pawn) is especially strong because it cannot be captured without cost, and the pieces defending against it are tied down. Create passed pawns by exchanging pawns where you have a majority.",
            "metadata": {
                "category": "endgame",
                "subcategory": "passed_pawns",
                "difficulty": "beginner",
                "title": "Passed Pawns",
            },
        },
        {
            "id": "endgame_opposition",
            "content": "Opposition is a critical concept in king and pawn endgames where the two kings face each other with one square between them. The player who does NOT have to move holds the opposition and can force the opposing king to give way. Direct opposition (kings on the same file or rank with one square between) is most common, but distant opposition (multiple squares apart on the same line) and diagonal opposition also exist. Opposition often determines whether a pawn ending is won or drawn.",
            "metadata": {
                "category": "endgame",
                "subcategory": "opposition",
                "difficulty": "beginner",
                "title": "Opposition",
            },
        },
        {
            "id": "endgame_queen_vs_pawn",
            "content": "Queen versus a pawn on the 7th rank is usually a win for the queen, but pawns on the c, f, a, and h files present special difficulties. Bishop pawns (c and f) can draw because the king can reach the corner and force stalemate. Rook pawns (a and h) can also sometimes draw by stalemate motifs. For central and knight pawns, the queen wins by approaching the pawn with checks, driving the enemy king in front of its own pawn, and bringing the friendly king closer.",
            "metadata": {
                "category": "endgame",
                "subcategory": "queen_vs_pawn",
                "difficulty": "intermediate",
                "title": "Queen vs Pawn Endgames",
            },
        },
        {
            "id": "endgame_bishop_endgames",
            "content": "Same-colored bishop endgames can be decisive because the stronger side's bishop can dominate the opponent's by controlling key diagonals and supporting passed pawns. Opposite-colored bishop endgames are famous for their drawing tendencies — even two extra pawns may not be enough to win if the defending bishop controls the queening square. In opposite-colored bishop positions, the attacker should create passed pawns on both sides of the board to overload the defending bishop.",
            "metadata": {
                "category": "endgame",
                "subcategory": "bishop_endgames",
                "difficulty": "intermediate",
                "title": "Bishop Endgames",
            },
        },
        {
            "id": "endgame_rook_seventh_rank",
            "content": "A rook on the 7th rank (2nd rank for Black) is enormously powerful, attacking pawns from behind and confining the enemy king to the back rank. Two rooks on the 7th rank can often force checkmate or win decisive material. In rook endgames, the first priority is often to seize the 7th rank — this alone can turn a slightly worse position into a winning one. Defend against rook invasions by keeping your pawns off the rank your opponent's rook controls.",
            "metadata": {
                "category": "endgame",
                "subcategory": "rook_seventh",
                "difficulty": "beginner",
                "title": "Rook on the Seventh Rank",
            },
        },
        {
            "id": "endgame_knight_vs_bishop",
            "content": "Knights are generally superior in closed positions with pawns fixed on both sides, where they can hop over obstacles. Bishops are superior in open positions where they can sweep across the board. In knight vs bishop endgames, the side with the knight should keep the position closed and place pawns on the same color as the enemy bishop to restrict it, while the side with the bishop should open the position and create play on both flanks.",
            "metadata": {
                "category": "endgame",
                "subcategory": "knight_vs_bishop",
                "difficulty": "intermediate",
                "title": "Knight vs Bishop Endgames",
            },
        },
        {
            "id": "endgame_zugzwang",
            "content": "Zugzwang is a situation where any move a player makes worsens their position — they would prefer to pass but cannot. Zugzwang is most common in endgames, especially king and pawn endings, where the obligation to move forces the king to give ground. Recognizing zugzwang positions and knowing how to create them is essential for converting endgame advantages. In more complex positions, mutual zugzwang can arise where whoever has to move loses.",
            "metadata": {
                "category": "endgame",
                "subcategory": "zugzwang",
                "difficulty": "intermediate",
                "title": "Zugzwang",
            },
        },
        # =====================================================================
        # PHASE-SPECIFIC ADVICE (~10 documents)
        # =====================================================================
        {
            "id": "phase_opening_priorities",
            "content": "The three priorities in the opening, in order of importance: 1) King safety — castle early and avoid weakening pawn moves around your king. 2) Development — get all pieces into the game quickly, aiming for one piece per move. 3) Center control — occupy or influence the center with pawns and pieces. Violating these priorities without a concrete tactical justification typically leads to a difficult position.",
            "metadata": {
                "category": "opening",
                "subcategory": "priorities",
                "difficulty": "beginner",
                "title": "Opening Priorities",
            },
        },
        {
            "id": "phase_middlegame_planning",
            "content": "Middlegame planning should be based on the pawn structure and piece placement, not on vague ideas. Ask yourself: Where are the open files? Where are the weak squares? Which pieces are well-placed and which need improvement? A good plan targets a specific weakness in the opponent's position or aims to improve the placement of your worst piece. Even an imperfect plan is better than no plan at all — aimless moves allow the opponent to seize the initiative.",
            "metadata": {
                "category": "middlegame",
                "subcategory": "planning",
                "difficulty": "beginner",
                "title": "Middlegame Planning",
            },
        },
        {
            "id": "phase_when_to_trade",
            "content": "Trade pieces when you have a material advantage (simplifying toward a winning endgame), when your opponent's pieces are more active than yours, or when trades help you achieve a specific strategic goal. Avoid trading when you have the initiative and your pieces are more active, when you need pieces for an attack, or when the trades help your opponent uncramp their position. Trading the right pieces is a critical strategic skill — sometimes exchanging one specific pair of knights changes the entire character of the position.",
            "metadata": {
                "category": "middlegame",
                "subcategory": "trading_pieces",
                "difficulty": "intermediate",
                "title": "When to Trade Pieces",
            },
        },
        {
            "id": "phase_attacking_king",
            "content": "Before launching a kingside attack, ensure you have at least a local superiority of force — typically three attacking pieces minimum. Common attacking ingredients include: open files or diagonals toward the king, a pawn storm to break open the king's shelter, piece sacrifices on key squares (especially h7/h2 or g7/g2), and removing key defenders through exchanges. A premature attack with insufficient force often backfires, leaving you overextended with weaknesses in your own position.",
            "metadata": {
                "category": "middlegame",
                "subcategory": "attacking_king",
                "difficulty": "intermediate",
                "title": "Attacking the King",
            },
        },
        {
            "id": "phase_endgame_conversion",
            "content": "Converting an advantage in the endgame requires patience and precision. The general technique is: 1) Improve your king position. 2) Create a passed pawn or fix a weakness in the opponent's camp. 3) Tie down the opponent's pieces to passive defense. 4) Only then break through decisively. Rushing to win can squander the advantage — methodical improvement of your position, known as the 'principle of progress,' is the surest path to victory.",
            "metadata": {
                "category": "endgame",
                "subcategory": "conversion",
                "difficulty": "intermediate",
                "title": "Endgame Conversion",
            },
        },
        {
            "id": "phase_pawn_majority_play",
            "content": "To advance a pawn majority and create a passed pawn, push the candidate pawn (the pawn with no opposing pawn directly in front of it) first. Advance in a way that forces favorable exchanges — the goal is to trade one of your majority pawns for the opponent's minority pawn, leaving you with a passed pawn. A healthy pawn majority (no doubled or isolated pawns) should always be able to create a passed pawn with correct play.",
            "metadata": {
                "category": "endgame",
                "subcategory": "pawn_majority_play",
                "difficulty": "intermediate",
                "title": "Pawn Majority Play",
            },
        },
        {
            "id": "phase_two_weaknesses",
            "content": "The principle of two weaknesses states that one weakness is often not enough to win — you need to create a second weakness on the other side of the board. By threatening two targets simultaneously, you overstretch the opponent's defenses, as their pieces cannot protect both flanks at once. This principle applies to all phases but is especially important in endgames: first fix one weakness, then create play on the other side, then shuttle your pieces between the two targets until the defense cracks.",
            "metadata": {
                "category": "strategy",
                "subcategory": "two_weaknesses",
                "difficulty": "intermediate",
                "title": "The Principle of Two Weaknesses",
            },
        },
        {
            "id": "phase_middlegame_pawn_breaks",
            "content": "Pawn breaks are pawn advances that challenge the opponent's pawn structure, opening lines and changing the character of the position. Common breaks include d4-d5 in the King's Indian, ...c5 in the Sicilian, ...e5 in many queen pawn openings, and ...f5 as a kingside counterattack. Timing a pawn break correctly is crucial — play it too early without adequate piece support and it may fail; play it too late and the opponent may prevent it entirely.",
            "metadata": {
                "category": "middlegame",
                "subcategory": "pawn_breaks",
                "difficulty": "intermediate",
                "title": "Pawn Breaks",
            },
        },
        {
            "id": "phase_transition_to_endgame",
            "content": "The transition from middlegame to endgame is a critical moment that many players handle poorly. Before exchanging queens or entering an endgame, evaluate whether the resulting position favors you — consider pawn structure, king activity potential, and piece activity. Sometimes the right decision is to avoid the endgame and keep the queens on even when behind in material, as endgames are more technical and favor the side with structural advantages.",
            "metadata": {
                "category": "middlegame",
                "subcategory": "transition",
                "difficulty": "intermediate",
                "title": "Transitioning to the Endgame",
            },
        },
        {
            "id": "phase_defense_technique",
            "content": "When defending a worse position, follow these principles: keep pieces active rather than purely passive, seek counterplay rather than just defending, exchange your opponent's most dangerous attacking pieces, and avoid creating additional weaknesses. Practical defense also includes setting traps, complicating the position, and making your opponent find difficult moves. A fortress — a setup the opponent cannot break through despite material advantage — is often the defender's best hope in otherwise lost endgames.",
            "metadata": {
                "category": "middlegame",
                "subcategory": "defense",
                "difficulty": "intermediate",
                "title": "Defensive Technique",
            },
        },
        # =====================================================================
        # ADDITIONAL DOCUMENTS (to reach ~70 total)
        # =====================================================================
        {
            "id": "strategy_doubled_pawns",
            "content": "Doubled pawns (two pawns of the same color on the same file) are generally a weakness because they are less mobile and one of them cannot be protected by the other. However, doubled pawns are not always bad — they can open a file for a rook and control additional squares. Doubled pawns are most harmful when they are isolated and doubled (no adjacent pawns for support), as they become static targets that tie down your pieces to their defense.",
            "metadata": {
                "category": "strategy",
                "subcategory": "doubled_pawns",
                "difficulty": "beginner",
                "title": "Doubled Pawns",
            },
        },
        {
            "id": "strategy_backward_pawn",
            "content": "A backward pawn is one that cannot advance because the adjacent pawns have already moved forward, and advancing it would result in its capture. The square in front of a backward pawn is often a strong outpost for the opponent's pieces, particularly knights. To exploit a backward pawn, occupy the square in front of it and apply pressure down the file. To play with a backward pawn, seek to advance it with proper piece support or exchange it off.",
            "metadata": {
                "category": "strategy",
                "subcategory": "backward_pawn",
                "difficulty": "intermediate",
                "title": "Backward Pawns",
            },
        },
        {
            "id": "strategy_hanging_pawns",
            "content": "Hanging pawns are a pair of adjacent pawns (typically on c4 and d4 or c5 and d5) that have no neighboring pawns for support. They control important central squares and can provide dynamic energy through pawn advances, but they can also become targets if blockaded. The side with hanging pawns should play actively and seek a timely advance (d4-d5 or c4-c5), while the opponent should blockade them and attack the base of the pair.",
            "metadata": {
                "category": "strategy",
                "subcategory": "hanging_pawns",
                "difficulty": "intermediate",
                "title": "Hanging Pawns",
            },
        },
        {
            "id": "tactic_greek_gift",
            "content": "The Greek Gift sacrifice (Bxh7+) is a classic attacking pattern against a castled king. The typical prerequisites are: a bishop on the b1-h7 diagonal, a knight ready to jump to g5, and a queen that can reach the kingside quickly (usually via h5 or d3-h7). After Bxh7+ Kxh7, Ng5+ forces the king out, and Qh5 creates a mating attack. Always verify that the opponent cannot escape with ...Kg8 or adequately defend with ...Kg6 before executing this sacrifice.",
            "metadata": {
                "category": "tactic",
                "subcategory": "greek_gift",
                "difficulty": "intermediate",
                "title": "Greek Gift Sacrifice",
            },
        },
        {
            "id": "endgame_rook_pawn_activity",
            "content": "In rook endgames, rook activity is more important than pawn count. An active rook behind a passed pawn (your own or the opponent's) is far more effective than a passive rook defending from the side. Tarrasch's rule states that rooks belong behind passed pawns — this applies to both your own (supporting the advance) and the opponent's (controlling the pawn from behind as it advances further away from the rook's influence).",
            "metadata": {
                "category": "endgame",
                "subcategory": "rook_activity",
                "difficulty": "intermediate",
                "title": "Rook Activity in Endgames",
            },
        },

        # =====================================================================
        # EXPANDED PIN THEORY (wiki_pin_*)
        # =====================================================================
        {
            "id": "wiki_pin_absolute",
            "content": "An absolute pin is one where the pinned piece cannot legally move because doing so would expose the king to check. This is the most powerful form of pin since the opponent literally cannot break it by moving the pinned piece. Absolute pins occur when a sliding piece (bishop, rook, or queen) attacks a piece that shields the king along a rank, file, or diagonal. The pinner can exploit this systematically by piling on additional attackers against the pinned piece: if the defender cannot move it away, they must bring up other defenders instead. Classic exploitation involves attacking the pinned piece with pawns, forcing material loss. A key subtlety: even an absolutely pinned piece can still give check if it remains on the attacking line, and can still defend other pieces against captures by the enemy king. Always verify whether breaking the pin by interposing is possible before assuming the pin is permanent.",
            "metadata": {
                "category": "tactic",
                "subcategory": "pin",
                "difficulty": "beginner",
                "title": "Absolute Pin",
            },
        },
        {
            "id": "wiki_pin_relative",
            "content": "A relative pin is one where the piece shielded by the pinned piece is a valuable piece other than the king. Moving the pinned piece is technically legal but typically unwise because the shielded piece would be lost. Relative pins require careful evaluation: the defender must weigh whether moving the pinned piece is worth the material cost of losing the shielded piece, especially if the move creates a counter-threat. Relative pins are common strategic tools because they restrict the opponent's options without the absolute illegality constraint. A pinned piece in a relative pin often cannot defend other pieces effectively, creating secondary weaknesses. The Bg5 pin against Nf6 in many openings is a classic relative pin — it ties the knight to the queen on d8, reducing Black's defensive resources. Defending against a relative pin often means either breaking the pin through interposition, attacking the pinning piece, or accepting the exchange and compensating elsewhere.",
            "metadata": {
                "category": "tactic",
                "subcategory": "pin",
                "difficulty": "intermediate",
                "title": "Relative Pin Strategy",
            },
        },
        {
            "id": "wiki_pin_exploitation",
            "content": "Working the pin is an advanced technique where the pinner piles up attackers on the pinned piece since it cannot legally or practically escape. The defender must bring additional pieces to defend the pinned piece, tying down resources and creating further weaknesses. The attacking side can multiply pressure: first pin, then attack with a pawn, then add a rook or queen. Once the pinned piece is attacked more times than it can be defended, material wins. A doubled rook battery with a queen behind (Alekhine's Gun) is the ultimate expression of pin exploitation. Pins on the d- and e-files are especially powerful in opened positions because the queens typically occupy those files and pinning a center piece immobilizes vital defenders. Pins on the h4-d8 or b4-e7 diagonal (bishop pinning knight to queen) are common opening weapons that restrict Black's ability to complete development. The f3-knight pinned by Bg4 in many positions gives Black long-term pressure because the knight can no longer support e4 or advance to e5.",
            "metadata": {
                "category": "tactic",
                "subcategory": "pin",
                "difficulty": "intermediate",
                "title": "Exploiting and Working the Pin",
            },
        },
        {
            "id": "wiki_pin_breaking",
            "content": "Breaking a pin (unpinning) can be accomplished in several ways, each with strategic implications. First, the piece creating the pin can be captured if it is undefended or if the exchange is favorable. Second, another unit can be interposed to block the line of the pin — this is often the safest solution. Third, the piece being shielded (the king or valuable piece) can be moved off the attacked line, eliminating the pin's purpose. Fourth, the pinned piece itself can sometimes move despite the relative pin, especially if it creates a check or a decisive counter-threat (as in the Legal Trap, where Nxe5 sacrifices the knight despite the Bg4 pin on Nf3). A partial pin occurs when the pinned piece can still move along the pinning line — for example, a queen pinned along a file can still move along that same file. Recognizing when to break a pin actively versus passively defend is a key strategic skill. Breaking the pin early (attacking the pinner) is usually preferable to passive defense.",
            "metadata": {
                "category": "tactic",
                "subcategory": "pin",
                "difficulty": "intermediate",
                "title": "Breaking Pins: Unpinning Techniques",
            },
        },

        # =====================================================================
        # EXPANDED FORK THEORY (wiki_fork_*)
        # =====================================================================
        {
            "id": "wiki_fork_knight",
            "content": "The knight fork is the most feared type of fork because knights cannot be captured by the non-knight pieces they attack (pawns, bishops, rooks, queens cannot immediately recapture), and as a minor piece the knight is less valuable than the rooks and queens it typically forks. Knights are particularly dangerous forks because their unique L-shaped movement creates threats that do not exist along any line, making them harder to anticipate. A royal fork attacks the king and queen simultaneously with a knight, winning the queen. A family fork (or family check) occurs when a knight simultaneously attacks the king, queen, and one or more rooks. When the king is one of the forked pieces, it is an absolute fork: the king must move, and the other forked piece is lost with no compensation. To create a knight fork, look for squares that attack two or more enemy pieces simultaneously and calculate whether you can reach that square safely, possibly via a forcing sacrifice.",
            "metadata": {
                "category": "tactic",
                "subcategory": "fork",
                "difficulty": "beginner",
                "title": "Knight Fork Patterns",
            },
        },
        {
            "id": "wiki_fork_pawn",
            "content": "Pawn forks are extremely efficient because pawns are the least valuable pieces, so a pawn attacking two more valuable pieces simultaneously almost always wins material. A pawn fork occurs when a pawn advances to a square where it attacks two enemy pieces on adjacent files. The most common pawn fork scenario involves pushing a center or flank pawn to attack a knight and bishop, or two minor pieces. To create pawn fork opportunities, look for moments when enemy pieces are placed on squares where a pawn advance would hit both. In the Two Knights Defense, the move ...d5 after 4.Nc3 Nxe4 5.Nxe4 creates a pawn fork on d5 that wins back a piece. Pawn forks in the endgame can be decisive, as a passed pawn creating a fork is often unstoppable. The defensive principle against pawn forks is to avoid placing two pieces on squares reachable by the same pawn advance.",
            "metadata": {
                "category": "tactic",
                "subcategory": "fork",
                "difficulty": "beginner",
                "title": "Pawn Fork Opportunities",
            },
        },
        {
            "id": "wiki_fork_queen_rook",
            "content": "Queen and rook forks require more specific conditions than knight forks because the queen's high value means the forked pieces must be sufficiently valuable (typically undefended) to make the fork profitable. A queen fork attacking two undefended pieces wins material cleanly. However, a queen fork against defended pieces may not work — the opponent can simply defend one piece while the other is captured. Rook forks occur when a rook attacks two pieces along a rank or file; they are most effective when one of the targets is a king (forcing the king to move). Queen forks involving a check (one of the attacked pieces is the king) are among the strongest because the king is forced to move. When calculating queen and rook forks, always check whether the forking piece can itself be captured or chased away before completing the double attack. Queen forks are often the result of forcing sequences rather than simple positioning.",
            "metadata": {
                "category": "tactic",
                "subcategory": "fork",
                "difficulty": "intermediate",
                "title": "Queen and Rook Forks",
            },
        },

        # =====================================================================
        # EXPANDED SKEWER THEORY (wiki_skewer_*)
        # =====================================================================
        {
            "id": "wiki_skewer_definition",
            "content": "A skewer is a tactic in which a more valuable piece is directly attacked along a line, and when it moves to safety it exposes a less valuable piece behind it to capture. The skewer is the inverse of a pin: in a pin, the more valuable piece is behind the attacked piece; in a skewer, the more valuable piece is directly attacked and must move, revealing the less valuable piece behind it. Only sliding pieces (bishop, rook, queen) can execute skewers. The most common skewer involves a rook or queen attacking an enemy king or queen, which must move, uncovering a rook or other piece that is then captured. Skewers to the king are particularly powerful because the king has no choice but to move. An absolute skewer forces the king to move and costs material. A relative skewer attacks a valuable but not essential piece (such as a queen) that may be worth moving despite the material loss behind it.",
            "metadata": {
                "category": "tactic",
                "subcategory": "skewer",
                "difficulty": "beginner",
                "title": "Skewer: Definition and Types",
            },
        },
        {
            "id": "wiki_skewer_vs_pin",
            "content": "The skewer and pin are mirror-image tactics performed along the same attacking lines but with the piece values inverted. In a pin, the less valuable piece is attacked, and the more valuable piece hides safely behind it (the attacker hopes to exploit the pinned piece). In a skewer, the more valuable piece is attacked directly, and it must move to reveal the less valuable piece behind it. Understanding this distinction helps in recognizing both tactics: pins require the attacker to accumulate pressure on the front piece, while skewers work immediately by forcing the attacked piece to move. Skewers through the king are always effective because the king cannot voluntarily stay in check. Skewers through the queen are often decisive if the piece behind is a rook or the position is otherwise winning. The x-ray attack is related to the skewer: it involves a piece exerting indirect pressure through another piece on a target behind it.",
            "metadata": {
                "category": "tactic",
                "subcategory": "skewer",
                "difficulty": "intermediate",
                "title": "Skewer vs Pin: The Inverse Relationship",
            },
        },

        # =====================================================================
        # EXPANDED DISCOVERED ATTACK THEORY (wiki_discovered_*)
        # =====================================================================
        {
            "id": "wiki_discovered_attack_types",
            "content": "A discovered attack occurs when a piece moves and reveals an attack by another piece behind it on a target. The moving piece can make a new threat of its own, creating a double threat that is often impossible to meet. The most powerful form is a discovered check, where the piece that moves exposes the king to check from the piece behind it. This forces the opponent to respond to the check first, allowing the moving piece to capture freely or create unstoppable threats. A double check is the ultimate discovered attack: both the moving piece and the revealed piece give check simultaneously, meaning the king cannot block or interpose — it must move, and often there is no safe square. Double checks frequently lead to checkmate. When calculating discovered attacks, always ask: can the moving piece simultaneously capture a piece, deliver a check, or create a mating threat? The more threats created, the more decisive the discovered attack.",
            "metadata": {
                "category": "tactic",
                "subcategory": "discovered_attack",
                "difficulty": "intermediate",
                "title": "Types of Discovered Attack",
            },
        },
        {
            "id": "wiki_discovered_battery",
            "content": "A battery is the arrangement of two pieces of the same type (or a rook with queen, or bishop with queen) on the same file, rank, or diagonal so that the front piece can move to reveal the attack of the back piece. Doubling rooks on an open file creates a battery that can support discovered attacks and execute multiple threats. The queen-bishop battery on a long diagonal is a common attacking formation that threatens discovered checks. The queen-rook battery on the seventh rank is a powerful endgame and middlegame tool. Setting up batteries requires recognizing which piece will move (the front piece creates new threats) and which piece will reveal its attack (the back piece). Batteries are particularly powerful when they point at the enemy king, as every move of the front piece threatens either a direct attack or a discovered check. Preparing a battery means placing pieces on the right lines and then creating a moment when the battery fires.",
            "metadata": {
                "category": "tactic",
                "subcategory": "discovered_attack",
                "difficulty": "intermediate",
                "title": "Batteries and Discovered Attacks",
            },
        },

        # =====================================================================
        # EXPANDED ZWISCHENZUG THEORY (wiki_zwischenzug_*)
        # =====================================================================
        {
            "id": "wiki_zwischenzug_concept",
            "content": "A zwischenzug (German: in-between move) is an unexpected intermediate move that interrupts what appears to be a forced sequence of moves. Instead of responding directly to the opponent's threat, the player inserts a move that creates a new and more urgent threat, forcing the opponent to respond before they can execute their plan. The zwischenzug is one of the most psychologically difficult tactics to spot because it violates the natural expectation of recapturing or responding to a direct threat. Classic zwischenzug situations arise in capture sequences: instead of recapturing immediately, a player finds a check or a decisive threat that changes the evaluation of the entire exchange. The key to finding zwischenzugs is to pause before automatic recaptures and ask: is there a more forcing move available? Common zwischenzug patterns include checking the king before recapturing, attacking a hanging piece before responding to a threat, or promoting a pawn before taking back.",
            "metadata": {
                "category": "tactic",
                "subcategory": "zwischenzug",
                "difficulty": "intermediate",
                "title": "Zwischenzug: The In-Between Move",
            },
        },
        {
            "id": "wiki_zwischenzug_defensive",
            "content": "Defensive zwischenzugs are particularly important to recognize when your position seems lost or materially inferior. Instead of recapturing a piece that would leave you in a worse position, a defensive in-between move can change the outcome of a sequence entirely. For example, if an opponent captures a piece and expects you to recapture, a defensive zwischenzug might involve checking their king, attacking their queen, or creating a mating threat that forces them to deal with a new problem. Failing to look for defensive zwischenzugs often leads to unnecessarily bad outcomes. Conversely, when executing a combination, always check whether the opponent has a zwischenzug available before committing — otherwise a calculation that appears to win may actually lose if the opponent can insert an unexpected forcing move. The principle of checking for in-between moves applies both offensively and defensively in every combination.",
            "metadata": {
                "category": "tactic",
                "subcategory": "zwischenzug",
                "difficulty": "advanced",
                "title": "Defensive Zwischenzugs",
            },
        },

        # =====================================================================
        # EXPANDED OUTPOST THEORY (wiki_outpost_*)
        # =====================================================================
        {
            "id": "wiki_outpost_creation",
            "content": "An outpost is a square on the opponent's side of the board that cannot be attacked by enemy pawns and can be permanently occupied by a piece. Outposts are most valuable on the 5th, 6th, and 7th ranks, especially in the center or near the opponent's king. A knight on an outpost is exceptionally powerful because knights need to be close to their targets and cannot be chased away by pawns once established. To create an outpost, you must first eliminate the pawn that would attack the square by capturing it or provoking an exchange. The most common method is the exchange ...cxd5 or exd5 leaving a hole on d5 or c5. Once an outpost is created, the goal is to occupy it with the most effective piece — usually a knight, sometimes a bishop. An outpost knight on d6 or e6 deep in enemy territory can be paralyzingly strong, potentially worth as much as a rook.",
            "metadata": {
                "category": "strategy",
                "subcategory": "outpost",
                "difficulty": "intermediate",
                "title": "Creating and Occupying Outposts",
            },
        },
        {
            "id": "wiki_outpost_knight_vs_bishop",
            "content": "The classic outpost battle is when a knight on a strong outpost competes against a bishop in an open position. A knight on an outpost at d5 or c5, protected by a pawn, can dominate a bishop confined by its own pawns. The bishop's long-range capability is nullified when all key squares are covered by the knight and pawns. This is the basis of the 'good knight versus bad bishop' imbalance: if you have a knight and can establish it on an outpost while the opponent's bishop is hemmed in by pawns on the same color, the knight is strategically superior despite the theoretical equality of minor pieces. When fighting against an outpost knight, you must either exchange it off (especially using your own bishop), drive it away by advancing pawns to attack it, or accept the positional disadvantage and seek counterplay elsewhere. A knight on the 6th rank supported by a pawn is often stronger than a rook in the endgame.",
            "metadata": {
                "category": "strategy",
                "subcategory": "outpost",
                "difficulty": "advanced",
                "title": "Outpost Knight vs Restricted Bishop",
            },
        },

        # =====================================================================
        # EXPANDED PASSED PAWN THEORY (wiki_passed_pawn_*)
        # =====================================================================
        {
            "id": "wiki_passed_pawn_types",
            "content": "A passed pawn has no opposing pawns on its file or adjacent files to prevent promotion. Passed pawns are classified by their type: a protected passed pawn is protected by another pawn, making it immune to capture by the opposing king; connected passed pawns are adjacent passed pawns that support each other and are extremely powerful — a steamroller of connected passed pawns on the 6th rank beats a rook. An outside passed pawn is separated from the main pawn mass and can deflect the opposing king far from the defense of other pawns. The outside passed pawn in a king and pawn endgame is often decisive because the defending king must chase it while the attacking king captures the other pawns unopposed. As Nimzowitsch famously stated: 'A passed pawn is a criminal which should be kept under lock and key.' The value of a passed pawn increases geometrically as it advances — a passed pawn on the 7th rank may be worth more than a rook.",
            "metadata": {
                "category": "endgame",
                "subcategory": "passed_pawn",
                "difficulty": "intermediate",
                "title": "Types of Passed Pawns",
            },
        },
        {
            "id": "wiki_passed_pawn_outside",
            "content": "The outside passed pawn is one of the most decisive strategic weapons in king and pawn endgames. When one side has a passed pawn on the flank (especially the a- or h-file) separated from the main pawn mass, the opposing king must go to stop it, leaving the other pawns undefended. The attacking king then marches to the other side to win those pawns. The outside passed pawn works as a 'decoy' — it forces the opponent's king to commit to stopping it, creating a winning deflection. The key principle: if the outside passed pawn is far enough away, the defending king cannot both stop the pawn and prevent the attacking king from winning the remaining pawns. In rook endgames, the outside passed pawn is less effective because a rook placed behind the pawn can control it without the king's help, per Tarrasch's rule. In minor piece endgames, the outside passed pawn is often decisive because minor pieces cannot stop a passed pawn as efficiently as a rook.",
            "metadata": {
                "category": "endgame",
                "subcategory": "passed_pawn",
                "difficulty": "intermediate",
                "title": "The Outside Passed Pawn",
            },
        },
        {
            "id": "wiki_passed_pawn_blockade",
            "content": "Blockading a passed pawn means placing a piece directly in front of it to prevent its advance. Nimzowitsch developed the theory of blockade as a key defensive strategy: the ideal blockader is a piece that is strong on the blockading square while neutralizing the passed pawn's threat. Knights make the best blockaders because they control squares around the pawn while sitting on a strong central square; a knight blockading a passed pawn on d6 or e5 also attacks other parts of the board. Bishops are poor blockaders since they cannot attack the squares in front of the pawn without moving off the blockading square. The principle for the attacking side: break the blockade by forcing the blockader to move, either through a direct attack on it or by creating threats that force it to participate elsewhere. Creating multiple passed pawns simultaneously can overwhelm blockade resources since the defender cannot blockade all of them.",
            "metadata": {
                "category": "endgame",
                "subcategory": "passed_pawn",
                "difficulty": "advanced",
                "title": "Blockading Passed Pawns",
            },
        },

        # =====================================================================
        # PAWN WEAKNESSES: ISOLATED, BACKWARD, DOUBLED, HANGING (wiki_pawn_*)
        # =====================================================================
        {
            "id": "wiki_isolated_pawn_dynamic",
            "content": "An isolated pawn (IQP in the center, typically on d4 or d5) has no friendly pawns on adjacent files to defend it, meaning it can only be defended by pieces, which ties them down. However, an isolated pawn also provides compensating advantages: the squares in front of it on both adjacent files (the c- and e-files for a d4 IQP) cannot be occupied by enemy pawns, giving pieces excellent outpost squares and open lines. The IQP creates a dynamic imbalance: the side with the IQP typically has active pieces and attacking chances in the middlegame, while the side against the IQP aims to blockade it and reach a favorable endgame where the pawn becomes a pure weakness. When playing with an IQP, seek trades that keep pieces on the board and maintain attacking possibilities. When playing against an IQP, exchange pieces to reach an endgame and install a blockader on the square in front of the IQP.",
            "metadata": {
                "category": "strategy",
                "subcategory": "pawn_structure",
                "difficulty": "intermediate",
                "title": "Isolated Pawn: Dynamic Compensation",
            },
        },
        {
            "id": "wiki_isolated_pawn_defense",
            "content": "Defending against an isolated queen's pawn (IQP) requires a systematic strategic approach. The core goal is to establish a blockader directly in front of the IQP — ideally a knight on d5 (against d4 IQP) or d6 (against d5 IQP). Once the IQP is blockaded, it becomes a static weakness requiring piece defense, which ties down the opponent's resources. Piece exchanges are generally favorable for the defender: the IQP owner needs active pieces to generate attacking compensation, so exchanging pieces makes the IQP a pure liability. The defender should control the c-file and e-file (the files adjacent to the isolated pawn) with rooks to prevent the IQP owner from gaining space. The endgame conversion is often the decisive phase: if the defender reaches an endgame where the IQP is blockaded and the material is simplified, the IQP is frequently a winning advantage for the defending side. Avoid allowing the IQP to advance and create a passed pawn.",
            "metadata": {
                "category": "strategy",
                "subcategory": "pawn_structure",
                "difficulty": "advanced",
                "title": "Fighting Against the Isolated Pawn",
            },
        },
        {
            "id": "wiki_backward_pawn_weakness",
            "content": "A backward pawn is one that has fallen behind its neighboring pawns and cannot be advanced without being immediately captured, yet cannot be defended by other pawns. The square directly in front of a backward pawn is typically a permanent weakness — a hole that the opponent can occupy with a piece. The backward pawn on c6 or d6 is one of the most common targets in the Sicilian and French Defense structures. The pawn itself can only be defended by pieces, tying them down to passive defense. To exploit a backward pawn, place a rook on the file containing it (creating direct pressure), establish a piece on the square in front of the pawn (the outpost square), and avoid trading pieces that would relieve the defender's burden. The defender's counterplay against a backward pawn usually involves pushing it forward at the right moment — accepting that the pawn structure changes but creating counterplay in return. The backward pawn is especially weak when placed on a half-open file.",
            "metadata": {
                "category": "strategy",
                "subcategory": "pawn_structure",
                "difficulty": "intermediate",
                "title": "Backward Pawn: Exploitation and Defense",
            },
        },
        {
            "id": "wiki_doubled_pawns_impact",
            "content": "Doubled pawns occur when two pawns of the same color occupy the same file, typically the result of a capture. They have both weaknesses and occasional strengths. The weaknesses: doubled pawns cannot defend each other, one of them is usually isolated (the rear pawn cannot be supported by side pawns), they reduce pawn cover and create semi-open files for the opponent, and in the endgame they often count as one effective pawn. The strengths: doubled pawns can control more squares than single pawns (a doubled pawn on f3 and f4 controls multiple squares), they open files for rooks, and in some cases provide extra pawn support for a piece on an outpost. Doubled pawns are most problematic when isolated (the doubled-isolated pawn), when on the same color as your bishop (hampering its mobility), or when they cannot be un-doubled. In the Nimzo-Indian Defense, Black willingly accepts doubled c-pawns for White in exchange for the bishop pair and structural compensation.",
            "metadata": {
                "category": "strategy",
                "subcategory": "pawn_structure",
                "difficulty": "intermediate",
                "title": "Doubled Pawns: Weaknesses and Strengths",
            },
        },
        {
            "id": "wiki_hanging_pawns_theory",
            "content": "Hanging pawns are a pair of adjacent pawns on the c- and d-files (typically c5 and d5 or c4 and d4) that are not supported by other pawns on adjacent files. They are 'hanging' in the sense that they have no lateral pawn support. Hanging pawns represent a dynamic structural tension: they control significant central space and give the pieces good activity, but they can become targets if the opponent establishes piece pressure against both pawns. The side with hanging pawns typically has attacking possibilities and active pieces due to the space advantage; the side against hanging pawns tries to create pressure against both pawns simultaneously, forcing one to advance (becoming isolated) or to remain and be attacked. The critical moment in hanging pawn positions is when one pawn must advance (d5 or c5 push) to relieve the pressure — this changes the pawn structure fundamentally. A well-timed pawn advance can create a passed pawn or open attacking lines, while a mistimed advance weakens the position.",
            "metadata": {
                "category": "strategy",
                "subcategory": "pawn_structure",
                "difficulty": "advanced",
                "title": "Hanging Pawns: Dynamic Tension",
            },
        },
        {
            "id": "wiki_pawn_majority_conversion",
            "content": "A pawn majority is a greater number of pawns on one side of the board compared to the opponent. Pawn majorities are most important in the endgame, where they can be converted into a passed pawn. The principle for converting a pawn majority: advance the pawn that is not opposed first, then push the others forward. For a 3-versus-2 majority on the queenside, the typical plan is to create a passed pawn by advancing two pawns while the third protects. A healthy pawn majority can create a passed pawn; a crippled majority (containing doubled pawns or an isolated pawn) may be unable to create a passed pawn and is not truly an advantage. The minority attack is the counter-strategy: the side with fewer pawns advances them to destroy the opponent's pawn majority by exchanging them, creating weaknesses (isolations, backward pawns) in the larger pawn group rather than trying to match it pawn-for-pawn.",
            "metadata": {
                "category": "endgame",
                "subcategory": "pawn_structure",
                "difficulty": "intermediate",
                "title": "Pawn Majority: Conversion to Passed Pawn",
            },
        },

        # =====================================================================
        # OPEN FILE THEORY (wiki_open_file_*)
        # =====================================================================
        {
            "id": "wiki_open_file_rook",
            "content": "An open file is a file with no pawns of either color, giving rooks unobstructed mobility along it. A half-open file has one pawn (the opponent's), giving a rook control of most of the file but blocked by the enemy pawn. Open files are primary highways for rooks; a rook on an open file penetrates to the 7th or 8th rank and applies direct pressure. The strategic principle: fight for control of open files by placing rooks on them before the opponent does, and then use the file to penetrate. If both sides have rooks on an open file, the first to double rooks (or add the queen behind) gains decisive control. A rook on the 7th rank ('pig') attacks enemy pawns that have not advanced and traps the opposing king on the back rank. Two rooks on the 7th rank are exceptionally powerful. Files adjacent to the open file (half-open files) are also valuable because they provide lanes for attacking enemy pawns. When calculating pawn exchanges, always consider what files will be opened and who benefits.",
            "metadata": {
                "category": "strategy",
                "subcategory": "open_files",
                "difficulty": "beginner",
                "title": "Open Files and Rook Activity",
            },
        },
        {
            "id": "wiki_open_file_control",
            "content": "Controlling an open file requires not just placing a rook on it, but maintaining that control against the opponent's attempts to contest it. If the opponent places a rook on the same file, a rook trade will occur unless one side secures a powerful penetration square on the file. Intrusion squares (outpost squares on the 7th or 8th rank accessible via the open file) are what make open file control valuable. A rook reaching the 7th rank typically wins pawns, attacks the enemy king, and coordinates with the other rook. To seize a file, calculate whether your rook can penetrate or must remain on the file defensively. Files can be opened by pawn exchanges, pawn sacrifices, or by advancing pawns past the midpoint. In the opening, players often deliberately choose pawn structures to open specific files for their rooks — for example, the Sicilian Dragon opens the g-file for Black's rook on g8 after ...g6 and 0-0.",
            "metadata": {
                "category": "strategy",
                "subcategory": "open_files",
                "difficulty": "intermediate",
                "title": "Controlling Open Files",
            },
        },

        # =====================================================================
        # FIANCHETTO THEORY (wiki_fianchetto_*)
        # =====================================================================
        {
            "id": "wiki_fianchetto_structure",
            "content": "A fianchetto is the development of a bishop to the second square of the knight's file (b2 or g2 for White, b7 or g7 for Black) after advancing the adjacent knight's pawn one square. The fianchettoed bishop controls a long diagonal (a1-h8 or h1-a8) and exerts long-range pressure on the center and the opposite wing. The fianchetto creates a specific pawn structure: the g3-Bg2 or b3-Bb2 formation for White (or the mirror for Black) gives the king a solid shelter after castling. The fianchettoed bishop is most powerful when the long diagonal is open or semi-open — it can bear down on central squares like d5, e4, or b7, d5. The weakness of the fianchetto structure is that exchanging the fianchettoed bishop leaves holes along the diagonal (weakened dark or light squares) and exposes the king after castling. The 'anti-fianchetto' strategy involves trading off the fianchettoed bishop to exploit those hole weaknesses.",
            "metadata": {
                "category": "opening",
                "subcategory": "fianchetto",
                "difficulty": "beginner",
                "title": "Fianchetto Structure and Principles",
            },
        },
        {
            "id": "wiki_fianchetto_bishop_exchange",
            "content": "Trading the fianchettoed bishop is one of the most important strategic themes in positions featuring kingside or queenside castling behind a fianchetto. When the fianchettoed bishop is exchanged (particularly by an opponent bishop sacrifice or knight trade), the resulting weakness is the color complex of squares the bishop was guarding. In a Kingside Indian or King's Indian setup, the fianchettoed bishop on g7 guards f6, h6, and the long diagonal. If exchanged, the opponent gains access to f6, potentially planting a knight there or advancing pawns to h6 and g5 without fear. The anti-fianchetto bishop trade is a key motif in the Saemisch King's Indian and various anti-Dragon setups. Defending against this requires either keeping the bishop on the board, blocking the diagonal, or ensuring the resulting weaknesses are compensated by activity elsewhere. When attacking against a fianchetto, try to trade off the defending bishop before launching a pawn storm.",
            "metadata": {
                "category": "strategy",
                "subcategory": "fianchetto",
                "difficulty": "intermediate",
                "title": "Trading the Fianchettoed Bishop",
            },
        },

        # =====================================================================
        # PROPHYLAXIS THEORY (wiki_prophylaxis_*)
        # =====================================================================
        {
            "id": "wiki_prophylaxis_middlegame",
            "content": "Prophylaxis in the middlegame means anticipating the opponent's plans and taking measures to prevent them before they can be executed. Rather than always asking 'what do I want to do?', the prophylactic approach also asks 'what does my opponent want to do, and how can I stop it?' This is a hallmark of modern positional chess. Prophylactic moves often look passive but are in reality preventing powerful counterplay. Common prophylactic measures include: retreating a bishop to prevent a knight fork, placing a rook to prevent an opponent's rook from reaching a key file, advancing a pawn to stop a knight outpost, or moving the king to prevent a back rank weakness. Nimzowitsch and later Petrosian were masters of prophylaxis — Petrosian was particularly known for restricting opponent counterplay so severely that the opponent had no good moves. Prophylaxis requires calculating not just your own plans but visualizing the opponent's ideal position and then making moves to deny it.",
            "metadata": {
                "category": "strategy",
                "subcategory": "prophylaxis",
                "difficulty": "intermediate",
                "title": "Prophylaxis in the Middlegame",
            },
        },
        {
            "id": "wiki_prophylaxis_pawn_breaks",
            "content": "Prophylaxis in pawn structures focuses on preventing the opponent's pawn breaks before they become unstoppable. Every pawn structure has characteristic breaks: in the King's Indian, Black aims for ...d5 or ...c5 breaks; in the French, Black plans ...c5; in the Sicilian, White plans the d4-d5 advance. Preventing these breaks at the right moment is crucial. The prophylactic approach includes: placing pawns or pieces on squares that stop the break, advancing your own pawns to control the key squares, or timing your own pawn advances to preempt the opponent's. If you allow the opponent to execute their thematic pawn break, the resulting position often gives them exactly the counterplay or position they need. For example, in Sicilian structures with d6 and e6 pawns, White must decide when and how to prevent ...d5 — allowing ...d5 often equalizes or gives Black the initiative. Prophylaxis against pawn breaks is a prerequisite for long-term positional pressure.",
            "metadata": {
                "category": "strategy",
                "subcategory": "prophylaxis",
                "difficulty": "advanced",
                "title": "Prophylaxis Against Pawn Breaks",
            },
        },

        # =====================================================================
        # KING ENDGAME THEORY (wiki_king_endgame_*)
        # =====================================================================
        {
            "id": "wiki_opposition_theory",
            "content": "Opposition is a key concept in king and pawn endgames. Two kings are in opposition when they stand on the same rank, file, or diagonal with an odd number of squares between them (direct opposition = 1 square apart). The player who does NOT have to move holds the opposition — the opponent's king must give way. Direct opposition (kings two squares apart on a file or rank) is most important in pawn endgames; the player with the opposition can often penetrate to win enemy pawns. Distant opposition occurs when the kings are separated by 3 or 5 squares on the same line — moving toward the opponent with the distant opposition eventually achieves direct opposition. Diagonal opposition has the kings on the same diagonal with an odd number of squares between them. The key practical application: in K+P vs K endgames, the attacking king must gain opposition to escort the pawn to promotion. The defending king uses opposition to block the path and force a draw.",
            "metadata": {
                "category": "endgame",
                "subcategory": "opposition",
                "difficulty": "beginner",
                "title": "Opposition in King Endgames",
            },
        },
        {
            "id": "wiki_triangulation_technique",
            "content": "Triangulation is a king maneuver used to transfer the move ('waste a tempo') while reaching the same position, effectively passing the burden of the move to the opponent. A king triangulates by taking three moves to travel to a square that could normally be reached in two moves — the extra step allows the player to effectively pass their turn, placing the opponent in zugzwang. Triangulation is only possible when the king has extra space to maneuver in a triangular path that returns it to the starting point with an extra move used. The opponent's king, which can only travel in straight lines to the contested squares, cannot mirror this triangulation and is forced into zugzwang. Triangulation is a decisive weapon in king and pawn endgames where zugzwang is critical. The defending side must recognize when triangulation is possible and either prevent it by controlling the extra squares the king needs or accept the resulting zugzwang.",
            "metadata": {
                "category": "endgame",
                "subcategory": "triangulation",
                "difficulty": "advanced",
                "title": "Triangulation: Tempo Manipulation",
            },
        },
        {
            "id": "wiki_key_squares_concept",
            "content": "Key squares (or critical squares) in king and pawn endgames are squares that, if occupied by the attacking king, guarantee pawn promotion regardless of the defender's best play. For a center or knight's file pawn, the key squares are the three squares two ranks ahead of the pawn. For example, for a pawn on e5, the key squares are d7, e7, and f7 — if White's king reaches any of these squares, the e-pawn queens. For a rook pawn (a or h file), the key squares are only two squares (on the 7th rank for the pawn's file and the adjacent file). The defending king must prevent the attacking king from reaching any key square. The attacking king aims to occupy a key square while the pawn supports it. Knowledge of key squares determines whether positions are theoretically won or drawn even before detailed calculation. A passed pawn on the 6th rank often controls its own key squares, making it immediately decisive.",
            "metadata": {
                "category": "endgame",
                "subcategory": "king_pawn",
                "difficulty": "intermediate",
                "title": "Key Squares in King and Pawn Endgames",
            },
        },

        # =====================================================================
        # ZUGZWANG (wiki_zugzwang_*)
        # =====================================================================
        {
            "id": "wiki_zugzwang_mutual",
            "content": "Zugzwang is a situation where the obligation to move is a disadvantage — any move worsens the player's position. In a full zugzwang, the player would prefer to pass but cannot. In a reciprocal zugzwang (mutual zugzwang), either player is in zugzwang when it is their turn to move — the player to move loses. Zugzwang is most common in king and pawn endgames where every king move loses a pawn or surrenders a critical square. It also appears in certain piece endgames and even the middlegame (though less commonly). The practical implications: when heading into an endgame, calculate not just material but whether your pieces have sufficient 'waiting moves' that don't change the position's character. A position where all your moves are forced deteriorations is zugzwang. The classic weapon to create zugzwang is triangulation, where the king wastes a tempo to transfer the move to the opponent.",
            "metadata": {
                "category": "endgame",
                "subcategory": "zugzwang",
                "difficulty": "intermediate",
                "title": "Zugzwang: Reciprocal and Practical",
            },
        },

        # =====================================================================
        # LUCENA AND PHILIDOR EXPANDED (wiki_lucena_*, wiki_philidor_*)
        # =====================================================================
        {
            "id": "wiki_lucena_bridge",
            "content": "The Lucena position is the most important theoretical position in rook endgames. It arises when the attacking side has its pawn on the 7th rank and its king in front of the pawn, but the rook is cut off on the short side. The winning method is 'building the bridge': the attacking rook gives check to drive the defending king away, then the rook pivots to shield its own king from checks. The technique: 1) Place the rook on the 4th rank (or 5th). 2) Bring the attacking king to the side using the rook as a shield against checks. 3) The defending rook can no longer give perpetual check because the bridge (rook on the 4th rank) intercepts the checks. The Lucena position occurs with any pawn except a rook pawn (h or a file) — the rook pawn is a draw because the defending king can reach the corner. Knowing this position is essential because most won rook endgames eventually transpose into the Lucena.",
            "metadata": {
                "category": "endgame",
                "subcategory": "lucena",
                "difficulty": "intermediate",
                "title": "Lucena Position: Building the Bridge",
            },
        },
        {
            "id": "wiki_lucena_applicability",
            "content": "The Lucena position's significance extends beyond its specific setup — it is the template for winning rook and pawn endgames in general. Any won rook endgame with a passed pawn aims to reach the Lucena position. The path to Lucena requires: advancing the pawn to the 7th rank, positioning the king in front of the pawn, and then using the 'bridge' technique to escort the pawn to promotion. The defensive side, when unable to hold the Philidor position, must understand when Lucena is unavoidable and transition to other defensive resources or accept the loss. A key practical point: many rook endgames that appear lost technically can still be saved if the position does not reach the exact Lucena setup — for example, if the defending king can remain in front of the pawn or the defending rook can operate from behind. The rule of thumb: a rook endgame with an extra pawn is won if it reaches Lucena, drawn if the defender achieves Philidor.",
            "metadata": {
                "category": "endgame",
                "subcategory": "lucena",
                "difficulty": "advanced",
                "title": "When the Lucena Position Applies",
            },
        },
        {
            "id": "wiki_philidor_passive_defense",
            "content": "The Philidor position is the primary drawing technique for the defending side in rook endgames. The defending rook is placed on the 6th rank (or whichever rank the pawn will eventually pass through), cutting off the attacking king. As long as the pawn has not reached the 6th rank, the defending rook stays on the 6th rank. Once the pawn advances to the 6th rank, the defending rook immediately switches to checking the attacking king from behind. This perpetual check (from the short side if necessary) cannot be stopped because the attacking king cannot shelter from checks without advancing the pawn, which the defending rook can block. The Philidor position draws because the defending rook can harass the king endlessly. The key moment is when the defending rook must switch from the 6th rank cutoff to checks — waiting too long means the attacking king can use the pawn as a shield. The Philidor is the most fundamental rook endgame draw and must be known by every serious player.",
            "metadata": {
                "category": "endgame",
                "subcategory": "philidor",
                "difficulty": "intermediate",
                "title": "Philidor Position: Passive Defense",
            },
        },

        # =====================================================================
        # MATING PATTERNS (wiki_mate_*)
        # =====================================================================
        {
            "id": "wiki_smothered_mate",
            "content": "Smothered mate is a checkmate delivered by a knight against a king that is trapped (smothered) by its own pieces. The classic smothered mate sequence begins with a queen sacrifice to lure the enemy king to a corner square where it is surrounded by its own pieces (typically rooks and minor pieces on adjacent squares), and then the knight delivers check on the only square available — a check from which the king cannot escape because every escape square is occupied by its own pieces. The typical sequence involves a series of checks forcing the king to the corner: queen gives check, king moves to corner, then queen sacrifice on the rook, king is forced to take the queen, and the knight delivers the smothered checkmate. The prerequisites: the enemy king is in or near a corner, all escape squares are covered by the opponent's own pieces, and a knight can reach a checking square. Recognizing the smothered mate pattern is important because the sacrificial sequence can look counterintuitive without knowing the final position.",
            "metadata": {
                "category": "tactic",
                "subcategory": "mating_pattern",
                "difficulty": "intermediate",
                "title": "Smothered Mate Pattern",
            },
        },
        {
            "id": "wiki_back_rank_weakness",
            "content": "Back rank weakness occurs when a castled king has no 'luft' (escape square) and is vulnerable to checks and checkmate along the first rank. When all three squares in front of the castled king are occupied by friendly pawns (often f2, g2, h2 for the kingside), a rook or queen check along the back rank (first or eighth rank) cannot be met by the king escaping. The weakest setup is when the king is on g1 with pawns on f2, g2, h2 — a single rook check on the first rank delivers checkmate. Creating luft (advancing h3 or h6) is a prophylactic measure that eliminates back rank vulnerabilities. Back rank weakness can be exploited through deflection: lure away or trade off the piece that is defending the back rank, then deliver the decisive rook check. The back rank theme appears in numerous tactical motifs including decoys, deflections, and sacrifices that remove defenders of the critical square. Always scan for back rank weaknesses when your rooks enter the opponent's position.",
            "metadata": {
                "category": "tactic",
                "subcategory": "mating_pattern",
                "difficulty": "beginner",
                "title": "Back Rank Weakness",
            },
        },
        {
            "id": "wiki_greek_gift_prerequisites",
            "content": "The Greek Gift sacrifice (Bxh7+) is the classic bishop sacrifice on h7 (or h2) against a castled king. Precise prerequisites must be met before executing this sacrifice: (1) A bishop on the b1-h7 diagonal (or b8-h2 diagonal for Black). (2) A knight available to jump to g5 within one or two moves. (3) A queen that can reach h5 or d3 quickly to join the attack. (4) The h7 square must not be overprotected — typically only the king defends it after the bishop captures. (5) The opponent has no effective counterattack or blocking move. After Bxh7+ Kxh7, Ng5+ forces the king to h6 or h8, and Qh5 (to h8 and then Qxf7) or Qd3+ creates a mating attack. The defense ...Kg6 must be evaluated carefully — White needs Qg4 or h4-h5 to continue the attack. If the king can reach safety via Kh6-Kg6, the sacrifice may be insufficient. Always calculate the entire sequence before sacrificing.",
            "metadata": {
                "category": "tactic",
                "subcategory": "greek_gift",
                "difficulty": "intermediate",
                "title": "Greek Gift Sacrifice: Prerequisites",
            },
        },

        # =====================================================================
        # MINORITY ATTACK (wiki_minority_*)
        # =====================================================================
        {
            "id": "wiki_minority_attack_qgd",
            "content": "The minority attack is a strategic plan where the side with fewer pawns on a given wing advances those pawns to attack and undermine the opponent's larger pawn group, creating a weakness (typically an isolated or backward pawn). It is most commonly seen in Queen's Gambit Declined structures where White has two queenside pawns (a- and b-pawns) against Black's three (a-, b-, c-pawns). White advances the b-pawn to b5 and then to b6 or forces bxc6, creating a backward pawn on c6 or an isolated c-pawn. This minority attack is White's standard queenside strategy in the exchange variation of the QGD. The resulting weakness (typically a backward or isolated pawn on c6) becomes a long-term target that White's rooks and pieces can exploit. Black's typical counter-strategy is to activate pieces, seek counterplay on the kingside, or trade off pieces to neutralize the weakness. The minority attack succeeds when White creates a permanent weakness and then exploits it systematically.",
            "metadata": {
                "category": "strategy",
                "subcategory": "minority_attack",
                "difficulty": "advanced",
                "title": "Minority Attack in Queen's Gambit Structures",
            },
        },

        # =====================================================================
        # TEMPO (wiki_tempo_*)
        # =====================================================================
        {
            "id": "wiki_tempo_concept",
            "content": "Tempo refers to a unit of time in chess — one move. Gaining a tempo means forcing the opponent to waste a move responding to a threat rather than pursuing their own plan. Losing a tempo (losing time) means making an unnecessary move that could have been avoided. In the opening, tempo loss is critical: each wasted move allows the opponent to advance their development and seize the initiative. Moving the same piece twice, making unnecessary pawn moves, or retreating pieces all waste tempo. The concept of 'equal tempi' means both sides have developed at the same rate and neither has a time advantage. Tempo advantages convert into concrete advantages when the position requires urgency — a single tempo can decide a race between passed pawns, or be the difference between completing an attack and allowing a defense to be organized. 'Gaining a tempo with check' is a common technique: a check forces a king move, allowing the side giving check to proceed with their plan one move faster.",
            "metadata": {
                "category": "strategy",
                "subcategory": "tempo",
                "difficulty": "beginner",
                "title": "Tempo: Time in Chess",
            },
        },
        {
            "id": "wiki_tempo_initiative",
            "content": "The initiative means having the right to dictate the course of play by making threats that must be answered. When you have the initiative, your opponent spends moves reacting rather than pursuing their own plans. Maintaining the initiative often means continuing to create threats — a player who pauses to consolidate may allow the opponent to equalize. The initiative can be quantified in terms of tempi: if you have a three-move attack and the opponent needs four moves to defend, you have the initiative. Sacrificing material for the initiative is justified when the resulting threats cannot be stopped without further material loss. The initiative must eventually convert into something concrete — material, a passed pawn, a mating attack, or a structural advantage. An initiative that fades without concrete gains is not worth the material sacrificed for it. The first-move advantage in chess is essentially an initiative advantage that must be carefully maintained.",
            "metadata": {
                "category": "strategy",
                "subcategory": "tempo",
                "difficulty": "intermediate",
                "title": "Initiative and Tempo Advantages",
            },
        },

        # =====================================================================
        # PAWN STRUCTURE THEORY (wiki_pawn_structure_*)
        # =====================================================================
        {
            "id": "wiki_hedgehog_structure",
            "content": "The Hedgehog pawn structure is characterized by Black having pawns on a6, b6, d6, and e6 — a compact formation on the 6th rank (for Black) that resembles a hedgehog curled up in defense. This structure arises primarily from Sicilian and English Opening variations. The Hedgehog looks passive but contains tremendous latent energy: Black's pieces are harmoniously placed, and the 'break' moves ...b5 or ...d5 are held in reserve as powerful surprise weapons when the moment is right. The white side typically has more space, but this can become a liability if the pieces become overextended. The Hedgehog requires precise strategic understanding: Black must wait for the right moment to strike with the pawn breaks, and White must prevent those breaks while maintaining useful piece activity. Premature White expansions can be punished by timely ...b5 or ...d5 breaks that immediately create counterplay.",
            "metadata": {
                "category": "strategy",
                "subcategory": "pawn_structure",
                "difficulty": "advanced",
                "title": "Hedgehog Pawn Structure",
            },
        },
        {
            "id": "wiki_maroczy_bind",
            "content": "The Maroczy Bind is a pawn formation where White has pawns on c4 and e4 restricting Black's central pawn advances in Sicilian Defense positions. The pawns on c4 and e4 control d5, preventing Black from establishing a pawn on that key square and limiting Black's central counterplay. Black's position can feel cramped, with little room to maneuver. The bind is most effective when the d5 square remains under permanent control and Black's pieces are restricted. The defender of the Maroczy Bind (Black) must seek counterplay through the d6-pawn advance (...d5 at the right moment), by exchanging pieces to reduce the cramping effect, or by using the b5 advance to challenge the bind. White maintains the bind by keeping pawns on c4 and e4, placing a knight on d5, and avoiding exchanges that would relieve the pressure. The Maroczy Bind is a characteristic motif in the Accelerated Dragon and certain Anti-Sicilian setups.",
            "metadata": {
                "category": "strategy",
                "subcategory": "pawn_structure",
                "difficulty": "advanced",
                "title": "Maroczy Bind Structure",
            },
        },

        # =====================================================================
        # PIECE EXCHANGE PRINCIPLES (wiki_exchange_*)
        # =====================================================================
        {
            "id": "wiki_exchange_bishop_knight",
            "content": "Deciding when to trade bishops for knights (or vice versa) is one of the most important strategic judgments in chess. Knights are superior in closed positions with many pawns blocking lines, particularly when there are good outpost squares for them. Bishops excel in open positions and when there are pawns on both wings, where the bishop's long-range power is fully realized. Key principles: trade your knight for the opponent's bishop when the position will remain closed (pawns locked), because the bishop will be ineffective. Keep your bishop when planning to open the position. A bishop is particularly strong against a knight in a king and pawn endgame with pawns on both wings, because the bishop can quickly transfer from one flank to the other while the knight plods. The 'wrong-colored bishop' concept shows that a bishop can be useless if all pawns are on the opposite color from the bishop. When you have the bishop pair (both bishops), avoid exchanges unless forced — the bishop pair is a long-term positional advantage worth 0.3-0.5 pawns.",
            "metadata": {
                "category": "strategy",
                "subcategory": "piece_exchange",
                "difficulty": "intermediate",
                "title": "When to Trade Bishops for Knights",
            },
        },
        {
            "id": "wiki_exchange_when_to_trade",
            "content": "General piece exchange principles guide when trading is advantageous: trade when you are ahead in material (simplify to a won ending), trade when your pieces are passive and the opponent's are active (exchange active for active or passive for passive), and trade to relieve cramped positions. Avoid trading when you have more space (the opponent's pieces need room to maneuver), when the trade gives the opponent the bishop pair, when you are attacking (you need pieces to press the attack), or when trading leaves weak squares that the opponent can exploit. The 'exchange sacrifice' (rook for bishop or knight) can be positionally motivated: giving up the exchange for a dominant knight on an outpost or to destroy a key defensive piece can be correct. Always evaluate trades in terms of the resulting structure and piece activity, not just material count. A passive rook is often worth less than an active minor piece in certain middlegame positions.",
            "metadata": {
                "category": "strategy",
                "subcategory": "piece_exchange",
                "difficulty": "intermediate",
                "title": "Piece Exchange Principles",
            },
        },

        # =====================================================================
        # ROOK ON 7TH RANK (wiki_rook_seventh_*)
        # =====================================================================
        {
            "id": "wiki_rook_seventh_rank",
            "content": "A rook on the 7th rank (the 'pig') is among the most powerful pieces in chess because it attacks enemy pawns that remain on their starting squares (the 7th rank for Black is Black's 2nd rank) and restricts the enemy king. A rook on the 7th rank attacks the f7, g7, and h7 pawns when they have not advanced, and pins the king to the back rank. Two rooks on the 7th rank are generally sufficient to force checkmate or win significant material. To get a rook to the 7th rank, penetrate via an open file and then slide it along the 7th. The defending side must prevent this penetration by contesting the open file or keeping pawns on the 7th rank defended. If the defending rook is passive on the back rank, the 7th rank rook wins pawns easily. Rook on 7th rank plus a passed pawn is often a winning combination in endgames, as the pawn advances while the rook picks off the remaining enemy pawns.",
            "metadata": {
                "category": "strategy",
                "subcategory": "rook_activity",
                "difficulty": "intermediate",
                "title": "Rook on the 7th Rank",
            },
        },

        # =====================================================================
        # CENTRALIZATION (wiki_centralization_*)
        # =====================================================================
        {
            "id": "wiki_centralization_pieces",
            "content": "Centralization is the principle of placing pieces in or near the center of the board where they control the maximum number of squares and can quickly transfer to any part of the board. A centralized knight on e4 or d5 attacks up to 8 squares and can participate in both kingside attacks and queenside defense. A centralized queen on d4 controls 27 squares; on a1 it controls only 21. The principle of centralization applies throughout all phases: in the opening, develop pieces to central squares (e4, d4, e5, d5, c4, f4); in the middlegame, centralize pieces before launching wing attacks; in the endgame, the king must become active and centralize. A key principle: flank attacks must be prepared by central control — a wing attack launched without central control will be refuted by a central counter. The process of centralizing the king in the endgame is called king activation: the king should advance toward the center as soon as queens are off the board.",
            "metadata": {
                "category": "strategy",
                "subcategory": "centralization",
                "difficulty": "beginner",
                "title": "Centralization of Pieces",
            },
        },
        {
            "id": "wiki_centralization_king_endgame",
            "content": "King centralization in the endgame is not just important — it is mandatory. Once the queens are exchanged and mating threats are minimal, the king becomes a powerful fighting piece that must be activated. A centralized king supports passed pawns, attacks enemy pawns, fights for key squares, and coordinates with rooks and minor pieces. The path to the center should be taken as quickly as possible after entering the endgame. In rook endgames, the king should advance toward the center regardless of whether there are passed pawns, because a centralized king wins pawn races and creates multiple threats. In pawn endgames, the king is the most important piece — its position determines whether positions are won or drawn. The principle 'kings are strong pieces in the endgame' is one of the most important transitions between middlegame and endgame thinking. Players who delay king activation in the endgame often convert winning positions into draws or wins into losses.",
            "metadata": {
                "category": "endgame",
                "subcategory": "centralization",
                "difficulty": "beginner",
                "title": "King Centralization in the Endgame",
            },
        },

        # =====================================================================
        # TWO WEAKNESSES PRINCIPLE (wiki_two_weaknesses_*)
        # =====================================================================
        {
            "id": "wiki_two_weaknesses_principle",
            "content": "The principle of two weaknesses states that a single weakness is usually not enough to win because the defender can concentrate all resources on defending it. To win a positional advantage, the stronger side must create a second weakness on a different part of the board, forcing the defender to defend two problems simultaneously. The typical method: press against the first weakness to tie down the defender's pieces, then open a second front (often on the opposite wing) to create a second weakness that the already-committed defensive pieces cannot cover. Classic execution: create a backward pawn or isolated pawn on one side, press against it with rooks, then break through with a pawn advance on the other wing to create a passed pawn or a second target. The two weaknesses principle explains why endgames with an extra pawn but a single weakness often end in draws — the defending side successfully blockades or holds one weakness indefinitely. Against two weaknesses, there is no defensive plan that saves both.",
            "metadata": {
                "category": "strategy",
                "subcategory": "endgame_strategy",
                "difficulty": "advanced",
                "title": "The Principle of Two Weaknesses",
            },
        },
        {
            "id": "wiki_two_weaknesses_creating",
            "content": "Creating a second weakness requires patience and precise technique. The standard method involves first maximizing pressure on the existing weakness to fix the opponent's pieces in passive defensive positions. Once the defender is committed to defending the first weakness, a pawn lever or piece maneuver on the opposite flank creates a second front. Key tools for creating the second weakness: a pawn break on the other wing (e.g., h4-h5 to open the h-file), an unexpected piece sacrifice to create a passed pawn, or a king march to the other side. The defending side should actively seek counterplay to avoid being squeezed between two weaknesses — passive defense against two weaknesses is usually hopeless. Creating activity, offering piece trades, and seeking pawn breaks to transform the structure are the defensive resources. The principle applies at all levels: even beginners should recognize that fixing one weakness is easier than defending two.",
            "metadata": {
                "category": "strategy",
                "subcategory": "endgame_strategy",
                "difficulty": "advanced",
                "title": "Creating the Second Weakness",
            },
        },

        # =====================================================================
        # OVERLOADING (wiki_overloading_*)
        # =====================================================================
        {
            "id": "wiki_overloading_defender",
            "content": "Overloading a defender means giving one piece too many tasks to perform simultaneously — the piece cannot adequately fulfill all its defensive duties, and one of the targets it was supposed to protect becomes vulnerable. A typical overloading scenario: a rook defends both a back rank weakness and a critical pawn. By attacking both targets, the defending rook cannot protect both, and one falls. Identifying overloaded pieces requires asking: 'What is this piece responsible for? Can I force it to give up one duty?' Common overloading tactics include: sacrificing to divert the overloaded piece, attacking both targets in sequence to show the defender cannot cover both, and creating additional threats that compound the overloaded piece's burden. Overloading is different from deflection — in deflection, you lure a piece away; in overloading, the piece must choose between two or more duties it was already performing. The remedy for overloaded pieces is to bring up additional defenders or to reorganize the defensive structure to share the burden.",
            "metadata": {
                "category": "tactic",
                "subcategory": "overloading",
                "difficulty": "intermediate",
                "title": "Overloading a Defender",
            },
        },
        {
            "id": "wiki_overloading_queen",
            "content": "The queen is the piece most commonly overloaded because it is often used to defend multiple pieces and squares simultaneously. When the queen is overloaded, a single tactical blow can unravel the entire defensive position. Classic queen overloading: the queen defends both a knight and a back rank — attacking both targets forces the queen to abandon one. The queen overloaded as both attacker and defender is an even more acute problem: if the queen is the main attacking piece but also defends a key square, forcing it to defend removes the attack. When your own queen is potentially overloaded, distribute defensive duties to rooks and minor pieces wherever possible. When opponent's queen is overloaded, calculate sequences that force it to choose between two losing options. Queen overloading motifs are common in combinations involving back rank threats combined with piece attacks on the same queen.",
            "metadata": {
                "category": "tactic",
                "subcategory": "overloading",
                "difficulty": "intermediate",
                "title": "Queen Overloading Patterns",
            },
        },

        # =====================================================================
        # DEFLECTION (wiki_deflection_*)
        # =====================================================================
        {
            "id": "wiki_deflection_tactic",
            "content": "Deflection (also called decoy or lure) is a tactic that draws an enemy piece away from a defensive duty by offering it a tempting capture, forcing it to abandon its defensive role. The deflected piece takes the bait (or is forced to by a check or threat), and the previously defended square or piece becomes vulnerable. Common deflection patterns: a rook sacrifice on a defended square forces the opponent's queen to capture it, deflecting the queen from defending a checkmate. A pawn promotion deflects a piece guarding a key square. Deflection differs from overloading in that the deflected piece can only do one thing at a time — move to capture — and in doing so it leaves another duty unfulfilled. Deflection is also the principle behind many queen sacrifices: offer the queen such that taking it deflects the defending piece, and then checkmate follows on the now-undefended square. Every successful deflection is based on correctly identifying which piece is the key defender and what can lure it away.",
            "metadata": {
                "category": "tactic",
                "subcategory": "deflection",
                "difficulty": "intermediate",
                "title": "Deflection Tactics",
            },
        },

        # =====================================================================
        # INTERFERENCE (wiki_interference_*)
        # =====================================================================
        {
            "id": "wiki_interference_tactic",
            "content": "Interference is a tactic that places a piece on a square that interrupts the communication between two enemy pieces, cutting off their mutual defense or creating separate targets. By inserting a piece between two defending pieces, the attacker disconnects them — one can no longer support the other. For example, placing a piece between an enemy rook and bishop on the same diagonal or file prevents them from covering each other. Interference is a subtler tactic than most because the interfering piece often can be captured, but capturing it may make things worse (a piece sacrifice to create an interference). The interposing piece may also control important squares in its new position while disrupting enemy coordination. Interference is particularly effective when enemy pieces are lined up on the same file, rank, or diagonal and mutually dependent on their connection. Recognizing interference opportunities requires visualizing how enemy pieces coordinate and asking whether a forcing piece insertion could disrupt that coordination.",
            "metadata": {
                "category": "tactic",
                "subcategory": "interference",
                "difficulty": "advanced",
                "title": "Interference Tactics",
            },
        },

        # =====================================================================
        # PAWN PROMOTION TACTICS (wiki_promotion_*)
        # =====================================================================
        {
            "id": "wiki_promotion_tactics",
            "content": "Pawn promotion tactics leverage the threat of a pawn reaching the 8th rank to win material or force checkmate. The promotion threat can be used as a distraction (diverting enemy pieces to stop the pawn), as a direct winning line, or as a zwischenzug in combination sequences. Underpromotion — promoting to a rook, bishop, or knight instead of a queen — is a key tactic when queening would result in stalemate, or when a knight promotion delivers immediate check or fork. The 'fork of the new queen' is a danger to watch for: promoting to a queen that can be immediately forked or pinned. Common promotion themes: a passed pawn advances while supported by the king; a pawn sacrifice creates a passed pawn; a queening threat forces the opponent to sacrifice material to stop it. In endgames, the race to promote a pawn while preventing the opponent's promotion is a key strategic theme resolved by tempo counts (the 'rule of the square') and king position.",
            "metadata": {
                "category": "tactic",
                "subcategory": "promotion",
                "difficulty": "beginner",
                "title": "Pawn Promotion Tactics",
            },
        },
        {
            "id": "wiki_underpromotion",
            "content": "Underpromotion is the act of promoting a pawn to a rook, bishop, or knight instead of a queen. While promoting to a queen is almost always the strongest choice, underpromotion to a knight is the most common exception because a knight can deliver check in positions where a queen cannot. Knight underpromotion is the solution to stalemate avoidance: if promoting to a queen would stalemate the opponent (a draw), promoting to a rook or knight instead wins. Knight underpromotion delivers check in unique patterns due to the knight's L-shaped movement — a new knight on the promotion square may simultaneously fork the enemy king and another piece. Bishop underpromotion is extremely rare but can occur in stalemate avoidance or specific fortress scenarios. Rook underpromotion avoids stalemate more cleanly than a queen in some positions (keeping the rook's linear movement without the queen's diagonal reach). Always check whether promotion to a queen stalemates before executing.",
            "metadata": {
                "category": "tactic",
                "subcategory": "promotion",
                "difficulty": "intermediate",
                "title": "Underpromotion: When Not to Queen",
            },
        },

        # =====================================================================
        # FORTRESS POSITIONS (wiki_fortress_*)
        # =====================================================================
        {
            "id": "wiki_fortress_endgame",
            "content": "A fortress is a defensive structure in an endgame where the defending side, despite being materially behind, can draw by creating an impenetrable defensive perimeter that the attacking side cannot break through. Fortress positions are typically created when the attacking side has a queen or rook but the defending king and piece combination can create a position where no entry is possible. Classic fortress examples: queen versus rook with the right defensive setup (the defending king and rook create a fortress where the queen cannot penetrate), or rook versus bishop where the bishop controls the corner the rook pawn must promote on. Key fortress principles: place the defending king and pieces on the right squares, repeat moves if the opponent cannot make progress, and avoid any pawn moves that create new weaknesses. The attacking side must look for fortress breaches — forcing moves that disrupt the defensive arrangement. A perfect fortress is theoretically drawn even with large material disadvantages.",
            "metadata": {
                "category": "endgame",
                "subcategory": "fortress",
                "difficulty": "advanced",
                "title": "Fortress Positions in Endgames",
            },
        },

        # =====================================================================
        # STALEMATE TRAPS (wiki_stalemate_*)
        # =====================================================================
        {
            "id": "wiki_stalemate_traps",
            "content": "Stalemate is a draw that occurs when the player to move has no legal moves and is not in check. In a completely lost position, the defending side can attempt stalemate traps to save the game: sacrifice all remaining pieces so the opponent must take them, leaving the king with no legal moves. Common stalemate traps: in queen versus pawn on the 7th rank endings, the defending king can be stalemated if the stronger side is not careful about which pawn is on the 7th (a or c file queen endings are drawn because the defending king can reach the corner). A queen versus rook pawn on the 7th: if the king is on a8 and the pawn is on a7, the king is already in the corner and cannot be mated by the queen without giving stalemate. In pawn endgames, the defending side can sacrifice pawns to create a position where the king has no legal moves once all pawns are captured. Awareness of stalemate traps is essential for both sides — the stronger side must avoid them, the weaker side must seek them.",
            "metadata": {
                "category": "endgame",
                "subcategory": "stalemate",
                "difficulty": "intermediate",
                "title": "Stalemate Traps and Avoidance",
            },
        },

        # =====================================================================
        # BREAKTHROUGH PAWN SACRIFICE (wiki_breakthrough_*)
        # =====================================================================
        {
            "id": "wiki_breakthrough_sacrifice",
            "content": "The breakthrough pawn sacrifice is a tactic where a pawn is sacrificed to create a passed pawn from a group of pawns facing opposing pawns. With three pawns against three pawns in mutual blockade, one side can sacrifice one pawn to break through and create a passed pawn. The typical setup requires three pawns lined up against three opposing pawns on an open wing. The breakthrough works as follows: advance the most advanced pawn into enemy territory where it must be captured, then advance one of the other two pawns to create a passed pawn that cannot be stopped. The opposing side's three pawns can only capture one pawn, leaving the other two to promote. This tactic is particularly important in king and pawn endgames where both sides have equal material elsewhere — the breakthrough pawn sacrifice can be the decisive element. Always examine breakthrough possibilities in pawn races.",
            "metadata": {
                "category": "endgame",
                "subcategory": "pawn_tactics",
                "difficulty": "intermediate",
                "title": "Breakthrough Pawn Sacrifice",
            },
        },

        # =====================================================================
        # TARRASCH RULE / ROOK ENDGAME PRINCIPLES (wiki_rook_endgame_*)
        # =====================================================================
        {
            "id": "wiki_tarrasch_rule",
            "content": "Tarrasch's rule states that rooks should be placed behind passed pawns — both your own and the opponent's. When placed behind your own passed pawn, the rook gains power as the pawn advances (the rook's influence increases as the pawn moves further away). When placed behind the opponent's passed pawn, the rook controls it from a distance and prevents it from advancing freely. The rule applies most forcefully in rook endgames where pawn advancement is the decisive factor. A rook attacking a passed pawn from the side (a 'passive rook') is significantly weaker because as the pawn advances, the rook loses influence. The rook behind the pawn always controls more squares. Practical application: before selecting a rook move in an endgame, check whether placing the rook behind the passed pawn (yours or opponent's) is possible. The Tarrasch rule is one of the most reliable guidelines in rook endgames.",
            "metadata": {
                "category": "endgame",
                "subcategory": "rook_endgame",
                "difficulty": "beginner",
                "title": "Tarrasch Rule: Rooks Behind Passed Pawns",
            },
        },
        {
            "id": "wiki_rook_endgame_active_passive",
            "content": "Active versus passive rook defense is the central question in rook endgames. Passive defense involves the rook staying on a rank or file to prevent the opposing king from advancing, but this strategy typically loses because the attacking side can always create zugzwang or breakthrough situations. Active defense means constantly harassing the opponent with checks, attacking enemy pawns, and maintaining the rook's mobility. The Philidor position demonstrates successful passive defense — but it only works at a specific moment (before the pawn reaches the 6th rank), after which active checking defense takes over. The Lucena position shows why passive defense ultimately fails: the attacking rook on the 4th rank screens the king from checks, neutralizing the defensive rook's checking ability. General rule: when defending rook endgames, prefer active counterplay (checking the king, attacking pawns from behind) to passive waiting. A rook that gives perpetual check is worth far more than a rook sitting passively.",
            "metadata": {
                "category": "endgame",
                "subcategory": "rook_endgame",
                "difficulty": "intermediate",
                "title": "Rook Endgame: Active vs Passive Defense",
            },
        },

        # =====================================================================
        # KING SAFETY (wiki_king_safety_*)
        # =====================================================================
        {
            "id": "wiki_king_safety_structure",
            "content": "King safety depends on the pawn shelter in front of the castled king, the presence of defensive pieces, and the absence of enemy pieces near the king. The three key factors: (1) Pawn shelter integrity — pawns on f2, g2, h2 (for kingside castling) form the primary shield; any advance or exchange of these pawns creates weaknesses. (2) Absence of enemy pieces — every enemy piece that can approach the king increases the danger; removing attacking pieces through exchanges reduces mating threats. (3) Defensive piece coordination — pieces that can quickly return to defend the king are more valuable in unsafe positions. Common king safety weaknesses: the g2 (or g7) pawn advance to g3 weakens f3 and h3; the h2-h3 pawn advance weakens g3; trading the fianchettoed bishop leaves a weakened diagonal. Evaluating king safety requires counting the number of attacking pieces versus defensive resources, not just looking at the pawn structure.",
            "metadata": {
                "category": "strategy",
                "subcategory": "king_safety",
                "difficulty": "intermediate",
                "title": "King Safety: Pawn Shelter and Defense",
            },
        },
        {
            "id": "wiki_king_safety_attack",
            "content": "Attacking a weakened king requires coordination between pieces and pawns. The attacking principles: (1) Open lines toward the king — open files, diagonals, and ranks become highways for attacking pieces. (2) Sacrifice to rip open shelter — a piece sacrifice on h6, g7, or f7 destroys pawn shelter and exposes the king. (3) Bring all available pieces — an attack with three pieces versus two defenders usually wins. (4) Maintain initiative — once the attack begins, don't pause to consolidate; keep creating threats faster than the opponent can handle them. (5) Do not allow counterplay — an attack that exposes your own king can backfire if the opponent has equal attacking resources. The general rule: attack where you have more pieces. Count the number of pieces you can bring to the kingside and compare with the opponent's defensive pieces. A three-to-two attacker advantage in a confined king position is typically winning.",
            "metadata": {
                "category": "middlegame",
                "subcategory": "king_safety",
                "difficulty": "intermediate",
                "title": "Attacking a Weakened King",
            },
        },

        # =====================================================================
        # BISHOP AND KNIGHT CHECKMATE (wiki_bnk_*)
        # =====================================================================
        {
            "id": "wiki_bishop_knight_checkmate",
            "content": "The bishop and knight checkmate is the most difficult basic checkmate to execute, requiring deep understanding of how these two pieces cooperate. The key insight: the king must be driven to a corner of the same color as the bishop — only in those corners can checkmate be delivered. The procedure involves three phases: (1) Centralize both pieces and drive the enemy king toward a corner. (2) Maneuver the king to the edge of the board, then toward the correct-colored corner. (3) Use the 'W maneuver' or systematic technique to coordinate the bishop, knight, and attacking king to force the defending king into the mating corner. The W maneuver uses the knight to control squares the bishop cannot reach, covering all escape routes. A common error is allowing the king to escape to the wrong-colored corner (opposite color from the bishop), requiring another cycle to drive it to the correct corner. With perfect play, the checkmate is forced in at most 34 moves.",
            "metadata": {
                "category": "endgame",
                "subcategory": "basic_checkmate",
                "difficulty": "advanced",
                "title": "Bishop and Knight Checkmate",
            },
        },

        # =====================================================================
        # CHESS STRATEGY CONCEPTS (wiki_strategy_*)
        # =====================================================================
        {
            "id": "wiki_strategy_imbalances",
            "content": "Chess strategy revolves around creating and exploiting imbalances — positional differences between the two sides that are not directly about material count. Key imbalances include: pawn structure differences (isolated pawns, passed pawns, pawn majorities), piece quality differences (good bishop vs. bad bishop, active rook vs. passive rook, strong knight on outpost vs. limited knight), king safety differences, space advantages, development leads, and open file control. The player who correctly identifies the imbalances in a position and plays accordingly gains a strategic advantage. With an isolated pawn, the correct plan is to generate dynamic piece activity before simplification; against it, simplify and blockade. Every strategic decision should be driven by the concrete imbalances in the position, not abstract principles. The question 'what is the imbalance?' is the starting point for every strategic assessment.",
            "metadata": {
                "category": "strategy",
                "subcategory": "strategy_fundamentals",
                "difficulty": "intermediate",
                "title": "Strategic Imbalances in Chess",
            },
        },
        {
            "id": "wiki_strategy_plan_formation",
            "content": "Forming a strategic plan requires a methodical assessment of the position. The assessment process: (1) Evaluate material balance and piece quality. (2) Assess king safety for both sides. (3) Examine pawn structure — identify weaknesses, strengths, and potential pawn breaks. (4) Evaluate piece activity — which pieces are active, which are passive, and how to activate passive pieces. (5) Consider open files, diagonals, and outpost squares. From this assessment, identify the key imbalances and form a plan that either exploits your advantages or neutralizes opponent's advantages. A plan should be specific: not 'attack the kingside' but 'double rooks on the e-file, transfer the knight to d5, then push f4-f5 to open the f-file.' Plans must be flexible — be ready to change plans when the opponent makes unexpected moves. Every move should serve the plan or respond to an immediate threat.",
            "metadata": {
                "category": "strategy",
                "subcategory": "strategy_fundamentals",
                "difficulty": "intermediate",
                "title": "Strategic Plan Formation",
            },
        },
        {
            "id": "wiki_strategy_space",
            "content": "Space advantage means controlling more squares than the opponent, typically through an advanced pawn center. A space advantage restricts the opponent's pieces to cramped positions while giving your own pieces more mobility and more squares to occupy. With a space advantage, avoid exchanging pieces — the more pieces remain, the greater the cramping effect. With less space, seek piece exchanges to open the position and reduce the cramping effect. The key strategic questions with a space advantage: how to convert the space into a concrete advantage (open files, pawn breaks, piece infiltration), and how to prevent the opponent from creating counterplay with pawn breaks. The enemy's thematic pawn break should be prevented prophylactically. Space advantages are not permanent — a well-timed pawn break by the cramped side can dissolve them. A space advantage without a plan to convert it into something concrete often evaporates as the position simplifies.",
            "metadata": {
                "category": "strategy",
                "subcategory": "space",
                "difficulty": "intermediate",
                "title": "Space Advantage Strategy",
            },
        },

        # =====================================================================
        # CHESS TACTICS CONCEPTS (wiki_tactics_*)
        # =====================================================================
        {
            "id": "wiki_tactics_combination",
            "content": "A tactical combination is a sequence of forcing moves (usually including at least one sacrifice) that leads to a concrete advantage: checkmate, material gain, or positional improvement. Combinations rely on specific tactical themes: pins, forks, skewers, discovered attacks, deflections, and sacrifices. The key to executing combinations is calculation accuracy — you must see the entire sequence to the end before starting. Combinations typically begin with a forcing move (check, capture, or threat) that limits the opponent's responses, then continue forcing the opponent along a predetermined path to the winning outcome. Identifying combinations requires recognizing tactical patterns: connected pieces that can be attacked, overloaded defenders, back rank weaknesses, exposed kings. A combination that 'just works' often has a deep preparatory phase where the tactical preconditions were created strategically. The ability to calculate combinations accurately is the most essential concrete skill in chess.",
            "metadata": {
                "category": "tactic",
                "subcategory": "tactics_fundamentals",
                "difficulty": "intermediate",
                "title": "Tactical Combinations",
            },
        },
        {
            "id": "wiki_tactics_calculation",
            "content": "Calculation in chess means the process of mentally evaluating a sequence of moves and counter-moves to determine the outcome. Accurate calculation requires: (1) Candidate move generation — identify all forcing moves (checks, captures, major threats). (2) Tree pruning — eliminate obviously bad candidates early. (3) Concrete move order — evaluate the most forcing line first (checks before captures before threats). (4) Horizon awareness — know when to stop calculating and evaluate the resulting position. Common calculation errors: forgetting opponent's defensive resources, underestimating zwischenzugs, missing quiet but critical defensive moves, and overconfident pattern recognition that skips verification. The CCTV heuristic for candidate generation: Checks, Captures, Threats, Vital defensive moves. When calculating complex positions, first look for checks and forcing captures before considering quieter moves. Every calculation should be verified at least once before executing.",
            "metadata": {
                "category": "tactic",
                "subcategory": "tactics_fundamentals",
                "difficulty": "intermediate",
                "title": "Calculation Technique",
            },
        },

        # =====================================================================
        # ENDGAME PRINCIPLES (wiki_endgame_principles_*)
        # =====================================================================
        {
            "id": "wiki_endgame_rook_pawn",
            "content": "Rook and pawn versus rook is the most common endgame in practical play, and it is frequently drawn despite the extra pawn. The outcome depends on the position of the kings, the type of pawn, and which side achieves the Lucena or Philidor position. General rules: (1) A rook pawn (a or h file) is always a draw if the defending king can reach the corner in front of the pawn — the attacking side cannot drive the king out of the corner without stalemating it. (2) A center pawn (d or e file) is typically won if the attacker achieves the Lucena position. (3) The cut-off rule: if the defending king is cut off by 3 or more files from the pawn, the attacker typically wins. (4) The Philidor defense draws as long as the defending rook switches from rank defense to checking the king at the right moment. (5) An active defensive rook on the long side of the king (the side with more files) harasses the attacker with checks and is harder to neutralize than a rook on the short side.",
            "metadata": {
                "category": "endgame",
                "subcategory": "rook_pawn",
                "difficulty": "intermediate",
                "title": "Rook and Pawn vs Rook Endgame",
            },
        },
        {
            "id": "wiki_endgame_principles_general",
            "content": "The general principles of endgame play form a foundation for converting advantages. (1) Activate the king — the king becomes a powerful piece in the endgame and must march toward the center or the action. (2) Rooks belong behind passed pawns (Tarrasch's rule). (3) Create a passed pawn or prevent the opponent's passed pawn. (4) Eliminate the opponent's counterplay before advancing. (5) In material-up endgames, simplify but retain winning winning material — trade pieces (not pawns) to reduce the opponent's defensive resources. (6) The outside passed pawn diverts the opposing king. (7) King and pawn endgames: know key squares, opposition, and triangulation. (8) In two rooks vs. queen endings, the rooks typically draw or win if they coordinate effectively. These principles do not guarantee victory but form the procedural backbone of endgame technique that prevents avoidable errors.",
            "metadata": {
                "category": "endgame",
                "subcategory": "endgame_principles",
                "difficulty": "beginner",
                "title": "General Endgame Principles",
            },
        },
    ]

    return documents
