import random;

_URL_PREFIX = "https://raw.githubusercontent.com/lacdael/scripts/refs/heads/main/social/nostr/runecast/img/"
_SUFFIX = ".svg";

_RUNES = [ "f","f-rev","u","u-rev","th","th-rev","o","o-rev",
 "r","r-rev","c","c-rev","g","w","w-rev","h","h-rev",
 "n","n-rev","i","j","iw","p","p-rev","x","x-rev","s",
 "t","t-rev","b","b-rev","e","e-rev","m","m-rev","l",
 "l-rev","ng","oe","oe-rev","d"
]

_STRINGS = {
	"f-NAME":{"en": "Feoh"},
	"f":{"en": "Money, wealth, luck, abundance."},
	"f-rev":{"en":"Travel, relocation, dance of life."},
    "f-rev-NAME":{"en": "Feoh - reversed"},
	"u-NAME" : {"en":"Ur"},
	"u" : {"en":"Ox, strength, power, courage."},
	"u-rev-NAME" : {"en":"Ur - reversed"},
	"u-rev" : {"en":"Frailty, rashness, violence, lust."},
	"th-NAME" :{"en": "Thorn"},
	"th" : {"en":"Thorn, change, catharsis."},
	"th-rev-NAME" :{"en": "Thorn - reversed"},
	"th-rev" :{"en": "Compulsion, evil, violence, lust."},
	"o-NAME" : {"en":"Os"},
	"o" :{"en": "Mouth, creativity, "},
	"o-rev-NAME" : {"en":"Os - reversed"},
	"o-rev":{"en": "At a standstill, lack of direction"},
	"r-NAME" :{"en": "Rad"},
	"r" :{"en": "Wagaon, travel, journey, destiny."},
	"r-rev-NAME" :{"en": "Rad - reversed"},
	"r-rev" :{"en": "Crisis, rigidity, injustice, death."},
	"c-NAME" : {"en":"Cen"},
	"c" : {"en":"Torch, revelation, knowledge, creativity, inspiration."},
	"c-rev-NAME" : {"en":"Cen - reversed"},
	"c-rev" :{"en": "False hope, no creativity."},
	"g-NAME" : {"en":"Gyfu"},
	"g" : {"en":"Gift, love, generosity, marriage, partnership."},
	"w-NAME" : {"en":"Wynn"},
	"w" :{"en": "Joy, sucess, peace, pleasure, self defence."},
	"w-rev-NAME" : {"en":"Wynn - reversed"},
	"w-rev" :{"en": "Sorrow, strife, intoxication, frenzy."},
	"h-NAME" :{"en": "Haegl"},
	"h" :{"en": "Hailstrom, loss, destruction, change."},
	"h-rev-NAME" :{"en": "Haegl - reversed"},
	"h-rev" :{"en": "Catastrophe, loss, sickness, hardship, pain."},
	"n-NAME" : {"en":"Nyd"},
	"n" : {"en":"Need, necessity, hardship, delays."},
	"n-rev-NAME" : {"en":"Nyd - reversed"},
	"n-rev" :{"en":"Drudgery, laxity, restlessness."},
	"i-NAME" : {"en":"Is"},
	"i" : {"en":"Ice, standstill, block, challenge."},
	"j-NAME" :{"en": "Jer"},
	"j" : {"en":"Year, harvest, peace, rewards."},
	"iw-NAME" : {"en":"Eeoh"},
	"iw" :{"en": "Yew tree, stability, strength, reliability, enlightenment."},
	"p-NAME" : {"en":"Peorth"},
	"p" : {"en":"Luck, magic, mystery, feminine."},
	"p-rev-NAME" : {"en":"Peorth - reversed"},
	"p-rev" : {"en":"Addiction, loneliness, malaise."},
	"x-NAME" : {"en":"Eolh"},
	"x" : {"en":"Elk, protection, shield, self defence."},
	"x-rev-NAME" : {"en":"Eolh - reversed"},
	"x-rev" :{"en": "Hidden danger, taboo, warning."},
	"s-NAME" : {"en":"Sigel"},
	"s" : {"en":"Sun, strength, energy, health, success."},
	"t-NAME" : {"en":"Tyr"},
	"t" : {"en":"Tyr, honor, justice, leadership, authority."},
	"t-rev-NAME" : {"en":"Tyr - reversed"},
	"t-rev" : {"en":"Strife, war, stupidity, dullness."},
	"b-NAME" : {"en":"Beorc"},
	"b" : {"en":"Birch, birth, beginnings, personal growth, liberation."},
	"b-rev-NAME" : {"en":"Beorc - reversed"},
	"b-rev" : {"en":"Anxiety, deceit, abandon, loss of control."},
	"e-NAME" : {"en":"Eoh"},
	"e" : {"en":"Horse, transportation, partnership."},
	"e-rev-NAME" : {"en":"Eoh - reversed"},
	"e-rev" : {"en":"Reckless, haste, disharmony, mistrust, betrayal."},
	"m-NAME" : {"en":"Mann"},
	"m" : {"en":"Man, self, mankind, culture, friends."},
	"m-rev-NAME" : {"en":"Mann - reversed"},
	"m-rev" : {"en":"Depression, slyness, mortality, manipulation."},
	"l-NAME" : {"en":"Lagu"},
	"l" : {"en":"Lake, water, sea, flow, renewal"},
	"l-rev-NAME" : {"en":"Lagu - reversed"},
	"l-rev" : {"en":"Confusion, dispair, perversity, madness."},
	"ng-NAME" : {"en":"Ing"},
    "ng" : {"en":"Fertility, growth, harmony."},
	"oe-NAME" : {"en":"Oedel"},
	"oe" : {"en":"Estate, property, plenty."},
	"oe-rev-NAME" : {"en":"Oedel - reversed"},
	"oe-rev" : {"en":"Slavery, bad karma, homelessness."},
	"d-NAME" : {"en":"Daeg"},
	"d" : {"en":"Day, dawn, break-through, awareness."}
}

def getRune():
    k = random.choice( _RUNES );
    return "{}\n{}\n{}\n".format(
            _STRINGS[ k+"-NAME"]["en"],
            _URL_PREFIX+k+_SUFFIX,
            _STRINGS[ k ]["en"]);
