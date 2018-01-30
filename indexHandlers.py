import xml.etree.ElementTree as ET
import operator
import math


def normalIndexToXml(index, xmlFile):

    print index
    print xmlFile
    
    root = ET.Element("index")
    for text_id in index:
        keimeno = ET.SubElement(root, "keimeno")
        keimeno.set("id", text_id)
        print "Number of entries:: " + str(len(index[text_id]))
        for l in index[text_id]:
            lemma = ET.SubElement(keimeno, "lemma")
            lemma.set("name", l)
            lemma.set("weight", str(index[text_id][l]))
             
    tree = ET.ElementTree(root)
    tree.write(xmlFile)

def invertedIndexToXml(inverted_index, xmlFile):
    root = ET.Element("inverted_index")

    for l in inverted_index:
        lemma = ET.SubElement(root, "lemma")
        lemma.set("name", l)
        for d in inverted_index[l]:
            doc = ET.SubElement(lemma, "document")
            doc.set("id", d)
            doc.set("weight", str(inverted_index[l][d]))    
    
    tree = ET.ElementTree(root)
    tree.write(xmlFile)
        
def loadNormalIndex(xmlFile):
    """ fortonei to index apo xml se dictionary morfi. Elegxoume to onoma tou root. 
        An einai sosto theoroume oti to xml einai well-formed. 
        """
    index = {}
    
    # fortosi tou xml
    try:
        tree = ET.ElementTree(file=xmlFile)
    except IOError as e:
        print "Lathos kata ti fortosi tou Xml error: " + e.strerror
        return {}
    
    # pairnoume to root. Ola ta ids einai paidia tou root
    root = tree.getroot()
    if root.tag != 'index':
        print "Lathos euretirio"
        return {}
    
    ch = root.getchildren()
    
    for keimenoElem in ch:
        keimeno = keimenoElem.items()
        text_id = keimeno[0][1]
        index[text_id] = {}
        # tora pairnoume tou leimata tou keimenou me id 
        lemmata = keimenoElem.getchildren()
        for lemma in lemmata:
            props = lemma.items()
            name = props[0][1]
            weight = props[1][1]
            index[text_id][name] = float(weight)
            
    return index
        
def loadRevIndex(xmlFile):
    """ fortonei to inverted index apo xml se dictionary morfi. Elegxoume to onoma tou root. 
        An einai sosto theoroume oti to xml einai well-formed. 
        """
    index = {}
    
    # fortosi tou xml
    try:
        tree = ET.ElementTree(file=xmlFile)
    except IOError as e:
        print "Lathos kata ti fortosi tou Xml error: " + e.strerror
        return {}
    
    # pairnoume to root. Ola ta ids einai paidia tou root
    root = tree.getroot()
    
    if root.tag != 'inverted_index':
        print "Lathos euretirio"
        return {}
    
    ch = root.getchildren()
    
    for lemmaElem in ch:
        lemma = lemmaElem.items()
        name = lemma[0][1]
        index[name] = {}
        # tora pairnoume tou leimata tou keimenou me id 
        keimena = lemmaElem.getchildren()
        for keimeno in keimena:
            props = keimeno.items()
            text_id = props[0][1]
            weight = props[1][1]
            index[name][text_id] = weight
            
    return index        

def powerTo2(x):
    return x*x

def searchInNormalWithCosSim(index, terms):
    if not isinstance (terms, list):
        print "Doste ta orismata mesa se mia lista"
        return [-1]*len(terms)
    foundTexts = []
    for text_id in index.keys():
        validKeimeno = False
        for term in terms:
            if term in index[text_id]:
                validKeimeno = True
            else: # an vroume esto enan oro pou den einai stamatame
                validKeimeno = False
                break
        if validKeimeno:
            foundTexts.append(text_id)
    # gia kathe keimeno vres to cosine similarity
    finalAnswer = {}
    
    for text in foundTexts:
        # esoteriko ginomeno. Arkoun mono oi mi midenikoi oroi
        esgin = 0
        for term in terms:
            if term in index[text]:
                esgin += index[text][term] # * 1 apo to query vector peritto na to kanoume
        queryVectorLength = math.sqrt(len(terms)) # dianisma mono me asous |V| = sqrt(total asoi)
        # telos mikos tou dianismatos tou keimenou
        textVectorLen = map(powerTo2, index[text].values())
        textVectorLen= sum ( textVectorLen )
        
        finalAnswer[text] = esgin / ( queryVectorLength * textVectorLen ) 
    return sorted( finalAnswer.iteritems(), key=operator.itemgetter(1), reverse=True)
    
def searchInNormal(index, terms):
    if not isinstance (terms, list):
        print "Doste ta orismata mesa se mia lista"
        return [-1]*len(terms)
    # gia kathe oro pou briskoume theloume na kratama varos kai id gia opou ton briskoume. 
    # tha to kanoume se mia lista apo listes. I mitriki lista tha xei toses ypolistes osoi kai 
    # oi oroi. Kathe ipolista tha exei ola ta ids kai ta vari pou briskame
    result_list = [ ] * len(terms)
    for i in terms:
        result_list.append( {} )
    
    for text_id in index.keys():
        """ me to kanoniko euretirio prepei na pame se kathe id kai na doume an yparxei o oros
            ekei. efoson koitame kathe id einai pio apotelesmatiko na psaxoume gia olous tous
            orous anti na to xanatrexoume gia ton kathe oro """
        for pos,term in enumerate(terms):
            if term in index[text_id]:
                result_list[ pos ][text_id] = index[text_id][term]
    
    
    # sort ta apotelesmata prin ta epistrepsoume
    for pos,term_res in enumerate(result_list):
        result_list[pos] = sorted( term_res.iteritems(), key=operator.itemgetter(1), reverse=True)
        
    return result_list
        
def searchInReversed(index, terms):
    if not isinstance (terms, list):
        print "Doste ta orismata mesa se mia lista"
        return [-1]*len(terms)
    # gia kathe oro pou briskoume theloume na kratame varos kai id gia opou ton briskoume. 
    # tha to kanoume se mia lista apo listes. I mitriki lista tha xei toses ypolistes osoi kai 
    # oi oroi. Kathe ipolista tha exei ola ta ids kai ta vari pou briskame
    result_list = [ ] * len(terms)
    for i in terms:
        result_list.append( {} )
    
    for pos,term in enumerate(terms):
        # kateutheian ta keimena me tous orous
        result_list[pos] = index[term]
    
    # an exoume pano apo ena orous dose mono ta keimena pou xoun kai tous dio orous
    return result_list    
