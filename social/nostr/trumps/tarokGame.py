import argparse
import random
import secrets
import string
import traceback
import sys
import re
import os.path
import json
import time

DATA_FOLDER = "";

HELP_STR = "/start - Start a new Tarok game\n";
HELP_STR += "/join - Join an existing game ( optionally pass Game-ID )\n";
HELP_STR += "/play - Play a card, or fold\n";
HELP_STR += "/fold - End game ( optionally pass Game-ID )\n";
HELP_STR += "/hand - Get a player's hand ( optionally pass Game-ID )\n";
HELP_STR += "/state - Get the game state ( optionally pass Game-ID )\n";
HELP_STR += "/winner - Get the winner of a game ( optionally pass Game-ID )\n";
HELP_STR += "/list - List available games with players\n";
HELP_STR += "/help - This help string\n\n";
HELP_STR += "The Tarok card game, adapted for 2 players, using a 78 card deck:\n"
HELP_STR += "- Play the same suited card as your opponent, else play a trump card ( cards numbered I to XXI & the Fool )\n"
HELP_STR += "- If a player cannot make a move they lose the game\n"
HELP_STR += "- The player with the most valued cards, wins the round.\n"

MAX_GAMES = 20

ERROR_FINISH_OTHER_GAME = "Finish Other Game."
ERROR_JOIN_A_GAME = "Join a Game, Instead."
ERROR_GAME_ID_NONE = "No Game ID."
ERROR_GAME_ID_INVALID = "Invalid Game ID."
ERROR_CARD_NONE = "No Card Selected."
ERROR_GAME_FINISHED = "The Game Has Ended."
ERROR_PLAYER_FOLDED = "The Other Player Folded."
ERROR_PLAYER_NOT_TURN = "The Other Player's Turn."
MSG_WON = "You Won";
MSG_OK = "OK";
MSG_LOST = "You Lost";
MSG_CARDS_PLAYED = "Cards Played";
                 
#def print_played_cards(self, gameID):
#def player_hand( self, gameID , player ):
#def player_turn( self, gameID ):
#def player_name(self, gameID, which ):
#def games_get( self );
#def game_start(self, name ):
#def game_join(self, name, gameID ):
#def game_play( self, name, gameID, cardIndex ):
#def game_evaluate( self, gameID ):
#def game_end( self, gameID ):
#def game_played_cards(gameID);
#def game_is_open(self, gameID):

