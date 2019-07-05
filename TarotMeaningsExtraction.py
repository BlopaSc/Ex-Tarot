# -*- coding: utf-8 -*-
"""
@author: Blopa
"""


"""
Structure of the processed text:

tarot_meanings.txt:
	> Starts with the first card of the major arcana (Trump 0: The Fool)
	> Each card follows the following structure:
		<name of card>
		<empty line>
		Keywords
			<Keywords>
		Range of Meaning
			Light: <Light Meaning>
			Shadow: <Shadow Meaning>
		Correspondences
			<Correspondences, must include "Story: " subsection>
		Advice
			<Advice, must include "Fortune Telling. " subsection>
		Symbols and Insights
			<Symbols>
		Question to Ask
			<Questions>
		<empty line>
		<empty line>
	> After each card, another card starts unless at the EOF
"""

import re
import json

filename = "tarot_meanings.txt"

# Regular expression patterns for the text
name_pattern = ".+\n\s*\n"
subsection_pattern = "(\s|\*)\s.+\n"
section_pattern = ".+\n("+subsection_pattern+")+"
end_pattern = "\n\n"

name_regex = re.compile(name_pattern)
section_regex = re.compile(section_pattern)
subsection_regex = re.compile(subsection_pattern)
end_regex = re.compile(end_pattern)

# Names of the minor arcana ranks and their numeric value conversion
minor_ranks = {
		"Ace":1,
		"Two":2,
		"Three":3,
		"Four":4,
		"Five":5,
		"Six":6,
		"Seven":7,
		"Eight":8,
		"Nine":9,
		"Ten":10,
		"Page":11,
		"Knight":12,
		"Queen":13,
		"King":14
}

with open(filename,"r") as tarot:
	lines = tarot.readlines()
	index = 0
	cards = []
	card = {}
	reader = ""
	# Process all lines of the text document tarot_meanings.txt 
	while index < len(lines):
		# Cummulative reader, keeps adding text (line by line) until satifies regex
		reader += lines[index]
		# If matches card name regex
		if name_regex.match(reader):
			if reader.startswith("Trump"):
				# Major Arcana
				reader = reader[6:reader.find("\n")]
				card['name'] = reader[(reader.find(":")+2):]
				card['suit'] = "major"
				card['rank'] = int(reader[:reader.find(":")])
			else:
				# Minor Arcana
				reader = reader[:reader.find("\n")]
				card['name'] = reader
				card['suit'] = reader[(reader.find(" of ")+4):].lower()
				card['rank'] = minor_ranks[reader[:reader.find(" of ")]]
			reader = ""
		# If matches section regex (section header and 1 or more subsections)
		elif section_regex.match(reader):
			# If at EOF or end of section (end of section = no more subsections next) then process section
			if index+1 == len(lines) or subsection_regex.match(lines[index+1]) is None:
				section = reader[:reader.find("\n")]
				subsection = reader[(reader.find("\n")+1):]
				if section == "Keywords":
					# Keyword extraction
					card['keywords'] = subsection[2:subsection.find("\n")].lower().split(", ")
				elif section == "Range of Meaning":
					# Meanings extraction
					meanings = {}
					for sub in subsection.split("\n"):
						sub = sub[2:]
						if sub.startswith("Light: "):
							meanings['light'] = sub[7:sub.rfind(".")].split(". ")
						elif sub.startswith("Shadow: "):
							meanings['shadow'] = sub[8:sub.rfind(".")].split(". ")
					card['meanings'] = meanings
				elif section == "Advice":
					# Fortune telling extraction
					for sub in subsection.split("\n"):
						sub = sub[2:]
						if sub.startswith("Fortune Telling. "):
							card['fortune_telling'] = sub[17:sub.rfind(".")].split(". ")
				reader = ""
		# If matches end of card regex or no more lines to read
		if end_regex.match(reader) or index+1==len(lines):
			# Add the card collected to the dictionary
			cards.append(card)
			card = {}
			reader = ""
		index += 1
	tarot_meanings = {}
	tarot_meanings['description'] = "Tarot card interpretations from Mark McElroy's \"A Guide to Tarot Meanings\" (http://tarottools.com/2014/07/06/my-latest-book-belongs-to-you/)"
	tarot_meanings['interpretations'] = cards
	
	with open('major_arcana_characterizations.json','r') as characterizations:
		loaded = json.load(characterizations)
		chars = loaded['characterizations']
		for card in tarot_meanings['interpretations']:
			if card['suit']=='major':
				card['characterizations'] = chars[card['rank']]
	
	# Save as json
	with open('tarot_meanings_extract.json', 'w') as tarot_out:
		json.dump(tarot_meanings, tarot_out,indent = 4)
		   