# -*- coding: utf-8 -*-
"""
@author: Blopa
"""

import json
import nltk
import simplenlg

# NLTK tags reference: https://www.clips.uantwerpen.be/pages/mbsp-tags

# Some downloads that might be needed if not previously installed
"""nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('maxent_ne_chunker')
nltk.download('words')"""

# List of pronouns
all_pronouns = {
	'first_singular': {'subjective':'I', 'objective':'me', 'reflexive':'myself', 'possessive_adj':'my',	'possessive_obj':'mine'},
	'second_singular': {'subjective':'you', 'objective':'you', 'reflexive':'yourself', 'possessive_adj':'your',	'possessive_obj':'yours'},
	'third_male':{'subjective':'he', 'objective':'him', 'reflexive':'himself', 'possessive_adj':'his',	'possessive_obj':'his'},
	'third_female':{'subjective':'she', 'objective':'her', 'reflexive':'herself', 'possessive_adj':'her',	'possessive_obj':'hers'},
	'third_thing':{'subjective':'it', 'objective':'it', 'reflexive':'itself', 'possessive_adj':'its',	'possessive_obj':'its'},
	'first_plural':{'subjective':'we', 'objective':'us', 'reflexive':'ourselves', 'possessive_adj':'our',	'possessive_obj':'ours'},
	'second_plural':{'subjective':'you', 'objective':'you', 'reflexive':'yourselves', 'possessive_adj':'your',	'possessive_obj':'yours'},
	'third_plural':{'subjective':'they', 'objective':'them', 'reflexive':'themselves', 'possessive_adj':'their',	'possessive_obj':'theirs'}
}

# Pronouns to be precalculated
calculate_pronouns = ['third_male','third_female','third_plural']

# List of verbs, used as reference; not complete nor perfect but good enough
# Obtained from: http://www.ashley-bovan.co.uk/words/partsofspeech.html from Ashley Bovan
with open("31K verbs.txt","r") as txt:
	verbs = txt.read().splitlines()
	# Some added verbs that might be needed, list may be extended
	verbs.extend(['do','be','is','honors','over-extends','micromanages'])

