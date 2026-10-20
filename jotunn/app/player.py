import base64
from collections import Counter
import datetime
import dayplot as dp
from dotenv import load_dotenv
from io import BytesIO
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.figure import Figure
from operator import itemgetter
import orjson
import os
import requests
from requests.adapters import HTTPAdapter
import re
from time import sleep
from urllib3.util import Retry

load_dotenv()
api_key_header = {"X-API-Key": f"{os.getenv("API_KEY")}"}


class Player:
    metrics_defs = {
        "subclassDefeats": {
            "Berserker": 3133144330,
            "Behemoth": 626613399,
            "Sentinel": 1045301756,
            "Sunbreaker": 1337769169,
            "Striker": 2839721658,
            "Threadrunner": 115661044,
            "Revenant": 673324377,
            "Nightstalker": 451582922,
            "Gunslinger": 502216639,
            "Arcstrider": 2387491484,
            "Broodweaver": 2445590309,
            "Shadebinder": 813571064,
            "Voidwalker": 4114590251,
            "Dawnblade": 30426544,
            "Stormcaller": 2094083755,
        },
        "weapons": {
            "Auto Rifle": 2094013181,
            "Pulse Rifle": 982406257,
            "Scout Rifle": 2599646044,
            "Hand Cannon": 2117204340,
            "Sidearm": 2012993124,
            "Submachine Gun": 1165153680,
            "Bow": 3522276357,
            "Trace Rifle": 3124958797,
            "Fusion Rifle": 105734892,
            "Shotgun": 139320435,
            "Sniper Rifle": 633604541,
            "Grenade Launcher": 1681554390,
            "Rocket Launcher": 1200426430,
            "Sword": 1619269474,
            "Linear Fusion Rifle": 2707112071,
            "Machine Gun": 401742412,
        },
        "finalBlows": {
            "total": 2537844000,
            "solar": 2187143539,
            "arc": 1513312460,
            "void": 2327589890,
            "stasis": 2464463405,
            "strand": 2889561660,
        },
        "extra": {
            "totalFish": 24768693,
            "heaviestFish": 2691615711,
            "goodBoy": 3131994725,
            "snowballDefeats": 857713621,
            "cookiesBaked": 3597861791,
        },
    }

    exotic_defs = {
        1345867570: "Sweet Business",
        2907129556: "Sturm",
        3628991659: "Vigilance Wing",
        2362471601: "Rat King",
        1331482397: "MIDA Multi-Tool",
        3437746471: "Crimson",
        3844694310: "The Jade Rabbit",
        2286143274: "Huckleberry",
        2856683562: "SUROS Regime",
        1541131350: "Cerberus+1",
        814876684: "Wish Ender",
        204878059: "Malfeasance",
        347366834: "Ace of Spades",
        3413860062: "The Chaperone",
        3211806999: "Izanagi's Burden",
        1364093401: "The Last Word",
        2130065553: "Arbalest",
        3973202132: "Thorn",
        400096939: "Outbreak Perfected",
        3824673936: "Outbreak Perfected",
        3512014804: "Lumina",
        2816212794: "Bad Juju",
        4068264807: "Monte Carlo",
        2415517654: "Bastion",
        2357297366: "Witherhoard",
        1853180924: "Traveler's Chosen",
        1594120904: "No Time to Explain",
        3654674561: "Dead Man's Tale",
        603721696: "Cryosthethesia 77K",
        1833195496: "Ager's Scepter",
        2179048386: "Forerunner",
        46524085: "Osteo Striga",
        1802135586: "Touch of Malice",
        4293613902: "Quicksilver Storm",
        1473821207: "Revision Zero",
        3121540812: "Final Warning",
        3371017761: "Conditional Finality",
        3659414143: "Verglas Curve",
        940371471: "Wicked Implement",
        1441805468: "The Navigator",
        1345867571: "Coldheart",
        4190156464: "Merciless",
        3549153978: "Fighting Lion",
        2907129557: "Sunshot",
        3628991658: "Graviton Lance",
        4255268456: "Skyburner's Oath",
        3141979347: "Borealis",
        3089417789: "Riskrunner",
        4124984448: "Hard Light",
        19024058: "Prometheus Lens",
        2208405142: "Telesto",
        3413074534: "Polaris Lance",
        814876685: "Trinity Ghoul",
        1852863732: "Wavesplitter",
        3413860063: "Lord of Wolves",
        3588934839: "Le Monarque",
        417164956: "Jötunn",
        3110698812: "Tarrabah",
        3524313097: "Eriana's Vow",
        4103414242: "Divinity",
        4017959782: "Symmetry",
        3824106094: "Devil's Ruin",
        776191470: "Tommy's Matchbook",
        1665952087: "The Fourth Horseman",
        1363238943: "Ruinous Effigy",
        3460576091: "Duality",
        2603483885: "Cloudstrike",
        3260753130: "Ticuu's Divination",
        4289226715: "Vex Mythoclast",
        3761898871: "Lorentz Driver",
        14194600: "Edge of Intent",
        542203595: "Edge of Concurrence",
        2535142413: "Edge of Action",
        2812324401: "Dead Messenger",
        46125926: "Dead Messenger",
        3505113722: "Collective Obligation",
        374573733: "Delicate Tomb",
        1234150730: "Trespasser",
        219145368: "The Manticore",
        4174431791: "Hierarchy of Needs",
        3118061005: "Vexcalibur",
        1912669214: "Centrifuse",
        1508896098: "Wardcliff Coil",
        3580904581: "Tractor Cannon",
        3580904580: "Legend of Acrius",
        1744115122: "Legend of Acrius",
        3141979346: "D.A.R.C.I",
        3899270607: "The Colony",
        1864563948: "Worldline Zero",
        4036115577: "Sleeper Simulant",
        2069224589: "One Thousand Voices",
        2694576561: "Two-Tailed Fox",
        3766045777: "Black Talon",
        2044500762: "The Queenbreaker",
        3325463374: "Thunderlord",
        2376481550: "Anarchy",
        2591746970: "Leviathan's Breath",
        1395261499: "Xenophage",
        2232171099: "Deathbringer",
        2084878005: "Heir Apparent",
        370712896: "Salvation's Grip",
        2399110176: "Eyes of Tomorrow",
        3487253372: "The Lament",
        1363886209: "Gjallarhorn",
        2812324400: "Parasite",
        1763584999: "Grand Overture",
        3664831848: "Heartshadow",
        449318888: "Deterministic Chaos",
        3118061004: "Winterbite",
        1201830623: "Truth",
        1891561814: "Whisper of the Worm",
        1983149589: "Whisper of the Worm",
        17096506: "Dragon's Breath",
        3561203890: "Tessellation",
        3886719505: "Buried Bloodline",
        1034055198: "Necrochasm",
        3821409356: "Ex Diris",
        3856705927: "Hawkmoon",
        3549153979: "The Prospector",
        2188764214: "Dead Man's Tale",
        2910326942: "Wish-Keeper",
        2200470033: "Cull's Shadow",
        2197778303: "Fafnir",
        253843484: "Turncoat",
        1685137410: "Heirloom",
        3049715579: "Praxic Blade",
        4284533075: "Service of Luzaku",
        1753923263: "Wolfsbane",
        1202007252: "Whirling Ovation",
        648595258: "Graviton Spike",
        1736135946: "New Malpais",
        2973900274: "Third Iteration",
        2581676735: "New Land Beyond",
        331231237: "Finality's Auger",
        1481594633: "Barrow-Dyad",
        3725585710: "Lodestar",
        1111334348: "Ice Breaker",
        1047932517: "Slayer's Fang",
        2350354266: "Alethonym",
        3698448090: "Choir of One",
        2905188646: "Still Hunt",
        1681583613: "Ergo Sum",
        4129629253: "Khvostov 7G-0X",
        4207066264: "Microcosm",
        3284383335: "Euphony",
        427899681: "Red Death Reformed",
    }
    raid_hashes = {
        156253568: "Crota's End",
        1507509200: "Crota's End",
        4179289725: "Crota's End",
        107319834: "Crota's End",
        1566480315: "Crota's End",
        3333172150: "Crown of Sorrow",
        960175301: "Crown of Sorrow",
        3976949817: "Deep Stone Crypt",
        910380154: "Deep Stone Crypt",
        1042180643: "Garden of Salvation",
        2497200493: "Garden of Salvation",
        2659723068: "Garden of Salvation",
        3458480158: "Garden of Salvation",
        3845997235: "Garden of Salvation",
        1063970578: "King's Fall",
        2964135793: "King's Fall",
        3257594522: "King's Fall",
        2897223272: "King's Fall",
        1374392663: "King's Fall",
        2214608157: "Last Wish",
        2214608156: "Last Wish",
        1661734046: "Last Wish",
        2122313384: "Last Wish",
        1699948563: "Leviathan",
        1875726950: "Leviathan",
        287649202: "Leviathan",
        3916343513: "Leviathan",
        4039317196: "Leviathan",
        89727599: "Leviathan",
        2164432138: "Eater of Worlds",
        3089205900: "Eater of Worlds",
        809170886: "Eater of Worlds",
        3004605630: "Spire of Stars",
        119944200: "Spire of Stars",
        3213556450: "Spire of Stars",
        2693136600: "Leviathan",
        2693136601: "Leviathan",
        2693136602: "Leviathan",
        2693136603: "Leviathan",
        2693136604: "Leviathan",
        2693136605: "Leviathan",
        1685065161: "Leviathan",
        1800508819: "Leviathan",
        2449714930: "Leviathan",
        3446541099: "Leviathan",
        3857338478: "Leviathan",
        3879860661: "Leviathan",
        3912437239: "Leviathan",
        417231112: "Leviathan",
        4206123728: "Leviathan",
        508802457: "Leviathan",
        757116822: "Leviathan",
        771164842: "Leviathan",
        1516551982: "Calus Resplendent",
        747671496: "Insurrection Prime Revolutionary",
        2530656885: "Morgeth Surpassing",
        2918919505: "Root of Nightmares",
        2381413764: "Root of Nightmares",
        2192826039: "Salvation's Edge",
        4129614942: "Salvation's Edge",
        1541433876: "Salvation's Edge",
        940375169: "Salvation's Edge",
        2812525063: "Scourge of the Past",
        548750096: "Scourge of the Past",
        2586252122: "The Desert Perpetual (Epic)",
        3817322389: "The Desert Perpetual (Epic)",
        3896382790: "The Desert Perpetual",
        1044919065: "The Desert Perpetual",
        4169648179: "Atraks Sovereign",
        4169648182: "Nezarec Sublime",
        4169648176: "Oryx Exalted",
        4169648177: "Rhulk Indomitable",
        3711931140: "Vault of Glass",
        1485585878: "Vault of Glass",
        1681562271: "Vault of Glass",
        3022541210: "Vault of Glass",
        3881495763: "Vault of Glass",
        2906950631: "Vow of the Disciple",
        4156879541: "Vow of the Disciple",
        3889634515: "Vow of the Disciple",
        4217492330: "Vow of the Disciple",
        1441982566: "Vow of the Disciple",
    }

    dungeon_hashes = {
        1668217731: "Duality",
        3012587626: "Duality",
        2823159265: "Duality",
        1754635208: "Equilibrium",
        2727361621: "Equilibrium",
        # 2961030534: "Ghosts of the Deep: Eternity",
        # 4190119662: "Ghosts of the Deep: Explorer (Matchmade)",
        # 1094262727: "Ghosts of the Deep: Explorer",
        2716998124: "Ghosts of the Deep",
        313828469: "Ghosts of the Deep",
        # 124340010: "Ghosts of the Deep: Ultimatum",
        1112917203: "Grasp of Avarice",
        3774021532: "Grasp of Avarice",
        4078656646: "Grasp of Avarice",
        785700678: "Pit of Heresy",
        2559374368: "Pit of Heresy",
        2559374374: "Pit of Heresy",
        2559374375: "Pit of Heresy",
        785700673: "Pit of Heresy",
        1375089621: "Pit of Heresy",
        2582501063: "Pit of Heresy",
        1077850348: "Prophecy",
        4148187374: "Prophecy",
        # 715153594: "Prophecy: Eternity",
        # 1788465402: "Prophecy: Explorer (Matchmade)",
        # 3637651331: "Prophecy: Explorer",
        # 3193125350: "Prophecy: Ultimatum",
        # 4046934917: "Spire of the Watcher: Eternity",
        # 943878085: "Spire of the Watcher: Explorer (Matchmade)",
        # 1225969316: "Spire of the Watcher: Explorer",
        1801496203: "Spire of the Watcher",
        2296818662: "Spire of the Watcher",
        1262462921: "Spire of the Watcher",
        # 3339002067: "Spire of the Watcher: Ultimatum",
        247869137: "Sundered Doctrine",
        3521648250: "Sundered Doctrine",
        3834447244: "Sundered Doctrine",
        2032534090: "The Shattered Throne",
        1915770060: "Vesper's Host",
        3492566689: "Vesper's Host",
        4293676253: "Vesper's Host",
        300092127: "Vesper's Host",
        2534833093: "Warlord's Ruin",
        2004855007: "Warlord's Ruin",
    }

    def __init__(self, query):
        self.name = query
        self.member_type = 0
        self.member_id = 0
        self.characters = dict()
        self.account = {
            "main": {
                "class": "",
                "subclass": "",
                "weaponArchetype": "",
                "emblemHash": "",
            },
            "subclassDefeats": {
                "Berserker": 0,
                "Behemoth": 0,
                "Sentinel": 0,
                "Sunbreaker": 0,
                "Striker": 0,
                "Threadrunner": 0,
                "Revenant": 0,
                "Nightstalker": 0,
                "Gunslinger": 0,
                "Arcstrider": 0,
                "Broodweaver": 0,
                "Shadebinder": 0,
                "Voidwalker": 0,
                "Dawnblade": 0,
                "Stormcaller": 0,
            },
            "aggregates": {
                "activitiesCleared": 0,
                "assists": 0,
                "kills": 0,
                "precisionKills": 0,
                "deaths": 0,
                "suicides": 0,
                "resurrectionsPerformed": 0,
                "killsDeathsRatio": 0,
                "killsDeathsAssists": 0,
                "relicKills": 0,
                "grenadeKills": 0,
                "meleeKills": 0,
                "superKills": 0,
                "longestSingleLife": "",
                "orbsDropped": 0,
                "orbsGathered": 0,
                "publicEventsCompleted": 0,
                "combatRating": 0,
                "playtime": 0,
            },
            "weapons": {
                "Auto Rifle": 0,
                "Pulse Rifle": 0,
                "Scout Rifle": 0,
                "Hand Cannon": 0,
                "Sidearm": 0,
                "Submachine Gun": 0,
                "Bow": 0,
                "Trace Rifle": 0,
                "Fusion Rifle": 0,
                "Shotgun": 0,
                "Sniper Rifle": 0,
                "Grenade Launcher": 0,
                "Rocket Launcher": 0,
                "Sword": 0,
                "Linear Fusion Rifle": 0,
                "Machine Gun": 0,
            },
            "finalBlows": {
                "total": 0,
                "solar": 0,
                "arc": 0,
                "void": 0,
                "stasis": 0,
                "strand": 0,
            },
            "finalBlowsPcts": {
                "pctStrand": 0,
                "pctStasis": 0,
                "pctVoid": 0,
                "pctArc": 0,
                "pctSolar": 0,
            },
            "extra": {
                "totalFish": 0,
                "heaviestFish": 0,
                "goodBoy": 0,
                "snowballDefeats": 0,
                "cookiesBaked": 0,
            },
        }
        self.exotics = dict()
        for weapon in self.exotic_defs.values():
            if weapon in self.exotics:
                continue
            self.exotics.update({weapon: {"kills": 0, "precision": 0}})
        self.raids = dict()
        for raid in self.raid_hashes.values():
            if raid in self.raids:
                continue
            self.raids.update(
                {
                    raid: {
                        "sortIndex": 0,
                        # "launches": 0,
                        "clears": 0,
                        "kills": 0,
                        "deaths": 0,
                        "ratio": 0.0,
                        "fastest": 0,
                        "playtime": 0,
                        # "flawless": False,
                        # "contest": False,
                    }
                }
            )

        self.dungeons = dict()
        for dungeon in self.dungeon_hashes.values():
            if dungeon in self.dungeons:
                continue
            self.dungeons.update(
                {
                    dungeon: {
                        "sortIndex": 0,
                        # "launches": 0,
                        "clears": 0,
                        "kills": 0,
                        "deaths": 0,
                        "ratio": 0.0,
                        "fastest": 0,
                        "playtime": 0,
                        # "flawless": False,
                        # "solo": False,
                        # "soloFlawless": False,
                        # "contest": False,
                    }
                }
            )

    def pull_data(self, session: requests.Session, url: str):
        try:
            response = session.get(
                url=url,
                data={},
                timeout=10,
            )
            if response:
                response.raise_for_status()
            else:
                return None
        except requests.exceptions.RequestException as e:
            print("ERROR: Could not get profile data:", e)
            return None
        if response.status_code != 200:
            print("ERROR: Status code not 200")
            return None
        return response.content

    def pull_membership_data(self):
        if not isinstance(self.name, str):
            return False
        if not re.match(r"^[A-Za-z0-9 ]+[#]\d{4}$", self.name):
            return False
        player_display_info = self.name.strip().split("#")
        player_display_info_payload = orjson.dumps(
            {
                "displayName": f"{player_display_info[0]}",
                "displayNameCode": int(player_display_info[1]),
            }
        )
        player_search_url = f"https://www.bungie.net/Platform/Destiny2/SearchDestinyPlayerByBungieName/-1/"
        try:
            response = requests.request(
                "POST",
                url=player_search_url,
                headers=api_key_header,
                data=player_display_info_payload,
                timeout=10,
            )
            if response:
                response.raise_for_status()
            else:
                return False
        except requests.exceptions.RequestException as e:
            print(f"ERROR: Error getting membership data: {e}")
            return False
        if response.status_code != 200:
            print("ERROR: Status code not 200")
            return False

        data = orjson.loads(response.content)
        if len(data["Response"]) == 0:
            return False

        self.member_id = data["Response"][0]["membershipId"]
        self.member_type = data["Response"][0]["membershipType"]
        return True

    def process(self):
        self.pull_membership_data()
        if (self.member_id == 0) or (self.member_type == 0):
            print("ERROR: Cannot process: No member info")
            return False

        with requests.Session() as session:
            session.headers.update(api_key_header)
            retry_config = Retry(
                total=3, backoff_factor=1, status_forcelist=[500, 501, 502, 503, 504]
            )
            adapter = HTTPAdapter(
                max_retries=retry_config, pool_connections=10, pool_maxsize=10
            )
            session.mount("https://", adapter=adapter)
            session.mount("http://", adapter=adapter)

            profile_and_metric_data = self.pull_data(
                session=session,
                url=f"https://www.bungie.net/Platform/Destiny2/{self.member_type}/Profile/{self.member_id}/?components=200,1100",
            )
            if profile_and_metric_data is None:
                return False
            if self.process_profile_data(data=profile_and_metric_data):
                print("INFO: Profile data processed")
            else:
                print("ERROR: Profile data failed to process")
                return False

            aggregate_data = self.pull_data(
                session=session,
                url=f"https://www.bungie.net/Platform/Destiny2/{self.member_type}/Account/{self.member_id}/Stats/?groups=1",
            )
            if aggregate_data is None:
                print("ERROR: Aggregate data failed to pull")
                return False
            else:
                print("INFO: Aggregate data pulled")

            for character_id, character in self.characters.items():
                exotic_data = self.pull_data(
                    session=session,
                    url=f"https://www.bungie.net/Platform/Destiny2/{self.member_type}/Account/{self.member_id}/Character/{character_id}/Stats/UniqueWeapons/",
                )
                if exotic_data is None:
                    print("ERROR: Exotic data failed to pull")
                    return False
                character["exotics"] = exotic_data

                raid_dungeon_data = self.pull_data(
                    session=session,
                    url=f"https://www.bungie.net/Platform/Destiny2/{self.member_type}/Account/{self.member_id}/Character/{character_id}/Stats/AggregateActivityStats/",
                )
                if raid_dungeon_data is None:
                    print("ERROR: Raid/Dungeon data failed to pull")
                    return False
                character["raidDungeon"] = raid_dungeon_data

                if self.process_heatmap_for_character(
                    session=session, character_id=character_id
                ):
                    print(f"INFO: Heatmap for {character_id} processed")
                else:
                    print(f"ERROR: Heatmap for {character_id} failed to process")
                    return False

        if self.process_metric_data(data=profile_and_metric_data):
            print("INFO: Metric data processed")
        else:
            return False

        if self.process_account_aggregate(data=aggregate_data):
            print("INFO: Aggregate data processed")
        else:
            return False

        if self.process_exotics():
            print("INFO: Exotic data processed")
        else:
            return False

        if self.process_raid_dungeon():
            print("INFO: Raid/Dungeon data processed")
        else:
            return False

        return True

    def process_profile_data(self, data: bytes):
        # character_data_url = f"https://www.bungie.net/Platform/Destiny2/{self.member_type}/Profile/{self.member_id}/?components=200,1100"
        character_response_data = orjson.loads(data)["Response"]["characters"]["data"]

        total_playtime = 0
        races = {0: "Human", 1: "Awoken", 2: "Exo"}
        classes = {0: "Titan", 1: "Hunter", 2: "Warlock"}
        for ch_number in range(0, len(character_response_data)):
            character_id = list(character_response_data)[ch_number]
            total_playtime += int(
                character_response_data[character_id]["minutesPlayedTotal"]
            )
            self.characters.update(
                {
                    f"{character_id}": {
                        "id": character_response_data[character_id]["characterId"],
                        "timePlayed": str(
                            datetime.timedelta(
                                minutes=int(
                                    character_response_data[character_id][
                                        "minutesPlayedTotal"
                                    ]
                                )
                            )
                        ),
                        "timePlayedRaw": character_response_data[character_id][
                            "minutesPlayedTotal"
                        ],
                        "lightLevel": character_response_data[character_id]["light"],
                        "race": races[
                            character_response_data[character_id]["raceType"]
                        ],
                        "class": classes[
                            character_response_data[character_id]["classType"]
                        ],
                        "emblemPath": character_response_data[character_id][
                            "emblemPath"
                        ],
                        "emblemHash": character_response_data[character_id][
                            "emblemHash"
                        ],
                        # Bugged?
                        # "titleHash": character_response_data[character_id]["titleRecordHash"],
                        "pctStrand": 0,
                        "pctStasis": 0,
                        "pctVoid": 0,
                        "pctArc": 0,
                        "pctSolar": 0,
                        "exotics": bytes,
                        "raidDungeon": bytes,
                        "heatmapURL": "",
                    }
                }
            )

        self.account["aggregates"]["playtime"] = datetime.timedelta(
            minutes=total_playtime
        )
        return True

    def process_metric_data(self, data: bytes):
        metrics_response_data = orjson.loads(data)["Response"]["metrics"]["data"][
            "metrics"
        ]
        for subclass, hash in self.metrics_defs["subclassDefeats"].items():
            self.account["subclassDefeats"][subclass] = metrics_response_data[
                f"{hash}"
            ]["objectiveProgress"]["progress"]
        # AGGREGATES CALCULATE THIS BETTER
        # for weaponArch, hash in self.metrics_defs["weapons"].items():
        #     self.account["weapons"][weaponArch] = metrics_response_data[f"{hash}"]["objectiveProgress"]["progress"]
        for element, hash in self.metrics_defs["finalBlows"].items():
            self.account["finalBlows"][element] = metrics_response_data[f"{hash}"][
                "objectiveProgress"
            ]["progress"]
        for metric, hash in self.metrics_defs["extra"].items():
            self.account["extra"][metric] = metrics_response_data[f"{hash}"][
                "objectiveProgress"
            ]["progress"]

        # Gets the class/emblemHash/weapon archetype of the character with most time played
        self.account["main"]["class"] = self.characters[
            max(self.characters, key=lambda c: max(self.characters[c]["timePlayedRaw"]))
        ]["class"]
        self.account["main"]["emblemHash"] = self.characters[
            max(self.characters, key=lambda c: max(self.characters[c]["timePlayedRaw"]))
        ]["emblemHash"]
        self.account["main"]["weaponArchetype"] = max(
            self.account["weapons"], key=self.account["weapons"].get
        )

        # Get subclass use breakdown
        # Instantiate as 1 to prevent divide by zero

        # totalWarlock = 1
        # totalHunter = 1
        # totalTitan = 1
        # for subclass, kills in self.account["subclassDefeats"].items():
        #     if subclass in ["Broodweaver", "Shadebinder", "Voidwalker", "Stormcaller", "Dawnblade"]:
        #         totalWarlock += kills
        #     elif subclass in ["Threadrunner", "Revenant", "Nightstalker", "Arcstrider", "Gunslinger"]:
        #         totalHunter += kills
        #     elif subclass in ["Berserker", "Behemoth", "Sentinel", "Striker", "Sunbreaker"]:
        #         totalTitan += kills

        # for _,char_data in self.characters.items():
        #     if char_data["class"] == "Warlock":
        #         char_data["pctStrand"] = 100 * round(self.account["subclassDefeats"]["Broodweaver"] / totalWarlock , 4)
        #         char_data["pctStasis"] = 100 * round(self.account["subclassDefeats"]["Shadebinder"] / totalWarlock , 4)
        #         char_data["pctVoid"] = 100 * round(self.account["subclassDefeats"]["Voidwalker"] / totalWarlock , 4)
        #         char_data["pctArc"] = 100 * round(self.account["subclassDefeats"]["Stormcaller"] / totalWarlock , 4)
        #         char_data["pctSolar"] = 100 * round(self.account["subclassDefeats"]["Dawnblade"] / totalWarlock , 4)
        #     if char_data["class"] == "Hunter":
        #         char_data["pctStrand"] = 100 * round(self.account["subclassDefeats"]["Threadrunner"] / totalHunter , 4)
        #         char_data["pctStasis"] = 100 * round(self.account["subclassDefeats"]["Revenant"] / totalHunter , 4)
        #         char_data["pctVoid"] = 100 * round(self.account["subclassDefeats"]["Nightstalker"] / totalHunter , 4)
        #         char_data["pctArc"] = 100 * round(self.account["subclassDefeats"]["Arcstrider"] / totalHunter , 4)
        #         char_data["pctSolar"] = 100 * round(self.account["subclassDefeats"]["Gunslinger"] / totalHunter , 4)
        #     if char_data["class"] == "Titan":
        #         char_data["pctStrand"] = 100 * round(self.account["subclassDefeats"]["Berserker"] / totalTitan , 4)
        #         char_data["pctStasis"] = 100 * round(self.account["subclassDefeats"]["Behemoth"] / totalTitan , 4)
        #         char_data["pctVoid"] = 100 * round(self.account["subclassDefeats"]["Sentinel"] / totalTitan , 4)
        #         char_data["pctArc"] = 100 * round(self.account["subclassDefeats"]["Striker"] / totalTitan , 4)
        #         char_data["pctSolar"] = 100 * round(self.account["subclassDefeats"]["Sunbreaker"] / totalTitan , 4)

        # Get element use breakdown
        totalElements = (
            1
            + self.account["finalBlows"]["strand"]
            + self.account["finalBlows"]["stasis"]
            + self.account["finalBlows"]["solar"]
            + self.account["finalBlows"]["arc"]
            + self.account["finalBlows"]["void"]
        )
        self.account["finalBlows"]["total"] = (
            self.account["finalBlows"]["strand"]
            + self.account["finalBlows"]["stasis"]
            + self.account["finalBlows"]["solar"]
            + self.account["finalBlows"]["arc"]
            + self.account["finalBlows"]["void"]
        )
        self.account["finalBlowsPcts"]["pctStrand"] = 100 * round(
            self.account["finalBlows"]["strand"] / totalElements, 4
        )
        self.account["finalBlowsPcts"]["pctStasis"] = 100 * round(
            self.account["finalBlows"]["stasis"] / totalElements, 4
        )
        self.account["finalBlowsPcts"]["pctVoid"] = 100 * round(
            self.account["finalBlows"]["void"] / totalElements, 4
        )
        self.account["finalBlowsPcts"]["pctArc"] = 100 * round(
            self.account["finalBlows"]["arc"] / totalElements, 4
        )
        self.account["finalBlowsPcts"]["pctSolar"] = 100 * round(
            self.account["finalBlows"]["solar"] / totalElements, 4
        )

        return True

    def process_account_aggregate(self, data: bytes):
        account_data = orjson.loads(data)["Response"]["mergedAllCharacters"]["merged"][
            "allTime"
        ]
        self.account["weapons"]["Auto Rifle"] = int(
            account_data["weaponKillsAutoRifle"]["basic"]["value"]
        )
        self.account["weapons"]["Trace Rifle"] = int(
            account_data["weaponKillsBeamRifle"]["basic"]["value"]
        )
        self.account["weapons"]["Bow"] = int(
            account_data["weaponKillsBow"]["basic"]["value"]
        )
        self.account["weapons"]["Glaive"] = int(
            account_data["weaponKillsGlaive"]["basic"]["value"]
        )
        self.account["weapons"]["Fusion Rifle"] = int(
            account_data["weaponKillsFusionRifle"]["basic"]["value"]
        )
        self.account["weapons"]["Hand Cannon"] = int(
            account_data["weaponKillsHandCannon"]["basic"]["value"]
        )
        # Yes this one is confusing
        self.account["weapons"]["Linear Fusion Rifle"] = int(
            account_data["weaponKillsTraceRifle"]["basic"]["value"]
        )
        self.account["weapons"]["Machine Gun"] = int(
            account_data["weaponKillsMachineGun"]["basic"]["value"]
        )
        self.account["weapons"]["Pulse Rifle"] = int(
            account_data["weaponKillsPulseRifle"]["basic"]["value"]
        )
        self.account["weapons"]["Rocket Launcher"] = int(
            account_data["weaponKillsRocketLauncher"]["basic"]["value"]
        )
        self.account["weapons"]["Scout Rifle"] = int(
            account_data["weaponKillsScoutRifle"]["basic"]["value"]
        )
        self.account["weapons"]["Shotgun"] = int(
            account_data["weaponKillsShotgun"]["basic"]["value"]
        )
        self.account["weapons"]["Sniper Rifle"] = int(
            account_data["weaponKillsSniper"]["basic"]["value"]
        )
        self.account["weapons"]["Submachine Gun"] = int(
            account_data["weaponKillsSubmachinegun"]["basic"]["value"]
        )
        self.account["weapons"]["Sidearm"] = int(
            account_data["weaponKillsSideArm"]["basic"]["value"]
        )
        self.account["weapons"]["Sword"] = int(
            account_data["weaponKillsSword"]["basic"]["value"]
        )
        self.account["weapons"]["Grenade Launcher"] = int(
            account_data["weaponKillsGrenadeLauncher"]["basic"]["value"]
        )

        self.account["aggregates"]["activitiesCleared"] = int(
            account_data["activitiesCleared"]["basic"]["value"]
        )
        self.account["aggregates"]["assists"] = int(
            account_data["assists"]["basic"]["value"]
        )
        self.account["aggregates"]["kills"] = int(
            account_data["kills"]["basic"]["value"]
        )
        self.account["aggregates"]["precisionKills"] = int(
            account_data["precisionKills"]["basic"]["value"]
        )
        self.account["aggregates"]["deaths"] = int(
            account_data["deaths"]["basic"]["value"]
        )
        self.account["aggregates"]["suicides"] = int(
            account_data["suicides"]["basic"]["value"]
        )
        self.account["aggregates"]["resurrectionsPerformed"] = int(
            account_data["resurrectionsPerformed"]["basic"]["value"]
        )
        self.account["aggregates"]["killsDeathsRatio"] = round(
            account_data["killsDeathsRatio"]["basic"]["value"], 2
        )
        self.account["aggregates"]["killsDeathsAssists"] = round(
            account_data["killsDeathsAssists"]["basic"]["value"], 2
        )
        self.account["aggregates"]["relicKills"] = int(
            account_data["weaponKillsRelic"]["basic"]["value"]
        )
        self.account["aggregates"]["grenadeKills"] = int(
            account_data["weaponKillsGrenade"]["basic"]["value"]
        )
        self.account["aggregates"]["meleeKills"] = int(
            account_data["weaponKillsMelee"]["basic"]["value"]
        )
        self.account["aggregates"]["superKills"] = int(
            account_data["weaponKillsSuper"]["basic"]["value"]
        )
        self.account["aggregates"]["longestSingleLife"] = account_data[
            "longestSingleLife"
        ]["basic"]["displayValue"]
        self.account["aggregates"]["orbsDropped"] = int(
            account_data["orbsDropped"]["basic"]["value"]
        )
        self.account["aggregates"]["orbsGathered"] = int(
            account_data["orbsGathered"]["basic"]["value"]
        )
        self.account["aggregates"]["publicEventsCompleted"] = int(
            account_data["publicEventsCompleted"]["basic"]["value"]
        )
        self.account["aggregates"]["combatRating"] = round(
            account_data["combatRating"]["basic"]["value"], 2
        )
        return True

    def process_exotics(self):
        for character_id, character in self.characters.items():
            for weapon in orjson.loads(character["exotics"])["Response"]["weapons"]:
                self.exotics[self.exotic_defs[weapon["referenceId"]]]["kills"] += int(
                    weapon["values"]["uniqueWeaponKills"]["basic"]["value"]
                )
                self.exotics[self.exotic_defs[weapon["referenceId"]]][
                    "precision"
                ] += int(
                    weapon["values"]["uniqueWeaponPrecisionKills"]["basic"]["value"]
                )
            print(f"INFO: Exotics for {character_id} processed")
        self.exotics = dict(
            sorted(
                self.exotics.items(),
                key=lambda item: itemgetter("kills")(item[1]),
                reverse=True,
            )
        )
        return True

    def process_raid_dungeon(self):
        for character in self.characters.values():
            activity_list = orjson.loads(character["raidDungeon"])["Response"][
                "activities"
            ]
            for activity in activity_list:
                if activity["activityHash"] in self.raid_hashes:
                    raid = self.raid_hashes[activity["activityHash"]]
                    # Need to check for the fastest
                    if activity["values"]["fastestCompletionMsForActivity"]["basic"][
                        "value"
                    ] > 0 and (
                        self.raids[raid]["fastest"] == 0.0
                        or (
                            self.raids[raid]["fastest"] != 0
                            and self.raids[raid]["fastest"]
                            > activity["values"]["fastestCompletionMsForActivity"][
                                "basic"
                            ]["value"]
                        )
                    ):
                        self.raids[raid]["fastest"] = int(
                            activity["values"]["fastestCompletionMsForActivity"][
                                "basic"
                            ]["value"]
                            * 0.001
                        )
                    self.raids[raid]["clears"] += int(
                        activity["values"]["activityCompletions"]["basic"]["value"]
                    )
                    self.raids[raid]["deaths"] += int(
                        activity["values"]["activityDeaths"]["basic"]["value"]
                    )
                    self.raids[raid]["kills"] += int(
                        activity["values"]["activityKills"]["basic"]["value"]
                    )
                    self.raids[raid]["playtime"] += int(
                        activity["values"]["activitySecondsPlayed"]["basic"]["value"]
                    )

                elif activity["activityHash"] in self.dungeon_hashes:
                    dungeon = self.dungeon_hashes[activity["activityHash"]]
                    # Need to check for the fastest
                    if activity["values"]["fastestCompletionMsForActivity"]["basic"][
                        "value"
                    ] > 0 and (
                        self.dungeons[dungeon]["fastest"] == 0.0
                        or (
                            self.dungeons[dungeon]["fastest"] != 0
                            and self.dungeons[dungeon]["fastest"]
                            > activity["values"]["fastestCompletionMsForActivity"][
                                "basic"
                            ]["value"]
                        )
                    ):
                        self.dungeons[dungeon]["fastest"] = int(
                            activity["values"]["fastestCompletionMsForActivity"][
                                "basic"
                            ]["value"]
                            * 0.001
                        )
                    self.dungeons[dungeon]["clears"] += int(
                        activity["values"]["activityCompletions"]["basic"]["value"]
                    )
                    self.dungeons[dungeon]["deaths"] += int(
                        activity["values"]["activityDeaths"]["basic"]["value"]
                    )
                    self.dungeons[dungeon]["kills"] += int(
                        activity["values"]["activityKills"]["basic"]["value"]
                    )
                    self.dungeons[dungeon]["playtime"] += int(
                        activity["values"]["activitySecondsPlayed"]["basic"]["value"]
                    )

        total = {
            "sortOrder": 9999,
            # "launches": 0,
            "clears": 0,
            "kills": 0,
            "deaths": 0,
            "ratio": 0.0,
            "fastest": 0,
            "playtime": 0,
            # "flawless": False,
            # "contest": False,
        }

        for raid in self.raids.values():
            raid["ratio"] = (
                round(raid["kills"] / raid["deaths"], 2)
                if raid["deaths"] > 0
                else raid["kills"]
            )

            total["clears"] += raid["clears"]
            total["kills"] += raid["kills"]
            total["deaths"] += raid["deaths"]
            total["playtime"] += raid["playtime"]

            raid["playtime"] = str(datetime.timedelta(seconds=raid["playtime"]))
            raid["fastest"] = str(datetime.timedelta(seconds=raid["fastest"]))

        total["playtime"] = str(datetime.timedelta(seconds=total["playtime"]))
        total["ratio"] = (
            round(total["kills"] / total["deaths"], 2)
            if total["deaths"] > 0
            else total["kills"]
        )
        self.raids.update({"Raids: Total": total})
        self.raids["Leviathan"]["sortOrder"] = 10
        self.raids["Eater of Worlds"]["sortOrder"] = 20
        self.raids["Spire of Stars"]["sortOrder"] = 30
        self.raids["Scourge of the Past"]["sortOrder"] = 40
        self.raids["Crown of Sorrow"]["sortOrder"] = 50
        self.raids["Last Wish"]["sortOrder"] = 60
        self.raids["Garden of Salvation"]["sortOrder"] = 70
        self.raids["Deep Stone Crypt"]["sortOrder"] = 80
        self.raids["Vault of Glass"]["sortOrder"] = 90
        self.raids["Vow of the Disciple"]["sortOrder"] = 100
        self.raids["King's Fall"]["sortOrder"] = 110
        self.raids["Root of Nightmares"]["sortOrder"] = 120
        self.raids["Atraks Sovereign"]["sortOrder"] = 130
        self.raids["Oryx Exalted"]["sortOrder"] = 140
        self.raids["Rhulk Indomitable"]["sortOrder"] = 150
        self.raids["Nezarec Sublime"]["sortOrder"] = 160
        self.raids["Crota's End"]["sortOrder"] = 170
        self.raids["Salvation's Edge"]["sortOrder"] = 180
        self.raids["The Desert Perpetual"]["sortOrder"] = 190
        self.raids["The Desert Perpetual (Epic)"]["sortOrder"] = 200
        self.raids["Calus Resplendent"]["sortOrder"] = 210
        self.raids["Morgeth Surpassing"]["sortOrder"] = 220
        self.raids["Insurrection Prime Revolutionary"]["sortOrder"] = 230
        self.raids = dict(
            sorted(
                self.raids.items(),
                key=lambda item: itemgetter("sortOrder")(item[1]),
                reverse=True,
            )
        )

        total = {
            "sortOrder": 9999,
            # "launches": 0,
            "clears": 0,
            "kills": 0,
            "deaths": 0,
            "ratio": 0.0,
            "fastest": 0,
            "playtime": 0,
            # "flawless": False,
            # "contest": False,
        }

        for dungeon in self.dungeons.values():
            dungeon["ratio"] = (
                round(dungeon["kills"] / dungeon["deaths"], 2)
                if dungeon["deaths"] > 0
                else dungeon["kills"]
            )

            total["clears"] += dungeon["clears"]
            total["kills"] += dungeon["kills"]
            total["deaths"] += dungeon["deaths"]
            total["playtime"] += dungeon["playtime"]

            dungeon["playtime"] = str(datetime.timedelta(seconds=dungeon["playtime"]))
            dungeon["fastest"] = str(datetime.timedelta(seconds=dungeon["fastest"]))

        total["playtime"] = str(datetime.timedelta(seconds=total["playtime"]))

        total["ratio"] = (
            round(total["kills"] / total["deaths"], 2)
            if total["deaths"] > 0
            else total["kills"]
        )
        self.dungeons.update({"Dungeons: Total": total})
        self.dungeons["The Shattered Throne"]["sortOrder"] = 10
        self.dungeons["Pit of Heresy"]["sortOrder"] = 20
        self.dungeons["Prophecy"]["sortOrder"] = 30
        self.dungeons["Grasp of Avarice"]["sortOrder"] = 40
        self.dungeons["Duality"]["sortOrder"] = 50
        self.dungeons["Spire of the Watcher"]["sortOrder"] = 60
        self.dungeons["Ghosts of the Deep"]["sortOrder"] = 70
        self.dungeons["Warlord's Ruin"]["sortOrder"] = 80
        self.dungeons["Vesper's Host"]["sortOrder"] = 90
        self.dungeons["Sundered Doctrine"]["sortOrder"] = 100
        self.dungeons["Equilibrium"]["sortOrder"] = 110
        self.dungeons = dict(
            sorted(
                self.dungeons.items(),
                key=lambda item: itemgetter("sortOrder")(item[1]),
                reverse=True,
            )
        )

        return True

    def process_heatmap_for_character(self, character_id, session: requests.Session):
        last_year_date = (
            datetime.datetime.today()
            .replace(year=datetime.datetime.now().year - 1)
            .isoformat()[0:10]
        )
        full_date_list = []

        # Instantiate with non-relevant value for if no playtime in past year
        unique_date_list = ["0001-01-01"]
        unique_date_value_list = [0]

        done_collecting = False
        for page in range(0, 10):
            if done_collecting:
                break
            character_data_url = f"https://www.bungie.net/Platform/Destiny2/{self.member_type}/Account/{self.member_id}/Character/{character_id}/Stats/Activities/?page={page}&count=250"
            activity_data = self.pull_data(session=session, url=character_data_url)
            if activity_data is None:
                print(
                    f"ERROR: Heatmap data failed to pull for {character_id} page {page}"
                )
                return False
            else:
                print(f"INFO: Heatmap page {page} pulled for {character_id}")

            response_content = orjson.loads(activity_data)["Response"]
            if len(response_content) == 0:
                break
            for activity in response_content["activities"]:
                if activity["period"][0:10] < last_year_date:
                    done_collecting = True
                    break
                full_date_list.append(activity["period"][0:10])
            date_counts = Counter(full_date_list)
            for date, count in date_counts.items():
                unique_date_list.append(date)
                unique_date_value_list.append(count)
            print(f"INFO: Historical heatmap page {page} processed for {character_id}")
            sleep(0.125)
        fig = Figure(figsize=(12, 6))
        ax = fig.subplots()
        colors = ["#323232", "#fafaf0"]
        color_map = LinearSegmentedColormap.from_list("jotunn", colors, N=256)
        dp.calendar(
            dates=unique_date_list,
            values=unique_date_value_list,
            start_date=last_year_date,
            end_date=datetime.datetime.today().isoformat()[0:10],
            boxstyle="round",
            color_for_none="#00000000",
            edgecolor="#fafaf0",
            edgewidth=0.1,
            cmap=color_map,
            day_kws={"size": 0, "color": "#00000000"},
            month_kws={"size": 0, "color": "#00000000"},
            day_x_margin=0,
            month_y_margin=0,
            ax=ax,
        )
        buf = BytesIO()
        fig.savefig(buf, transparent=True, format="png", bbox_inches="tight")
        buf.seek(0)
        self.characters[character_id]["heatmapURL"] = base64.b64encode(
            buf.getvalue()
        ).decode("utf-8")
        return True
