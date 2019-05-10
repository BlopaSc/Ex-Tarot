# -*- coding: utf-8 -*-
"""
@author: Blopa
"""

import json
import random

with open('tarot_stories.json', 'r') as stories_file:
	tarot = json.load(stories_file)		
	
	with open('story_templates.json','r') as templates_file:
		templates = json.load(templates_file)
		
		output = "THIS "+random.choice(templates['seasons'])+", "+random.choice(random.choice(tarot['interpretations'])['fortune_telling']).lower()+"<br><br>"

		story_type = random.choice(templates['story_types'])
		
		story = templates[story_type]['story']
		tenses = templates[story_type]['tenses']
		person = templates[story_type]['person']
		sides = templates[story_type]['sides']
		
		characters = sum([tense=='character' for tense in tenses])
        
		cards = random.sample(tarot['interpretations'],len(tenses))
        # Sample major arcana characters
        
		for i in range(len(sides)):
			
			if tenses[i]=='character':
				pass
				# get random major arcana character
			else:
				story = story.replace("$"+str(i),random.choice(cards[i]['stories'][person[i]][sides[i]][tenses[i]]))
		output += story
		print(output.replace("<br>","\n"))
		