with open('tarot_meanings_extract.json', 'r') as meanings_file:
	tarot = json.load(meanings_file)
	tarot['description'] += " with generated stories"
	# Modify story_telling in cases needed: some of court cards require modification
	for card in tarot['interpretations']:
		for tell_index in range(len(card['fortune_telling'])):
			tell = card['fortune_telling'][tell_index]
			if tell.startswith("This card "):
				tell = tell[tell.find("with ")+5:tell.find(",",tell.find(",")+1)]
				card['fortune_telling'][tell_index] = tell.replace(","," and").capitalize() + " is coming your way"
	# Generate stories
	lexicon = simplenlg.lexicon.XMLLexicon()
	factory = simplenlg.NLGFactory(lexicon)
	realiser = simplenlg.Realiser()
	# For each card in the tarot
	for card in tarot['interpretations']:
		card['stories'] = {}
		# For all the pronouns
		for pronoun_type in all_pronouns:
			# In the list
			if pronoun_type not in calculate_pronouns:
				continue
			pronouns = all_pronouns[pronoun_type]
			person = pronouns['subjective']
			p = factory.createClause()
			p.setSubject(person)
			card['stories'][pronoun_type] = {}
			# For each of the two possible interpretations (light/shadow)
			for side in card['meanings']:
				card['stories'][pronoun_type][side] = {'infinitive':[] ,'past': [], 'present':[], 'present_participle': [], 'future': [] }
				# And for each of the meanings, calculate the infinitive, past, present, present_participle and future tenses of the meaning
				for meaning in card['meanings'][side]:
					# Separate merged words, tokenize and tag
					story = meaning.lower().replace("you're","you are").replace("you've","you have")
					tokens = nltk.word_tokenize(story)
					tagged = nltk.pos_tag(tokens)
					# Verb at first position is assumed
					transform_verb = True
					subjective_pronoun = False
					past = ""
					present = ""
					present_participle = ""
					future = ""
					infinitive=""
					print_trigger = False
					for tagged_index,tag in enumerate(tagged):
						space = ("" if tagged_index==0 else " ")
						# If word is verb and verbs needs to be transformed (first verb) or comes after subjective pronoun
						if (transform_verb or subjective_pronoun) and tag[1][0]=='V':
							root = tag[0][:tag[0].find("ing")]
							p.setFeature(simplenlg.Feature.FORM,simplenlg.Form.NORMAL)
							p.setVerb(tag[0])
							p.setTense(simplenlg.Tense.PAST)
							verb = realiser.realiseSentence(p).lower()[len(person)+1:-1]
							# If initial detection fails, try to detect root
							if verb.find("inged")>=0:
								p.setVerb(root)
								verb = realiser.realiseSentence(p).lower()[len(person)+1:-1]
								if verb not in verbs:
									p.setTense(simplenlg.Tense.PRESENT)
									p.setFeature(simplenlg.Form,simplenlg.Form.INFINITIVE)
									verb = realiser.realiseSentence(p).lower()[len(person)+1:-1]
									# If rooted-verb fails to be tensed correctly, try other options
									if verb not in verbs:
										# If last two consonants are the same, remove one
										if len(root)>2 and root[-1]==root[-2]:
											print(verb)
											p.setVerb(root[:-1])
										# If ends in -ck, drop the k
										elif root.endswith("ck"):
											# Document error for verb mimic
											p.setVerb(root[:-1])
										# Else try adding and -e, e.g: deceiving -> deceiv -> deceive
										else:
											p.setVerb(root+"e")
										verb = realiser.realiseSentence(p).lower()[len(person)+1:-1]
										# Error verbs, unknown verbs
										if verb not in verbs:
											pass
											#print(story)
											#print(verb)
							# Past tense
							p.setFeature(simplenlg.Feature.TENSE,simplenlg.Tense.PAST)
							past+=space + realiser.realiseSentence(p).lower()[len(person)+1:-1]
							# Future tense
							p.setFeature(simplenlg.Feature.TENSE,simplenlg.Tense.FUTURE)
							future +=space + realiser.realiseSentence(p).lower()[len(person)+1:-1]
							# Present tense
							p.setFeature(simplenlg.Feature.TENSE,simplenlg.Tense.PRESENT)
							present +=space + realiser.realiseSentence(p).lower()[len(person)+1:-1]
							# Presente_participle tense
							# Added <= 1 because some sentences started with adverb -> verb, and there's no verb-verb case (I believe)
							present_participle +=space + (tag[0] if tagged_index<=1 else realiser.realiseSentence(p).lower()[len(person)+1:-1])
							# Infinitive tense
							p.setFeature(simplenlg.Feature.FORM,simplenlg.Form.BARE_INFINITIVE)
							infinitive +=space + realiser.realiseSentence(p).lower()[len(person)+1:-1]
							transform_verb = False
						else:
							# TODO: Add modification so that if "not - verb" then, do negation and don't deactivate subjective_pronoun
							subjective_pronoun = False
							# Replaces pronouns in 2nd person to the new person's 
							if tag[0] in all_pronouns['second_singular'].values():
								if tag[0].endswith("self"):
									word=space+pronouns['reflexive']
								elif tag[1]=='PRP$':
									word=space+pronouns['possessive_adj']
								elif (tagged_index+1==len(tagged)) or (tagged[tagged_index+1][1] in ['IN','(']) or (tagged[tagged_index+1][1]=='VB' and tagged[tagged_index-1][1]=='VBZ'):
									word=space+pronouns['objective']
								elif tagged[tagged_index+1][1]=='.':
									word=space+tag[0]
								else:
									word=space+pronouns['subjective']
									subjective_pronoun = True
							else:
								word=("" if tag[0]==',' else space)+tag[0]
							# After a CC, see if next word is gerund verb which is part of sentence
							if tag[1]=="CC" and tagged[tagged_index+1][1]=='VBG' and tagged[tagged_index+1][0] not in ["misguiding","teaching"]:
								transform_verb = True
							past += word
							present += word
							present_participle += word
							future += word
							infinitive += word
					if print_trigger:
						print(past)
						print(future)
						print(present)
						print(present_participle)
						print(infinitive)
					# Add stories
					card['stories'][pronoun_type][side]['infinitive'].append(infinitive)
					card['stories'][pronoun_type][side]['past'].append(past)
					card['stories'][pronoun_type][side]['present'].append(present)
					card['stories'][pronoun_type][side]['present_participle'].append(present_participle)
					card['stories'][pronoun_type][side]['future'].append(future)
	# Save as json
	with open('tarot_stories.json', 'w') as tarot_out:
		json.dump(tarot, tarot_out,indent = 4)
		