class Game():

    HAND_SIZE = 5
    CARDS = list(range(0, 78))  # Equivalent to [0,1, 2, ..., 73]
    
    CARD_SUIT_SIZE = 14;
    CARD_CLUB_ACE = 0;
    CARD_DIAMOND_ACE = 14;
    CARD_HEART_ACE = 28;
    CARD_SPADE_ACE = 42;
    CARD_FOOL = 56;
    CARD_DECK_SIZE = 78;

    GAMES_AVAILABLE = {};
    GAMES_OPEN = {};
    GAMES_ENDED = {};
    _path_games_available = DATA_FOLDER+"_games_available.json";
    _path_games_open = DATA_FOLDER+"_games_open.json";
    _path_games_ended = DATA_FOLDER+"_games_ended.json";

    def __init__(self):
        if os.path.exists( self._path_games_available ):
            with open( self._path_games_available ,'r' ) as file:
                self.GAMES_AVAILABLE = json.load( file );
        if os.path.exists( self._path_games_open ):
            with open( self._path_games_open ,'r' ) as file:
                self.GAMES_OPEN = json.load( file );
        if os.path.exists( self._path_games_ended ):
            with open( self._path_games_ended ,'r' ) as file:
                self.GAMES_ENDED = json.load( file );

    def get_game_ids_by_player( self, player_name):
        game_ids = []
        for game_id, game_data in self.GAMES_OPEN.items():
            if ( game_data["player1"]["name"] == player_name or 
                game_data["player2"]["name"] == player_name ):
                game_ids.append(game_id)
        return game_ids


    def _random_string(self, length=6):
        # Non-ambiguous characters (avoiding visually similar characters)
        characters = "ABCDEFGHJKLMNPQRSTUVWXYZabcdefghjkmnpqrstuvwxyz23456789"
        return ''.join(secrets.choice(characters) for _ in range(length))

    def _store_new_available_game( self, gameID, name, hand , remainder ):
        self.GAMES_AVAILABLE[ gameID ] = { "player1": { "name": name , "hand": hand } , "remainder" : remainder };
        with open( self._path_games_available,'w') as f:
            json.dump( self.GAMES_AVAILABLE, f , default=str );

    def _store_house_keeping(self):
        now = time.time()
        fourWeeks = 2419200  # 4 weeks in seconds
        oldest = None
        oldest_key = None
        for gameID, gameData in self.GAMES_OPEN.items():
            game_timestamp = gameData.get("timestamp", 0)  # Retrieve the timestamp
            if now - game_timestamp > fourWeeks:
                # Update oldest if this game is older than the current oldest
                if oldest is None or game_timestamp < oldest:
                    oldest = game_timestamp
                    oldest_key = gameID
        if None != oldest_key:
            o = dict( self.GAMES_OPEN[ oldest_key ] );
            del self.GAMES_OPEN[ oldest_key ];
            with open( self._path_games_available,'w') as f:
                json.dump( self.GAMES_AVAILABLE, f , default=str );
            return oldest_key , o;
        else:
            return None, None


    def _store_open_game( self, gameID, name, hand ):
        try:
            gameData = self.GAMES_AVAILABLE[ gameID ];
            if name == gameData["player1"]["name"]:
                raise Exception("Invalid Player");
            self.GAMES_OPEN[ gameID ] = {
                    "player1": { "name": gameData["player1"]["name"], "hand": gameData["player1"]["hand"], "played":[] },
                    "player2": { "name": name, "hand": hand, "played": [] },
                    "turn" : random.choice(["player1", "player2"]),
                    "played" : [],
                    "timestamp" : time.time()
                };
            self._store_del_game( gameID );
            with open( self._path_games_open,'w') as f:
                json.dump( self.GAMES_OPEN, f , default=str );
        except:
            traceback.print_exc();

    def _store_play_game( self, gameID, name, card ):
        self.GAMES_OPEN[ gameID ]["turn"] = "player2" if self.GAMES_OPEN[ gameID ]["turn"] == "player1" else "player1";
        
        if ( name != self.GAMES_OPEN[ gameID ]["player1"]["name"]
            and name != self.GAMES_OPEN[ gameID ]["player2"]["name"] ):
            raise Exception("Invalid Player");
        
        player = "player1" if name == self.GAMES_OPEN[ gameID ]["player1"]["name"] else "player2";
        
        if card not in self.GAMES_OPEN[ gameID ][ player ]["hand"]:
            raise Exception("Invalid Play");
        
        self.GAMES_OPEN[ gameID ][ "played" ].append( card );
        self.GAMES_OPEN[ gameID ][ player ]["hand"].remove( card );
        self.GAMES_OPEN[ gameID ][ player ]["played"].append( card );
        with open( self._path_games_open,'w') as f:
            json.dump( self.GAMES_OPEN, f , default=str );
 
    def _store_del_game( self, gameID ):
        del self.GAMES_AVAILABLE[ gameID ];
        with open( self._path_games_available,'w') as f:
            json.dump( self.GAMES_AVAILABLE , f , default=str );

    def _play_validate(self, lastCard, card ):
        if ( card >= self.CARD_FOOL and card < self.CARD_DECK_SIZE ):
            return True;
        elif ( lastCard >= self.CARD_CLUB_ACE and lastCard < self.CARD_DIAMOND_ACE ):
            # Clubs
            return True;
        elif ( lastCard >= self.CARD_DIAMOND_ACE and lastCard < self.CARD_HEART_ACE ):
            # Diamonds
            return True
        elif ( lastCard >= self.CARD_HEART_ACE and lastCard < self.CARD_SPADE_ACE ):
            # Hearts
            return True;
        elif ( lastCard >= self.CARD_SPADE_ACE and lastCard < self.CARD_FOOL ):
            # Spade
            return True;
        return False;

    def _store_get_game_data( self, gameID ):
        if gameID not in self.GAMES_OPEN:
            raise Exception("Invalid GameID");
        return self.GAMES_OPEN[ gameID ];
    
    def _store_get_finished_game_data( self, gameID ):
        if gameID not in self.GAMES_ENDED:
            raise Exception("Invalid GameID");
        return self.GAMES_ENDED[ gameID ];
    
    def _store_finish_game( self, gameID ):
        try:
            gameData = self._store_get_game_data( gameID );
            self.GAMES_ENDED[ gameID ] = gameData;
            del self.GAMES_OPEN[ gameID ];
            with open( self._path_games_open,'w') as f:
                json.dump( self.GAMES_OPEN , f , default=str );
            
            old_games = [];
            fourWeeks = 2419200  # 4 weeks in seconds
            for gameID, gameData in self.GAMES_ENDED.items():
                game_timestamp = gameData.get("timestamp", 0)  # Retrieve the timestamp
                now = time.time()
                if now - game_timestamp > fourWeeks:
                    old_games.append( gameID );
            for v in old_games:
                del self.GAMES_ENDED[ v ];

            with open( self._path_games_ended,'w') as f:
                json.dump( self.GAMES_ENDED , f , default=str );
            
        except:
            traceback.print_exc()
    #####################################################

    def game_is_open(self, gameID):
        return ( gameID in self.GAMES_OPEN );
    
    def game_played_cards(self, gameID):
        if gameID not in self.GAMES_OPEN:
            raise Exception("Invalid GameID")
        gameData = self._store_get_game_data(gameID)
        return gameData["played"]
        
    def print_played_cards(self, gameID):
        if gameID not in self.GAMES_OPEN:
            raise Exception("Invalid GameID")
        
        gameData = self._store_get_game_data(gameID)
        turn = gameData["turn"]
        
        played1 = gameData["player1"]["played"]
        played2 = gameData["player2"]["played"]
        
        # Identify the longest array
        if len(played1) >= len(played2):
            first, second = played1, played2
        else:
            first, second = played2, played1

        played_order = []

        # Alternate starting with the last card of the longest array
        max_len = max(len(first), len(second))
        for i in range(max_len):
            if i < len(first):
                played_order.append(self.TAROT_ASCII[first[-(i + 1)]])  # Append from the longest array
            if i < len(second):
                played_order.append(self.TAROT_ASCII[second[-(i + 1)]])  # Append from the other array

        # Reverse the order to match the correct sequence
        played_order.reverse()
        print(played_order)

    def games_get( self, aFormat ):
        arr = [];
        s = "";
        for k,v in self.GAMES_AVAILABLE.items():
            if aFormat == "string":
                s +="{} - {}\n".format(k,v["player1"]["name"]);
            else:
                arr.append( [ k , v["player1"]["name"] ] );
        if aFormat == "string":
            return s;
        return arr;

    def game_start(self, name ):
        gameID = self._random_string();
        hand , remainder = self._hand_and_remainder();
        self._store_new_available_game( gameID, name, hand, remainder );
        return [ gameID, hand ];

    def game_join(self, name, gameID ):
        if gameID not in self.GAMES_AVAILABLE:
            raise Exception("Invalid GameID");
        
        gameData = self.GAMES_AVAILABLE[ gameID ];
        hand = self._hand_from_remainder( gameData["remainder"] );
        self._store_open_game( gameID, name, hand ) 
        return [gameID, hand];
    
    def player_hand( self, gameID , player ):
        if gameID not in self.GAMES_OPEN:
            raise Exception("Invalid GameID");
        if ( player != self.GAMES_OPEN[ gameID ]["player1"]["name"]
            and player != self.GAMES_OPEN[ gameID ]["player2"]["name"] ):
            raise Exception("Invalid Player");
        if self.GAMES_OPEN[ gameID ][ "player1"]["name"] == player:
            return self.GAMES_OPEN[ gameID ][ "player1" ][ "hand" ];
        if self.GAMES_OPEN[ gameID ][ "player2"]["name"] == player:
            return self.GAMES_OPEN[ gameID ][ "player2" ][ "hand" ];
        return [];

    def player_turn( self, gameID ):
        if gameID not in self.GAMES_OPEN:
            raise Exception("Invalid GameID");
        return self.GAMES_OPEN[ gameID ][ "turn" ];
    
    def player_name(self, gameID, which ):
        if gameID not in self.GAMES_OPEN:
            raise Exception("Invalid GameID");
        if which == "player1" or which == "player2":
            return self.GAMES_OPEN[ gameID ][ which ][ "name" ];

    def player_name_other(self, gameID, playerName):
        if gameID not in self.GAMES_OPEN:
            raise Exception("Invalid GameID");
        if playerName == self.GAMES_OPEN[ gameID ][ "player1" ][ "name" ]:
            return self.GAMES_OPEN[ gameID ][ "player2" ][ "name" ]
        elif playerName == self.GAMES_OPEN[ gameID ][ "player2" ][ "name" ]:
            return self.GAMES_OPEN[ gameID ][ "player1" ][ "name" ]
        return None;

    def game_play( self, name, gameID, cardIndex ):
        if gameID not in self.GAMES_OPEN:
            raise Exception("Invalid GameID");
        
        gameData = self._store_get_game_data( gameID );
        
        if name != gameData["player1"]["name"] and name != gameData["player2"]["name"]:
            print( gameData );
            raise Exception("Invalid Player");
        
        player = "player1" if name == gameData["player1"]["name"] else "player2";
       
        if cardIndex == None:
            self._store_finish_game( gameID )
            return False;
 
        if cardIndex >= len( gameData[ player ][ "hand" ] ):
            print( "card: {}".format( card ) );
            print( "player: {}".format( player ) );
            print( "hand: {}".format( gameData[ player ]["hand"] ));
            raise Exception("Invalid Play");

        otherPlayer = "player2" if player == "player1" else "player1";

        card = gameData[ player ][ "hand" ][ cardIndex ];

        if len( gameData[ otherPlayer ][ "played" ] ) > 0:
            lastPlay = gameData[ otherPlayer ][ "played" ][ -1 ];

            if not self._play_validate( lastPlay , card ):
                print( "lastPlay: {}, card: {}".format( lastPlay, card ));
                raise Exception("Invalid Play");

        self._store_play_game( gameID, name, card );

        if len(gameData[otherPlayer]["played"]) == 5 and len(gameData[player]["played"]) == 5:
            self._store_finish_game( gameData )
            return False;
        
        return True;

    def game_end( self, gameID ):
        self._store_finish_game( gameID )

    def _game_evaluate( self, gameData ):
        
        player1Name = gameData["player1"]["name"];
        player2Name = gameData["player2"]["name"];
        player1Played = gameData["player1"]["played"];
        player2Played = gameData["player2"]["played"];
        
        totalPlayer1 = 0;
        totalPlayer2 = 0;
        
        for i in range(0,len(player1Played)):
            totalPlayer1 += self._cardToScore( player1Played[ i ] );
        for i in range(0,len(player2Played)):
            totalPlayer2 += self._cardToScore( player2Played[ i ] );

        if len( player1Played ) == len( player2Played ):
            if totalPlayer1 == totalPlayer2:
                return "draw";
            return player1Name if totalPlayer1 > totalPlayer2 else player2Name;
        return player1Name if len( player1Played ) > len( player2Played ) else player2Name;

    def game_evaluate( self, gameID ):
        gameData = self._store_get_finished_game_data( gameID );
        return self._game_evaluate( gameData );
    
    ###############################################

    def _cardToScore( self , card ):
        if card < self.CARD_FOOL:
            return ( card % self.CARD_SUIT_SIZE ) + 1; # 01-14
        else:
            return ( card - self.CARD_FOOL ) + self.CARD_SUIT_SIZE; # 15-37

    def _hand_from_remainder(self, remainder):
        hand = []
        while len(hand) < self.HAND_SIZE:
            i = random.randint(0, len(remainder) - 1)
            _c = remainder[i]
            if _c not in hand:
                hand.append(_c)
        return hand

    def _hand_and_remainder(self ):
        arr = [[], []]
        j = 0
        while len(arr[0]) < self.HAND_SIZE:
            i = random.randint(0, len(self.CARDS) - 1)
            _c = self.CARDS[i]
            if _c not in arr[0] and _c not in arr[1] and len(arr[j]) < self.HAND_SIZE:
                arr[j].append(_c)
            j += 1
            if j >= 2:
                j = 0
        # Fill up remainder
        for _c in self.CARDS:
            if _c not in arr[0]:
                arr[1].append(_c)
        return arr


    TAROT_ASCII = [
        # Clubs
        "[ ♣A  ]", #0
        "[ ♣2  ]",
        "[ ♣3  ]",
        "[ ♣4  ]",
        "[ ♣5  ]",
        "[ ♣6  ]",
        "[ ♣7  ]",
        "[ ♣8  ]",
        "[ ♣9  ]",
        "[ ♣10 ]",
        "[ ♣P  ]",
        "[ ♣J  ]",
        "[ ♣Q  ]",
        "[ ♣K  ]",
        # Diamonds
        "[ ♦A  ]", #14
        "[ ♦2  ]",
        "[ ♦3  ]",
        "[ ♦4  ]",
        "[ ♦5  ]",
        "[ ♦6  ]",
        "[ ♦7  ]",
        "[ ♦8  ]",
        "[ ♦9  ]",
        "[ ♦10 ]",
        "[ ♦P  ]",
        "[ ♦J  ]",
        "[ ♦Q  ]",
        "[ ♦K  ]",
        # Hearts
        "[ ♥A  ]", #26
        "[ ♥2  ]",
        "[ ♥3  ]",
        "[ ♥4  ]",
        "[ ♥5  ]",
        "[ ♥6  ]",
        "[ ♥7  ]",
        "[ ♥8  ]",
        "[ ♥9  ]",
        "[ ♥10 ]",
        "[ ♥P  ]",
        "[ ♥J  ]",
        "[ ♥Q  ]",
        "[ ♥K  ]",
        # Spades
        "[ ♠A  ]", #42
        "[ ♠2  ]",
        "[ ♠3  ]",
        "[ ♠4  ]",
        "[ ♠5  ]",
        "[ ♠6  ]",
        "[ ♠7  ]",
        "[ ♠8  ]",
        "[ ♠9  ]",
        "[ ♠10 ]",
        "[ ♠P  ]",
        "[ ♠J  ]",
        "[ ♠Q  ]",
        "[ ♠K  ]",
        # Trumps (Roman Numerals I to XXI)
        "[Fool ]", #56
        "[I    ]",
        "[II   ]",
        "[III  ]",
        "[IV   ]",
        "[V    ]",
        "[VI   ]",
        "[VII  ]",
        "[VIII ]",
        "[IX   ]",
        "[X    ]",
        "[XI   ]",
        "[XII  ]",
        "[XIII ]",
        "[XIV  ]",
        "[XV   ]",
        "[XVI  ]",
        "[XVII ]",
        "[XVIII]",
        "[XIX  ]",
        "[XX   ]",
        "[XXI  ]" #78 -1
    ]

    TAROT_NAMES = [
        "Ace of Clubs", "Two of Clubs", "Three of Clubs", "Four of Clubs", "Five of Clubs", 
        "Six of Clubs", "Seven of Clubs", "Eight of Clubs", "Nine of Clubs", "Ten of Clubs", 
        "Page of Clubs", "Knight of Clubs", "Queen of Clubs", "King of Clubs",
        
        "Ace of Diamonds", "Two of Diamonds", "Three of Diamonds", "Four of Diamonds", "Five of Diamonds", 
        "Six of Diamonds", "Seven of Diamonds", "Eight of Diamonds", "Nine of Diamonds", "Ten of Diamonds", 
        "Page of Diamonds", "Knight of Diamonds", "Queen of Diamonds", "King of Diamonds", 
        
        "Ace of Hearts", "Two of Hearts", "Three of Hearts", "Four of Hearts", "Five of Hearts", 
        "Six of Hearts", "Seven of Hearts", "Eight of Hearts", "Nine of Hearts", "Ten of Hearts", 
        "Page of Hearts", "Knight of Hearts", "Queen of Hearts", "King of Hearts",
        
        "Ace of Spades", "Two of Spades", "Three of Spades", "Four of Spades", "Five of Spades", 
        "Six of Spades", "Seven of Spades", "Eight of Spades", "Nine of Spades", "Ten of Spades", 
        "Page of Spades", "Knight of Spades", "Queen of Spades", "King of Spades",
        
        "The Fool", "The Magician", "The High Priestess", "The Empress", "The Emperor", 
        "The Hierophant", "The Lovers", "The Chariot", "Strength", "The Hermit", 
        "Wheel of Fortune", "Justice", "The Hanged Man", "Death", "Temperance", 
        "The Devil", "The Tower", "The Star", "The Moon", "The Sun", 
        "Judgment", "The World"
    ]

    TAROT_MEANINGS = [
        "A new opportunity for growth or action; inspiration and creative potential.",
        "Partnership and cooperation, balancing different ideas or actions.",
        "Collaboration and teamwork; early success and expansion of efforts.",
        "Stability and security; a solid foundation after work or effort.",
        "Struggle and competition; challenges and conflict.",
        "Victory and achievement; recognition for hard work.",
        "Challenge and defense; persistence in the face of opposition.",
        "Effort and progress; continued work leading to success.",
        "Resilience and endurance; nearing completion or the final push.",
        "Completion of a cycle; fulfillment, but also burden or responsibility.",
        "A messenger of creativity and exploration; youthful energy and new beginnings.",
        "Action and pursuit of adventure; a bold and enthusiastic character.",
        "Nurturing creativity and growth; a strong, independent, and passionate woman.",
        "Leadership and authority in creative endeavors; mastering practical and ambitious goals.",
        
        "A new beginning in material wealth, opportunities, or investments.",
        "Balance and harmony in finances; juggling multiple priorities.",
        "Creativity in work; using talent to achieve success and recognition.",
        "Stability in material wealth; security and holding onto resources.",
        "Financial loss or hardship; a warning against wasteful spending or poor decisions.",
        "Generosity and balance in giving and receiving; mutual support.",
        "Assessment of resources; evaluating investments or past efforts.",
        "Hard work, diligence, and mastery in your craft or trade.",
        "Fulfillment of material goals; enjoying the rewards of hard work.",
        "Legacy, wealth, and family; a long-term financial or material goal reached.",
        "News regarding material matters, such as career, finance, or study; curiosity about tangible assets.",
        "Practicality and hard work; someone focused on achieving material goals.",
        "A nurturing and resourceful woman; someone who values comfort, luxury, and stability.",
        "Mastery of wealth and resources; a successful, authoritative figure in financial matters.",
        
        "Emotional renewal or new beginnings in love or relationships.",
        "Harmony and union; a partnership or romantic connection.",
        "Emotional fulfillment or celebration; joy shared with others.",
        "Emotional discontent or boredom; need for introspection or reevaluation.",
        "Emotional loss or regret; healing from disappointment.",
        "Nostalgia or reconciliation; revisiting past emotional experiences.",
        "Illusion or confusion; emotional choices or distractions.",
        "Moving on from emotional situations; emotional withdrawal or moving forward.",
        "Emotional satisfaction and contentment; the wish card—your desires fulfilled.",
        "Emotional fulfillment and happiness; a happy family or loving community.",
        "A messenger of love and emotions; youthful energy or new beginnings in relationships.",
        "Romantic, idealistic, and passionate; pursuing love or creative ideals.",
        "Compassion, intuition, and emotional nurturing; a caring, empathetic woman.",
        "Emotional balance and maturity; a wise, loving, and emotionally stable man.",
        
        "A new beginning in intellect or challenges; breakthroughs or sudden clarity.",
        "Conflict or division; a decision that may lead to separation or imbalance.",
        "Heartbreak or emotional pain; a difficult situation or betrayal.",
        "Rest or recovery after stress; contemplation or retreat for healing.",
        "Loss or struggle; a difficult situation requiring resilience.",
        "Moving forward from difficult times; transition or change toward a better situation.",
        "Deception or dishonesty; a warning to be cautious and aware of hidden motives.",
        "Restriction or limitation; feeling trapped or stuck in a situation.",
        "Anxiety or worry; mental stress or overwhelming thoughts.",
        "Completion of a painful cycle; hitting rock bottom but with hope for a new beginning.",
        "A messenger of information or challenges; new ideas and mental pursuits.",
        "Bold action and swift decision-making; someone who pursues intellectual or competitive goals.",
        "Independent, insightful, and perceptive; a woman who is clear-headed and strong-willed.",
        "Intellectual mastery, authority, and leadership; a wise, logical, and fair leader.",
        
        "New beginnings, spontaneity, and taking a leap of faith; trusting the journey ahead.",
        "Manifestation and personal power; using skills and resources to create reality.",
        "Intuition, wisdom, and inner knowing; trusting your instincts.",
        "Nurturing, creativity, and fertility; abundance and growth.",
        "Authority, structure, and leadership; establishing order and control.",
        "Tradition, wisdom, and spiritual guidance; connection to higher knowledge or institutions.",
        "Love, union, and choice; a relationship or decision that aligns with your values.",
        "Determination, willpower, and victory over obstacles; control and direction.",
        "Courage, inner strength, and compassion; overcoming challenges with patience.",
        "Introspection, solitude, and inner guidance; seeking wisdom within.",
        "Fate, cycles, and destiny; things are shifting, and a change is imminent.",
        "Fairness, balance, and truth; the consequences of actions are revealed.",
        "Surrender, letting go, and seeing things from a new perspective; patience.",
        "Transformation, endings, and new beginnings; clearing the old to make way for the new.",
        "Balance, harmony, and patience; blending opposites for a greater whole.",
        "Temptation, addiction, and bondage; being trapped by material or unhealthy attachments.",
        "Sudden upheaval, chaos, and revelation; a dramatic change that clears away the old.",
        "Hope, inspiration, and spiritual guidance; a sense of peace after turmoil.",
        "Illusion, intuition, and the subconscious; things are unclear or deceptive.",
        "Joy, success, and vitality; clarity and enlightenment after darkness.",
        "Awakening, renewal, and redemption; a call to evaluate your life or actions.",
        "Completion, wholeness, and achievement; the fulfillment of a cycle."
    ]


