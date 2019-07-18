from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = 'Imports Word Frequeencies into Database'

    def add_arguments(self, parser):
        parser.add_argument('wordlist', nargs=1, type=str)

    def handle(self, *args, **options):
        
        import_wordfreq(options['wordlist'][0])

        self.stdout.write(self.style.SUCCESS('Successfully imported word frequencies'))


from project.api.models import Word, Form, Sense, Gloss
import csv, sys

def import_wordfreq(wordlist):

    lists = {'wikipdia':'wordfreq_JaWikipedia.txt', 'mainichi':'wordfreq_MainichiShimbun.txt', 'internet':'wordfreq_Internet.txt'}

    if wordlist == 'internet':
        delim, index = ' ', 2
    else:
        delim, index = '\t', 0

    #import pdb; pdb.set_trace()

    # Open List
    with open('project/api/jmdict/' + lists[wordlist]) as f:

        reader = csv.reader(f,delimiter=delim)
    
        # Loop through contents
        for order, row in enumerate(reader):
            
            # Search for Form 
            token = row[index]
            forms = Form.objects.filter(characters=token)

            # Update 
            if len(forms) == 1:
                freq_order = forms[0].freq_order
                freq_order[wordlist] = order
                forms[0].freq_order = freq_order

                sys.stdout.write('\r')
                sys.stdout.write("good: %d: %s         " % (order,token))
                sys.stdout.flush()

            else:

                sys.stdout.write('\r')
                sys.stdout.write("pass: %d: %s         " % (order,token))
                sys.stdout.flush()

