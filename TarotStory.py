# -*- coding: utf-8 -*-
"""
@author: Blopa
"""

import json
import random

def calculate_combinations(n,cards,sides,avg_meanings,persons,times):
	perm = 1
	for i in range(n):
		perm *= (cards-i)
	return perm * ((sides*avg_meanings*persons*times)**n) 
	

def print_combination_info(tarot):
	cards = len(tarot['interpretations'])
	sides = len(tarot['interpretations'][0]['meanings'])
	avg_meanings = sum([sum([len(card['meanings'][key]) for key in card['meanings']]) for card in tarot['interpretations']])/(len(tarot['interpretations']) * len(tarot['interpretations'][0]['meanings']))
	print("Cards: %i, sides: %i, meanings per side: %.2f" %(cards,sides,avg_meanings))
	persons = len(tarot['interpretations'][0]['stories'])
	times = len(tarot['interpretations'][0]['stories']['third_male']['light'])
	print("Persons: %i, times: %i"%(persons,times))
		
	print("Possible combinations for n-cards:\n\nP(%i,n)*(%i*%.2f*%i*%i)^n\nP(%i,n)*(%.3f)^n\n\n"%(cards,sides,avg_meanings,persons,times,cards,(sides*avg_meanings*persons*times)))
	print("Previous formula: P(%i,n)*(%i*1*1*4)^n = P(%i,n)*8^n\n\n"%(cards,sides,cards))
	
	print("Comparison:\nn\tOld\tNew\tIncrease")
	for i in range(1,7+1):
		old =  calculate_combinations(i,cards,sides,1,1,4)
		new = calculate_combinations(i,cards,sides,avg_meanings,persons,times)
		print("%i:\t%i\t%i\t%.2f"%(i, old, new, new/old))
	
	print("\n")

with open('tarot_stories.json', 'r') as stories_file:
	tarot = json.load(stories_file)		
	with open('story_templates.json','r') as templates_file:
		
		templates = json.load(templates_file)
		
		output = "THIS "+random.choice(templates['seasons'])+", "+random.choice(random.choice(tarot['interpretations'])['fortune_telling']).lower()+"<br><br>"

		story_type = random.choice(templates['story_types'])
		
		story = templates[story_type]['story']
		idents = templates[story_type]['identifiers']
		
		cards = random.sample(tarot['interpretations'],story.count('$'))
		# Sample major arcana characters
		
		for i in range(story.count('$')):
			
			if idents[i][0]=='character':
				pass
				# get random major arcana character
			elif idents[i][0]=='story':
				story = story.replace("$",random.choice(cards[i]['stories'][idents[i][3]][idents[i][1]][idents[i][2]]),1)
		output += story
		print(output.replace("<br>","\n"))
		