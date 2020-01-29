from lxml import etree
import glob
from bs4 import BeautifulSoup
import csv
import datetime

# Compile a list of all HTML files in your folder.

files = glob.glob('*.htm*')

date = datetime.datetime.now()

story_data_compiled = []

# Read in files one by one from the 'files' list and using lxml, extract
# the section of the HTML that contains the data values needed.

for f in files:
    with open(f, 'r') as fin:
        text = fin.read()

    soup = BeautifulSoup(text, 'html.parser')
    div = soup.find('div')
    html = div.prettify()
    tree = etree.fromstring(html)
    stories = tree.xpath('//li[@class = "work blurb group"]')
    for story in stories:

        # Extract the AO3 assigned id for each individual story appearing on the
        # search page for use as the basis of the unique id and add the string 'A-'
        # to the front to identify the data source the id came from.

        story_id_block = story.xpath('@id')
        source_story_id = 'A-' + story_id_block[0].split('_')[1]

        # Extract the date of publication as recorded automatically or input by the
        # author of the story. Reformat the date into a more uniform YYYY-MM-DD format.

        date_block = story.xpath('div/p[@class = "datetime"]/text()')
        date_clean = date_block[0].replace('\n', '').strip()
        ymd = date_clean.split(' ')
        month_formatted = ymd[1].replace('Jan', '01').replace('Feb', '02').replace('Mar', '03').replace('Apr', '04').replace('May', '05').replace('Jun', '06').replace('Jul', '07').replace('Aug', '08').replace('Sep', '09').replace('Oct', '10').replace('Nov', '11').replace('Dec', '12')
        date_formatted = ymd[2] + '-' + month_formatted + '-' + ymd[0]

        # Extract the list of character tags added by the author of the story. Combine
        # the list into a single string for storage purposes.

        character_block = story.xpath('ul/li[@class = "characters"]/a/text()')
        characters = []
        for character in character_block:
            character_clean = character.replace('\n', '').strip()
            characters.append(character_clean)
        character_blob = "||".join(characters)

        # Extract the list of relationship tags added by the author of the story. Combine
        # the list into a single string for storage purposes.

        relationship_block = story.xpath('ul/li[@class = "relationships"]/a/text()')
        relationships = []
        for relationship in relationship_block:
            relationship_clean = relationship.replace('\n', '').strip()
            relationships.append(relationship_clean)
        relationship_blob = "||".join(relationships)

        # Extract the series and media types identified by the author as the inspiration
        # for the story. Combine the list into a single string for storage purposes.

        series_block = story.xpath('div/h5/a/text()')
        series = []
        for media in series_block:
            media_clean = media.replace('\n', '').strip()
            series.append(media_clean)
        series_blob = "||".join(series)

        # Extract the word count and format to remove commas so that the value can be
        # parsed as a number.

        word_count_block = story.xpath('dl/dd[@class = "words"]/text()')
        word_count = word_count_block[0].replace('\n', '').replace(',', '').strip()

        # Extract the chapter count and format to retain only the number of actual
        # chapters (e.g., '2/4' becomes '2'). Parse as a number.

        chapters_block = story.xpath('dl/dd[@class = "chapters"]/text()')
        chapter_list = (chapters_block[0].replace('\n', '').strip()).split('/')
        chapters = chapter_list[0]

        # Extract the rating designated by the author from the required tags section.
        # The ratings will be coded against the FFN ratings later.

        rating_block = story.xpath('div[@class = "header module"]/ul[@class = "required-tags"]/li[1]/a/span/span/text()')
        rating = rating_block[0].replace('\n', '').strip()

        story_data = []
        story_data.append(source_story_id)
        story_data.append(date_formatted)
        story_data.append(character_blob)
        story_data.append(relationship_blob)
        story_data.append(series_blob)
        story_data.append(word_count)
        story_data.append(chapters)
        story_data.append(rating)

        story_data_compiled.append(story_data)

print('done')

headers = ['source_story_id', 'published', 'characters', 'relationships', 'series', 'word_count', 'chapters', 'rating']
with open('AO3_' + date.strftime('%Y%m%d') + '.csv', 'w', newline='') as outfile:
    csvout = csv.writer(outfile)
    csvout.writerow(headers)
    csvout.writerows(story_data_compiled)
