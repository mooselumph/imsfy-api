from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = 'Imports JMdict'

    def handle(self, *args, **options):
        import_jmdict()
        self.stdout.write(self.style.SUCCESS('Successfully imported JMdict'))


from project.api.models import Word, Form, Sense, Gloss

from lxml import etree
import sys


def import_jmdict():

    tree = etree.parse("project/api/jmdict/JMdict_e.xml.gz")
    root = tree.getroot()

    # words = []
    # forms = []
    # senses = []
    # glosses = []

    # Word.objects.all().delete()
    # Form.objects.all().delete()
    # Sense.objects.all().delete()
    # Gloss.objects.all().delete()

    # Loop through elements (Use Iterparse?)
    for kk, entry in enumerate(root):

        if kk < 120852:
            continue  

        word = Word()
        #words.append(word)
        word.save()

        # Add k_ele
        order = 0
        for el in entry.xpath('k_ele'):

            characters = el.xpath('keb')[0].text
            info = el.xpath('ke_inf')[0].text if el.xpath('ke_inf') else ''
            priority = el.xpath('ke_pri')[0].text if el.xpath('ke_pri') else ''

            form = Form(order=order,category='kanji',word=word,characters=characters,information=info,priority=priority)
            #forms.append(form)
            form.save()

            order = order + 1
        
        # Add r_ele
        for el in entry.xpath('r_ele'):
            characters = el.xpath('reb')[0].text
            info = el.xpath('re_inf')[0].text if el.xpath('re_inf') else ''
            priority = el.xpath('re_pri')[0].text if el.xpath('re_pri') else ''

            form = Form(order=order,category='kana',word=word,characters=characters,information=info,priority=priority)
            #forms.append(form)
            form.save()

            order = order + 1

        # Add sense
        for ii, el in enumerate(entry.xpath('sense')):

            pos = el.xpath('pos')[0].text if el.xpath('pos') else ''
            field = el.xpath('field')[0].text if el.xpath('field') else ''
            misc = el.xpath('misc')[0].text if el.xpath('misc') else ''
            sense_information = el.xpath('s_inf')[0].text if el.xpath('s_inf') else ''

            if el.xpath('lsource'):
                source_lang = el.xpath('lsource')[0].attrib['xml:lang'] if ('xml:lang' in el.xpath('lsource')[0].attrib) else 'eng'
                source_word = el.xpath('lsource')[0].text if el.xpath('lsource')[0].text else ''
            else:
                source_lang, source_word = '',''

            sense = Sense(order=ii,word=word,pos=pos,field=field,misc=misc,sense_information=sense_information,source_lang=source_lang,source_word=source_word)
            sense.save()
            #senses.append(sense)

            # Add gloss
            for jj, el2 in enumerate(el.xpath('gloss')):
                gloss = Gloss(order=jj,sense=sense,text=el2.text)
                gloss.save()
                #glosses.append(gloss)

        #Show status
        if kk % 10 == 0:
            sys.stdout.write('\r')
            sys.stdout.write("%d" % (kk))
            sys.stdout.flush()

        # if kk % 10000 == 0 and kk > 0 and False:

        #     Word.objects.bulk_create(words)
        #     Form.objects.bulk_create(forms)
        #     Sense.objects.bulk_create(senses)
        #     Gloss.objects.bulk_create(glosses)

        #     words = []
        #     forms = []
        #     senses = []
        #     glosses = []

        #     print("Saved")