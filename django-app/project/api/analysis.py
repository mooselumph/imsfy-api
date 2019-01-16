#from py4j.java_gateway import JavaGateway
from natto import MeCab
import re
    
def get_sentences(blocks):

    blocks = segment_blocks(blocks)
    sentences = unblock_sentences(blocks)
    sentences = tokenize_sentences(sentences)

    return sentences
    

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
                
        #return els
        return {'type':'sentence','text':text,'elements':els}


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
    end = [{'type':'paragraph'}]    
    for block in blocks:
        sentences = sentences + block + end

    return sentences
      
def tokenize_sentences(sentences,dictionary='ipadic'):
    
    #gateway = JavaGateway()    
    #tokenizer = gateway.entry_point.getTokenizer(dictionary)
       
    
    def tokenize_element(el):
        
        with MeCab() as nm:

            if 'content' in el:
            
                #tokens = tokenizer.tokenize(el['content']);                
                #token.getSurface() + "\t" + token.getAllFeatures()
                
                tokens = nm.parse(el['content'], as_nodes=True)
                                
                el['tokens'] = [token.surface + ',' + token.feature for token in tokens]
                
            return el
        
    def tokenize_sentence(sentence):
        if (sentence['type']=='sentence'):
            sentence['elements'] = [tokenize_element(el) for el in sentence['elements']]
        return sentence
        
    sentences = [tokenize_sentence(sentence) for sentence in sentences]

    return sentences
  
def tokenize_text(sentence):
    
    with MeCab(r'-F%m,%f[0],%h,%f[8]\n -U?,?,?,?\n') as nm:  

        summary = []
        for n in nm.parse(sentence, as_nodes=True):
            # only normal nodes, ignore any end-of-sentence and unknown nodes
            if n.is_nor():
                summary.append(n.feature)

    return summary
    
def tokenize_text_old(sentence,dictionary='ipadic'):

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