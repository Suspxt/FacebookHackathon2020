import re
import json
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from googlesearch import search
class main_intent:

    def __init__(self, entities, traits):
        self.entities = entities
        self.traits = traits
        self.new = False
        self.response = "I'm not sure what are you saying can you try rephrasing that"
        self.current_time = datetime.now()
        self.g_api_key = 'AIzaSyCE3wsY5xE41YPGVQavGq0EyVD1lo1b44Q'

class salutation(main_intent):

    def __init__(self, entities, traits):
        super().__init__(entities, traits)

    def generate_response(self):
        if 'wit$greetings' in self.traits and 'wit$bye' in self.traits:
            if self.traits['wit$greetings'][1] >= self.traits['wit$bye'][1]:
                del self.traits['wit$bye']
            else:
                del self.traits['wit$greetings']
        if 'wit$greetings' in self.traits:
            self.response = 'Whatsup!'
            if 'wit$contact' in self.entities:
                self.response = f"{self.response[:-1]} {self.entities['wit$contact']['val']}!"
        elif 'wit$bye' in self.traits:
            self.response = 'Cya!'


class express(main_intent):

    def __init__(self, entities, traits):
        super().__init__(entities, traits)

    def generate_response(self):
        pass



class find(main_intent):

    def __init__(self, entities, traits):
        super().__init__(entities, traits)
        self.curr_location, self.end_location = None, None

    def generate_response(self, new_ent=None, new_trait=None):
        if new_ent:
            self.entities = new_ent
        if new_trait:
            self.trait = new_trait

        def search_info(query):
            goal = [i for i in search(query + ' info', tld="com", num=1, stop=1, pause=1)][0]
            self.response = f'You should check out {goal}, hope this is helpful!'
            self.new = True

        if 'topic' in self.entities:
            search_info(self.entities['topic']['val'])

        elif 'facilities' in self.entities:
            if self.entities['facilities']['role'] != 'facilities':
                self.end_location = self.entities['facilities']['role']
            else:
                self.end_location = self.entities['facilities']['val']
            self.response = f"Where are you trying to reach the {self.end_location} from? I want to tell you the nearest one."

        elif 'wit$location' in self.entities:
            self.curr_location = self.entities['wit$location']['val']
            url = "https://maps.googleapis.com/maps/api/place/textsearch/json?"
            r = requests.get(url + 'query=' + self.end_location + '&open' + '&key=' + self.g_api_key)
            result = r.json()['results'][0]
            address = result['formatted_address']
            name = result['name']
            self.new = True
            self.response = f"{name} at {address} is the closest open place to the location you provided"

class criticism(main_intent):

    def __init__(self, entities, traits):
        super().__init__(entities, traits)
        self.review = set()

    def generate_response(self, utter):
        self.review.add((utter, datetime.now()))
        if 'wit$sentiment' in self.traits:
            if self.traits['wit$sentiment'][0] != 'negative':
                self.response = "Thank you for the kind words you're amazing c:"
                self.new = True
                return True
            else:
                self.response = "Sorry you feel that way would you like to tell us more?"
        else:
            self.response = "Okay, would you like to tell us more?"
        return False

    def more_criticism(self, utter):
        if 'no' in utter:
            self.response = "That's okay sorry the bot isn't perfect yet, we will take your words into consideration"
        else:
            self.review.add((utter, datetime.now()))
            self.response = "Ok noted, thank you we will check this out ASAP"
        self.new = True

class remind(main_intent):

    def __init__(self, entities, traits):
        super().__init__(entities, traits)
        self.datetime_obj, self.reminder, self.interval = None, None, None

    def generate_response(self, new_ent=None, new_trait=None):

        if new_ent:
            self.entities = new_ent
        if new_trait:
            self.trait = new_trait
        if 'wit$reminder' in self.entities:
            self.reminder = self.entities['wit$reminder']['val']
            if 'wit$duration' in self.entities:
                self.interval = self.entities['wit$duration']['seconds']
                self.response = f"Ok got it, you will be reminded about {self.reminder} every {self.entities['wit$duration']['val']}"
                self.new = True
            else:
                self.response = f"When would you want us to remind you about '{self.reminder}'?"

        elif 'wit$datetime' in self.entities:
            date, time = self.entities['wit$datetime']['val'].split('T')
            time = time[:time.find('-')]
            self.datetime_obj = datetime.strptime(' '.join([date, time]), '%Y-%m-%d %H:%M:%S.%f')
            x = self.datetime_obj.strftime("on %m-%d-%Y at %H:%M")
            self.response = f"Ok got it, you will be reminded about '{self.reminder}' {x}"
            self.new = True

class correct(main_intent):

    def __init__(self, entities, traits):
        super().__init__(entities, traits)

    def generate_response(self):
        pass

class information(main_intent):

    def __init__(self, entities, traits):
        super().__init__(entities, traits)

    def generate_response(self, new_ent=None, new_trait=None):

        if new_ent:
            self.entities = new_ent
        if new_trait:
            self.trait = new_trait

        if 'rona' in self.entities:
            role = self.entities['rona']['role']
            if role == 'rona':
                self.webcrawl('rona')
            else:
                with open('response.json', 'r') as cr:
                    rona_responses = json.load(cr)["corona"]
                self.response = rona_responses[role]
            self.new = True
        elif 'health' in self.entities:
            role = self.entities['health']['role']
            with open('response.json', 'r') as cr:
                health_responses = json.load(cr)["health"]
            self.response = health_responses[role]
            self.new = True

    def webcrawl(self, u):
        if u == 'rona':
            url = "https://www.cdc.gov/coronavirus/2019-ncov/cases-updates/cases-in-us.html"
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            stats = soup.findAll("div", class_="callout")
            target = stats[0].get_text().lower()
            target = re.findall("[a-zA-Z\b\d+\b,]+", target)
            target2 = stats[1].get_text().lower()
            target2 = re.findall("[a-zA-Z\b\d+\b,]+", target2)
            self.response = "Recent statistics state that there are "
            string1 = f"{' '.join(target[2::-1])} and within 24 hours there were {' '.join(target[3:])}.\n"
            string2 = f"Sadly the total death count is {target2[2]} and there were {' '.join(target2[3:])} yesterday."
            self.response += string1 + string2
        else:
            pass
            return None
