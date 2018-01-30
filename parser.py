import nltk
import subprocess
from BeautifulSoup import BeautifulStoneSoup


class xmlToIndex:
    __openClassWords = ['JJ','JJR','JJS','RB','RBR','RBS','NN','NNS','NNP','NNPS','VB','VBD','VBG','VBN','VBP','FW']
    __stopClassWords = ['CD','CC','DT','EX','IN','LS','MD','PDT','POS','PRP','PRP$','RP','TO','UH','WDT','WP','WP$','WRB']
    
    def filenameToId(self):
        # H me8odos strip afairei apo to string o,ti tou dw8ei ws eisodos.
        tmp = self.fileName.strip(".xml")   
        split_list = tmp.split("_")
        if len(split_list) < 3:
            return None
        return split_list[2]
    
    def __init__(self, xmlFile, outdir):
        self.fileName = xmlFile
        # diabase to xml arxeio
        self.file_id = self.filenameToId()
        
        if self.file_id is None:
            return
        self.tokensDestination = outdir + "\\tmp" + "\\tokens." + self.file_id + ".txt";
        self.taggerDestination = outdir + "\\tmp" + "\\tagged." + self.file_id + ".txt";
        self.indexDir = outdir + "\\index"
        
        # fortonoume to xml arxeio
        xml = open(xmlFile)
        xmlContent = xml.read()
        xml.close()
        
        # metetrepse to xml se plain text
        textFromXml = self.xmlToText(xmlContent).lower()
        self.parsedXml = textFromXml
        
        # stelnoume to keimeno ston tokenizer
        tokens = nltk.tokenize.word_tokenize(textFromXml)
        
        
        # sozoume tous tokens se ena arxeio kratontas mono tis lexeis
        self.tokensToFile(tokens)
        
        # to tokensDestination exei pleon tous tokens apo to nltk. Ora gia ton TreeTagger
        self.tagTokens()
        
        # filtraroume tin exodo tou tree tagger
        self.filterTaggerOutput()
    
    __ignored_tokens = [ ':', '[', ']', '+', '=', ';', '|', '<', '>', '.', '{', '}', '"', '!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '_', '-', '/', '?', "'"]

    def xmlToText(self, content):
        soup = BeautifulStoneSoup(content)
        #pattern = re.escape(''.join(self.__ignored_tokens))
        
        """ To at einai to parse tree pou dhmiourgeitai apo th diatrexh
         tou xml eggrafou. Sth sygkekrimenh periptwsh to <page> 8ewreitai
         o pateras kai ta ypoloipa 8ewrountai paidia"""
         
        tags = soup.findAll('text', recursive=True)
        pureText = ""
        for t in tags:
            if len(t.text) > 0:
                """ apo default to BeautifulSoup otan bgazei ta tags (p.x. <h1></h1>) kai ena tag den exei text
                    yparxei periptosi na to enosei me to onoma tou epomenou tag xoris keno
                    (px <h1>References</h1> <h1>Further</h1> kataligei na einai ReferencesFurther. ME to getText
                    kai separator to keno to xorizei sosta """
                text = t.getText(' ')                
                """ xrisimopoioume to regular expression gia na petaxoume olous tous periergous xarakties
                    to [0-9]+ petaei olous tous arithmous (px 1 123241 15124 3241 kok)
                    to [\:\[\]\+\=;\|\'<>,.{}"!@#$%^&*()_\-\/?] bgazei opoindipote apo autous tous xaraktires 
                    (xreiazetai na kanoume escape kapoious poy exoun idiaiteri simasia gia to regular expression
                    opos ta square brackets i to + ktl. "Pare thn pragmatiki shmasia tou xarakthra kai mhn
                    prospa8eis na ton ermhneyseis".)
                    Telos to [a-z]*&[a-z]*; afairei oti einai tis morfis word&amp; 
                    """
                # to regexp de xreiazetai telika. Kratame ta panta gia na ta dosoume sto tokenize    
                pureText += text + ' ' # to keno gia na mi mas enosei lexeis 
                #pureText += re.sub(r'[0-9]+|[\:\[\]\+\=\;\|\'\<\>\,\.\{\}\"\!\@\#\$\%\^\&\*\(\)\_\-\/\?]|[a-z]*&[a-z]*;', ' ', t.text) + '\n'
        return pureText
      
    def tokensToFile(self, tokens):
        out = open(self.tokensDestination, 'w')
        
        # prota xekatharizoume tis morfes ton tokens
        # regexp gia dekadikous [0-9]*\.[0-9]+
        placeToEdit = [] # de mporoume na svisoume/prothesoume oso trexoume ti lista. KRatame tis theseis edo kai kanoume editmeta
        
        for index,token in enumerate(tokens):
            # to tokenize tin ora ti spaei se 3 tokens. Ara o tagger tha mperdeftei
            """ i ora xorizetai apo : . Ara an to proigoumeno token einai arithmos kai to epomeno arithmos me am 
                i pm ta ennonoume (kai meta svinoume to proigoiumeno kai to epomeno). Dld to 12:33am ginetai 
                '12', ':', '33am' kai theloume na antikatastisoume to ':' me to '12:33am' kai na svisoume ta alla
                dio """  
            if token == ':' and index > 1 and tokens[index-1].isdigit() and index < len(tokens) -1 and tokens[index+1][0].isdigit(): # to teleutaio mporouse na nai regexp. An prolavo to allazo
                tokens[index] = tokens[index-1] + token + tokens[index+1]
                placeToEdit.append( [ index-1 ] )
                placeToEdit.append( [ index+1 ] )
            if '/' in token: # sindiasmos lexeon his/her ktl prepei na spasei se his, /, her
                splitter = token.find('/')
                placeToEdit.append( [ index-1, token[:splitter]])
                tokens[index] = '/'
                if not token.endswith('/'):
                    placeToEdit.append( [ index + 1 , token[splitter+1:] ] )
            elif len(token) > 1 and (token.endswith(',') or token.endswith('.')):
                placeToEdit.append( [index+1, token[-1] ] ) # krata to , i tin .
                tokens[index] = token[:-1]
            #elif ord( token[0] ) > 127 : # theloume mono ascii xaraktires. Ara os 127
                #placeToEdit.append( [ index ] )
                 
        # apo to telos pros ti arxi tou placeToEdit pame kai svinoume
        placeToEdit.reverse()
        for d in placeToEdit:
            # an to d exei len 1 einai gia svisimo
            if len(d) == 1:
                del tokens[ d[0] ]
            else: # allios theloume na prosthesoume
                tokens.insert(d[0], d[1])
        
        #try :
        bigStr = ""
        for i in tokens:
            bigStr += i + '\n'
        #except Exception as e:
        #    print "Error in " + self.fileName
        str2 = bigStr.encode('latin-1', 'replace')
        out.write(str2)
        out.close()
        
    def tagTokens(self):
        taggerPath = "C:\\TreeTagger\\bin\\tag-english.bat"
        subprocess.Popen( [taggerPath, self.tokensDestination, self.taggerDestination], stdout = subprocess.PIPE, stderr = subprocess.PIPE ).communicate()
    
    def filterTaggerOutput(self):
        tagged = open(self.taggerDestination,'r')
        #print "Fortosi tagged lexeon"
        cnt = 0
        self.lemma_dict = {}
        for line in tagged:
            # dioxe to newline '\n' kai xorise vasi ton tabs
            a = line.strip().split('\t')
            
            # i deuteri lexi se kathe grammi exei ton tipo tou lhmmatos
            if a[1] not in self.__stopClassWords:
                if "&" in a[2]: # basi forum theoreitai skoupidi kai to petame
                    continue
                if len(a[2]) < 2:
                    continue
                if a[2] not in self.lemma_dict:
                    self.lemma_dict[ a[2] ] = 1
                else:
                    self.lemma_dict[ a[2] ] += 1
                cnt += 1
        #print "Lemma  " + str ( len(self.lemma_dict) ) 
    
    def getLemmas(self):
        return self.lemma_dict
