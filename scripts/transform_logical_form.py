class LexicalEntry:
    def __init__(self, type, lex, aliases):
        self.type = type
        self.lex = lex
        self.aliases = aliases
        self.is_pred = type[-2] == 't'
    
    def in_sentence(self, sentence):
        for alias in self.aliases:
            if sentence.lower().find(alias) != -1:
                return True
        return False
    def __str__(self):
        return "%s:%s" % (self.lex, self.type)        

class ParenForm:
    def __init__(self, paren_form, sentence):
        self.paren_form = paren_form
        self.sentence = sentence
        self.num_tracks = 0 # will be updated when combining entities
        self.LEXICAL_ENTRIES = {'a': [LexicalEntry('<<e,e>,t>', 'approach', ['approached']), LexicalEntry('<tr,e>', 'andrei', ['andrei'])],
                'd': [LexicalEntry('<tr,e>', 'danny', ['danny'])],
                'c': [LexicalEntry('<tr,e>', 'chair', ['chair'])],
                'y': [LexicalEntry('<e,t>', 'yellow', ['yellow']), LexicalEntry('<tr,e>', 'yevgeni', ['yevgeni'])],
                'b': [LexicalEntry('<tr,e>', 'bag', ['bag']), LexicalEntry('<e,t>', 'blue', ['blue'])],
                'h': [LexicalEntry('<<e,e>,t>', 'has', ['has', 'holding', 'held'])],
                'g': [LexicalEntry('<e,t>', 'green', ['green'])],
                'p': [LexicalEntry('<tr,e>', 'person', ['person'])],
                'l': [LexicalEntry('<<e,e>,t>', 'leave', ['left'])],
                't': [LexicalEntry('<tr,e>', 'telescope', ['telescope'])],
                'pu': [LexicalEntry('<<e,e>,t>', 'pick-up', ['picked-up', 'picking-up', 'moved', 'move'])],
                'la': [LexicalEntry('<<e,e>,t>', 'look-at', ['looked at'])],
                'm': [LexicalEntry('<<e,e>,t>', 'move', ['moving', 'moved'])],
                'pd': [LexicalEntry('<<e,e>,t>', 'put-down', ['putting-down', 'put-down', 'moved'])],
                'b1': [LexicalEntry('<tr,e>', 'bag', ['bag'])],
                'b2': [LexicalEntry('<tr,e>', 'bag', ['bag'])],
                'p1': [LexicalEntry('<tr,e>', 'person', ['person', 'someone', 'andrei', 'danny'])],
                'p2': [LexicalEntry('<tr,e>', 'person', ['person', 'someone', 'andrei', 'danny'])],
                'c1': [LexicalEntry('<tr,e>', 'chair', ['chair'])],
                'c2': [LexicalEntry('<tr,e>', 'chair', ['chair'])]}
        
        self.variable_map = {}

    def get_pred_tuples(self):
        return [tup.replace('(', '').replace(')', '').split() for tup in self.paren_form.split(') (')]
    
    def get_entry(self, abbrev, is_pred):
        possibilities = self.LEXICAL_ENTRIES[abbrev] # will throw key error if self.entities isn't complete
        for possibility in possibilities:
            if possibility.in_sentence(self.sentence) and is_pred == possibility.is_pred:
                return possibility
        else:
            if abbrev in ['h', 'g', 'y']:
                for entry in self.LEXICAL_ENTRIES[abbrev]:
                    if entry.lex in ['has', 'green', 'yellow']:
                        return entry
                
        raise ValueError("Cannot find entry for %s in sentence %s" % (abbrev, self.sentence))

    def combine_tuple(self, pred_tuple):
        predicate = self.get_entry(pred_tuple[0], True)
        args = map(lambda x: self.get_entry(x, False), pred_tuple[1:])
        string = str(predicate) + " "
        for arg in args:
            string += "(%s) " % self.get_entity_str(arg)
        return string.strip()

    def combine_all_tuples(self, tuples):
        string = "and:<t*,t> "
        for tuple in tuples:
            string += "(%s) " % self.combine_tuple(tuple)
        for entry, var in self.variable_map.items():
            string += "(%s %s) " % (str(entry), var)
        return string.strip()

    def parse(self):
        tuples = self.get_pred_tuples()
        tuple_strings = self.combine_all_tuples(tuples)
        string = ""
        for i in range(self.num_tracks):
            string += "(lambda $%d:tr " % i
        string += "(%s)%s" % (tuple_strings, ")"*self.num_tracks)
        return string

    def get_entity_str(self, entry):
        if entry in self.variable_map:
            variable = self.variable_map[entry]
        else:
            variable = "$%d" % self.num_tracks
            self.variable_map[entry] = variable
            self.num_tracks += 1 
        return "%s %s" % (str(entry), variable)