def parse_input(input_str):
    valid_commands = {"/start", "/join", "/play", "/fold", "/hand", "/state", "/winner", "/list", "/help"}
    valid_cards = {"a", "b", "c", "d", "e", "f", "g", "h", "i", "j"}
    # Initialize output
    command = None
    card = None
    game_id = None
    tokens = input_str.split()
    for token in tokens:
        if token in valid_commands:
            command = token
            break
    for token in tokens:
        if token.lower() in valid_cards:
            card = token
            break
    for token in tokens:
        if re.fullmatch(r"[A-Za-z0-9]{6}", token):
            game_id = token
            break
    return {"command": command, "card": card, "gameID": game_id}

# returns [ TEXT , playerName ] 
def playParseText( text , playerName ):
    parsed = parse_input( text );
   
    if parsed["command"] == None:
        return [ HELP_STR , playerName , None ];
    cmd = parsed["command"];

    def pickCardString( asciiCards, cards ):
        opt = ["(A)","(B)","(C)","(D)","(E)","(F)","(G)","(H)","(I)"]
        s = "";
        try:
            for i,v in enumerate(cards):
                s += "{}{} ".format( opt[i] , asciiCards[v] );
            s += "\nSelect a card:\n";
            return s;
        except:
            traceback.print_exc();

    def cardsPlayedString( g, gameID ):
        rsp = g.game_played_cards( gameID );
        s = [ g.TAROT_ASCII[i] for i in rsp ];
        #s.reverse();
        return "".join(s);

    if cmd.startswith("/start"):
        if None == playerName:
            raise Exception("Invalid Player");
        g = Game();
        
        endedGameID , endedGame = g._store_house_keeping()
        endedGameMsg = None;
        if None != endedGameID:
            endedPlayerName = g._game_evaluate( endedGame );
            endedGameMsg = [ "{} - {}".format( endedGameID, MSG_WON ) , endedPlayerName ];
        
        rlt = g.get_game_ids_by_player( playerName )
        if len(rlt) > 0:
            return [ ERROR_FINISH_OTHER_GAME, playerName, None ];
        
        if len( g.GAMES_AVAILABLE ) > MAX_GAMES:
            return [ ERROR_JOIN_A_GAME, playerName, None ];

        rsp = g.game_start( playerName );
        h = [ g.TAROT_ASCII[ i ] for i in rsp[1] ];
        return [ rsp[0]+" - "+"".join( h ) , playerName , endedGameMsg ];

    elif cmd.startswith("/join"):
        if None == playerName:
            raise Exception("Invalid Player");
        g = Game();
        if None == parsed["gameID"]:
            print("gameID is none");
            return [ ERROR_GAME_ID_NONE, playerName, None ];
        if not ( parsed["gameID"] in g.GAMES_AVAILABLE.keys() ):
            return [ ERROR_GAME_ID_INVALID, playerName, None ];
        rsp = g.game_join( playerName , parsed["gameID"] );
        
        playerTurn = g.player_turn( parsed["gameID"] )
        playerTurnName = g.player_name( parsed["gameID"], playerTurn )

        additionalMsg = None;
        rspMsg = None;
        if playerTurnName == playerName:
            rspMsg = "gameID : {}\n".format( rsp[0] );
            selectStr = pickCardString( g.TAROT_ASCII, rsp[1] ); #h );
            rspMsg += selectStr;
        else:
            rspMsg = "gameID : {}\n".format( rsp[0] );
            h = [ g.TAROT_ASCII[ i ] for i in rsp[1] ];
            rspMsg += "{}\n".format( h );
            rspMsg += ERROR_PLAYER_NOT_TURN;
            otherPlayerSelectStr = pickCardString( g.TAROT_ASCII , g.player_hand( parsed["gameID"] , playerTurnName ) )
            additionalMsg = [ otherPlayerSelectStr , playerTurnName ];
        return [ rspMsg , playerName, additionalMsg ];

    elif cmd.startswith("/state"):

        gameID = parsed["gameID"]
        g = Game();
        if None == gameID and None != playerName:
            rlt = g.get_game_ids_by_player( playerName )
            if len(rlt) > 1:
                return [ ERROR_GAME_ID_NONE, playerName, None ];
            if len(rlt) == 0:
                return [ ERROR_GAME_ID_INVALID, playerName, None ];
            gameID = rlt[0];
        
        if None == gameID:
            return [ ERROR_GAME_ID_NONE, playerName, None ];
        
        playedCards = cardsPlayedString( g, gameID );
        msg = MSG_CARDS_PLAYED + ": "+ ( playedCards if playedCards != "" else "None") +"\n";
        if None != playerName:
            playerTurn = g.player_turn( gameID )
            playerTurnName = g.player_name( gameID, playerTurn )
            if playerName == playerTurnName:
                msg += pickCardString( g.TAROT_ASCII , g.player_hand( gameID , playerName ) )
            else:
                msg += ERROR_PLAYER_NOT_TURN;
                msg += " - ";
                msg += playerTurnName;
        return [ msg , playerName, None ];
    elif cmd.startswith("/winner"):
        if None == parsed["gameID"]:
            return [ ERROR_GAME_ID_INVALID, playerName, None ];
        g = Game();
        rsp = g.game_evaluate( gameID )
        return [ rsp, playerName ];
    elif cmd.startswith("/play"):
        if None == playerName:
            raise Exception("Invalid Player");
        gameID = parsed["gameID"]
        g = Game();
        if None == gameID:
            rlt = g.get_game_ids_by_player( playerName )
            if len(rlt) > 1:
                return [ ERROR_GAME_ID_NONE, playerName, None ];
            if len(rlt) == 0:
                return [ ERROR_GAME_ID_INVALID, playerName, None ];
            gameID = rlt[0];
        if None == parsed["card"]:
            return [ ERROR_CARD_NONE, playerName, None ];
        if g.game_is_open( gameID ):
            playerTurn = g.player_turn( gameID )
            playerTurnName = g.player_name( gameID, playerTurn )
            playerOtherName = g.player_name( gameID, "player1" if playerTurn == "player2" else "player2" );
            if playerTurnName == playerName:
                cardIndex = ["a","b","c","d","e","f","g","h","i","j","k"].index( parsed["card"].lower() );
                gameIsInPlay = g.game_play( playerName , gameID , cardIndex  );
                if not gameIsInPlay:
                    winnerName = g.game_evaluate( gameID )
                    otherMsg = None;
                    playerStr = None;
                    if winnerName == playerName:
                        playerStr = MSG_WON;
                        otherMsg = [ MSG_LOST , playerOtherName  ];
                    else:
                        playerStr = MSG_LOST;
                        otherMsg = [ MSG_WON , playerOtherName ];
                    return [ playerStr, playerName, otherMsg ];
                otherPlayerSelectStr = pickCardString( g.TAROT_ASCII , g.player_hand( gameID , playerOtherName ) )
                
                playedCards = cardsPlayedString( g, gameID );
                otherPlayerMsg = MSG_CARDS_PLAYED + ": "+ ( playedCards if playedCards != "" else "None") +"\n";
                otherPlayerMsg += otherPlayerSelectStr;

                otherMsg = [ otherPlayerMsg , playerOtherName ];
                return [ "OK", playerName, otherMsg ];
            else: 
                return [ ERROR_PLAYER_NOT_TURN, playerName, None ];
        return [ ERROR_GAME_FINISHED, playerName, None ];
    elif cmd.startswith("/hand"):
        if None == playerName:
            raise Exception("Invalid Player");
        if None == parsed["gameID"]:
            raise Exception("Invalid GameID");
        g = Game();
        return [ pickCardString( g.TAROT_ASCII , g.player_hand( gameID , playerName ) ) , playerName , None ];
    elif cmd.startswith("/fold"):
        print("/fold");
        gameID = parsed["gameID"]
        g = Game(); 
        if None == gameID:
            rlt = g.get_game_ids_by_player( playerName )
            if len(rlt) > 1:
                return [ ERROR_GAME_ID_NONE, playerName, None ];
            if len(rlt) == 0:
                return [ ERROR_GAME_ID_INVALID, playerName, None ];
            gameID = rlt[0];
        if None == gameID:
            return [ ERROR_GAME_ID_NONE, playerName, None ];
        otherPlayerName = g.player_name_other(gameID,playerName);
        g.game_end( gameID );
        otherPayload = [ ERROR_PLAYER_FOLDED , otherPlayerName ];
        return [ "OK", playerName , otherPayload ];
    elif cmd.startswith("/help"):
        return [ HELP_STR , playerName, None ];
    elif cmd.startswith("/list"):
        g = Game();
        arrStr = g.games_get( "string" )
        if arrStr == "":
            return [ "No Games:(", playerName, None ];
        return [ arrStr, playerName, None ];
    return [ None, None, None ];

