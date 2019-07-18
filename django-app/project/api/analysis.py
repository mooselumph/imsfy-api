#from py4j.java_gateway import JavaGateway
from natto import MeCab
import re
from .app_settings import SEARCHABLE_POSID
    
def get_sentences(blocks):

    blocks = segment_blocks(blocks)
    sentences = unblock_sentences(blocks)
    words = tokenize_sentences(sentences)

    return sentences, words
    

def segment_blocks(blocks):
        
    blocks = [segment_block(block) for block in blocks]
    
    return blocks
    
def segment_block(block):
        
    def chunk_els(block):
    
        nonlocal chunks
        
        text = ''
        for el in block:
            if el['type'] == 'text':
                text = text + el['content']
            elif el['type'] in ['link','img']:        
                text = text + '<e' + str(len(chunks)) + '>'
                chunks.append(el)
                
        return text
    
    def unchunk_els(text):
            
        nonlocal chunks
    
        segments = re.split('(<e[0-9]+>)',text)
        
        els = []        
        for segment in segments:
            m = re.match('<e([0-9]+)>',segment)
            if m:
                idx = int(m.group(1))
                els.append(chunks[idx])
            else:
                if segment:
                    els.append({'type':'text','content':segment})
        
        fulltext = ''
        for el in els:
            if 'content' in el:
                fulltext += el['content']

        #return els
        return {'category':'sentence','text':fulltext,'elements':els}


    def chunk_quotes(text):
    
        nonlocal quotes
        
        iter = re.finditer(r"「[^「『」』]+」|『[^「『」』]+』",text)
        matches = [match for match in iter]
        
        if not matches:        
            return text
        else:
            for match in reversed(matches):
                n = len(quotes)
                quotes.append(match.group())
                text = text[:match.start()] + '<q' + str(n) + '>' + text[match.end() + 1:]
            return chunk_quotes(text)

    def unchunk_quotes(text):
        
        nonlocal quotes        
        for idx,quote in reversed(list(enumerate(quotes))):
            text = text.replace('<q' + str(idx) + '>',quote);
            
        return text
        
                
    # Create block of text with placeholders for hyperlinks and images
    chunks = []    
    text = chunk_els(block)
    
    # Create block of text with placeholders for quotes
    quotes = []    
    text = chunk_quotes(text)
    
    # Perform sentence segmentation
    sentences = re.findall(r".+?(?:[。？！]|$)",text)
    
    # Unchunk quotes
    sentences = [unchunk_quotes(sentence) for sentence in sentences]
    
    # Unchunk elements
    sentences = [unchunk_els(sentence) for sentence in sentences]

    return sentences

def unblock_sentences(blocks):
        
    sentences = []
    end = [{'category':'paragraph'}]    
    for block in blocks:
        sentences = sentences + block + end

    return sentences
      
def tokenize_sentences(sentences,dictionary='ipadic'):   

    article_words = set()

    for sentence in sentences:
        words = set()
        if (sentence['category']=='sentence'):
            for el in sentence['elements']:
                if 'content' in el:
                    el['tokens'],el_words = tokenize_text(el['content'])
                    words = words | el_words # Union of sets
            sentence['words'] = list(words)
            article_words = article_words | words

    return list(article_words)

def tokenize_text(text):

    # https://github.com/buruzaemon/natto-py/wiki/Output-Formatting
    # Ex. custom node format
    #
    # -F         ... short-form of --node-format
    # %F,[6,8,0] ... extract these elements from ChaSen feature as CSV
    #                - morpheme root-form (6th index)
    #                - reading (7th index)
    #                - part-of-speech (0th index)
    # %h         ... part-of-speech ID (IPADIC) (https://github.com/buruzaemon/natto/wiki/Node-Parsing-posid)
    #
    # -U         ... short-form of --unk-format
    #                specify empty CSV ,,, when morpheme cannot be found
    #                in dictionary
    #
        
    tokens = []
    words = set()

    with MeCab(r'-F%F,[6,8,0],%h\n -U,,,\n') as nm:
            
            for n in nm.parse(text, as_nodes=True):
                if not n.is_eos():
                    tokens.append(n.surface + ',' + n.feature)

                    parts = n.feature.split(',')

                    if n.is_nor() and int(parts[3]) in SEARCHABLE_POSID:
                        words.add(parts[0])

    return tokens,words

def tokenize_text_old(sentence):


    with MeCab(r'-F%F,[6,8,0],%h\n -U,,,\n') as nm:
    #with MeCab(r'-F%m,%f[0],%h,%f[8]\n -U?,?,?,?\n') as nm:  

        summary = []
        for n in nm.parse(sentence, as_nodes=True):
            # only normal nodes, ignore any end-of-sentence and unknown nodes
            if n.is_nor():
                summary.append(n.feature)

    return summary
    
def tokenize_text_java(sentence,dictionary='ipadic'):

    gateway = JavaGateway()    
    tokenizer = gateway.entry_point.getTokenizer(dictionary)

    tokens = tokenizer.tokenize(sentence);

    summary = []
    
    if dictionary == 'ipadic':
        labels = 'surface form,pos1,pos2,pos3,pos4,conj type,conj form,base form,reading,pronunciation'
    elif dictionary == 'naist-jdic':
        labels = 'surface form,pos1,pos2,pos3,pos4,conj type,conj form,base form,reading,pronunciation,transcription variation,compound info'
    elif dictionary == 'unidic':
        labels = 'surface form,pos1,pos2,pos3,pos4,conj form,conj type,lemma reading form, lemma form,pronunciation,*base form,written from,*base form,language type,initial sound alternation type,sound alteration form,final sound alteration type,final sound alteration form'
    elif dictionary == 'unidic-kanaaccent':
        labels = 'surface form,pos1,pos2,pos3,pos4,conj form,conj type,lemma reading form, lemma form,pronunciation,*base form,written from,*base form,language type,initial sound alternation type,sound alteration form,final sound alteration type,final sound alteration form,kana,kana base form,form,form base,initial connection type,final connection type,accent type,accent connection type,accent modification type'
    elif dictionary == 'jumandic':
        labels = 'surface form,pos1,pos2,pos3,pos4,base form,reading,semantic information'
    else:
        labels = ''
        
    summary.append(labels.split(','))

    for token in tokens:
        features = token.getSurface() + "," + token.getAllFeatures()
        summary.append(features.split(','))

    return summary