if __name__ == '__main__':
       
    if len(sys.argv) > 1:
        parser = argparse.ArgumentParser(description="Play the game Tarok.")
        parser.add_argument('cmd', type=str, help="Game command.")
        #parser.add_argument('--card', type=str, choices=["a","b","c","d","e","f","g","h","i"],help="Card choice.")
        #parser.add_argument('--gameID', type=str, help="Id of the game.")
        parser.add_argument('--player', type=str, help="Name of the player.")
        args = parser.parse_args()
        
        rsp = playParseText( args.cmd,args.player );
        print( rsp );
        sys.exit();

    g = Game();
    def pickCard( asciiCards, cards ):
        opt = ["(A)","(B)","(C)","(D)","(E)","(F)","(G)","(H)","(I)"]
        try:
            for i,v in enumerate(cards):
                print( opt[i] + asciiCards[v] + " ",end="");
            print(" ");
            p = "("+input("Please select a card: ").upper()+")";
            if p in opt:
                index = opt.index( p );
                if index < len(cards):
                    return index;
        except:
            return None;
            #traceback.print_exc();
        return None;

    # G.TAROT_ASCII[ ];
    rsp = g.game_start( "playerA" );
    gameID = rsp[0];
    playerAHand = rsp[1];
    print("gameID : {}".format( gameID ) );
    
    rsp = g.game_join( "playerB", gameID );
    playerBHand = rsp[1];
    
    gameIsInPlay = True;
    while gameIsInPlay:
        player = g.player_name( gameID, g.player_turn( gameID ) )
        rsp = g.game_played_cards(gameID);
        played = [ g.TAROT_ASCII[i] for i in rsp ];
        print( played );
        cardIndex = pickCard( g.TAROT_ASCII , g.player_hand( gameID , player ) )
        gameIsInPlay = g.game_play( player , gameID , cardIndex  );
        print("-------------------");
    
    rsp = g.game_evaluate( gameID )
    print("Winner is: ", rsp );

