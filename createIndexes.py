import os
import shelve
import glob
import math
import parser as parser
import indexHandlers as handlers

afrodir="C:\\afro"
test = afrodir+"\\testing"      

  
def update_weights(normIndex, revIndex):

    totalKeimena = len(normIndex)

    for keimeno in normIndex:
        currentKeimeno = normIndex[keimeno]
        """ gia kathe lemma ipologizoume to varos. Kai gia na glitosoume xrono gia kathe
            oro enimeronoume to antistoixo baros gia to keimeno pou koitame.
            Oso trexoume to keimeno ipologizoume to athroisma ton tetragonon. Otan 
            teleiosoume me olous tous orous dieroume to freq*idf me ti riza tou athroismatos 
        """
        square_sum = 0
        for term in currentKeimeno:
            tf = currentKeimeno[term]
            # ipologismos idf
            ni = len(revIndex[term])
            idf = math.log10( float(totalKeimena) / float(ni) )
            # antikathistoume ti sixnotita me to freq*idf
            
            currentKeimeno[term] = tf*idf
            square_sum += math.pow( currentKeimeno[term], 2)
            
        euclid_len = math.sqrt(square_sum)
        for term in currentKeimeno:
            currentKeimeno[term] /= euclid_len
            """ ara xeroume to varous tou orou term gia to keimeno id.
            anti na xanatrexoume to revIndex mporoume na to kanoume kateutheian 
            update edo """
            revIndex[term][keimeno ] = currentKeimeno[term]  
            

xmlDir = "c:\\afro\\wiki-single"            
if __name__ == '__main__':
    # lista olon ton xml sto directory
    filelist = glob.glob(xmlDir + "\\*.xml")
    
    # elegxe an to basiko directory iparxei kai 
    # dimiourgise to directory pou tha sosoume ta tokenized
    if os.path.exists(afrodir) and not os.path.exists(test):
        os.mkdir(test)
        
    # theloume na ftiaxoume ena dictionary me ta ids kai ta full path
    
    normalIndex = {}
    reversedIndex = {}
    # me to shelve sozoume to dictionary sto skliro.
    idLexiko = shelve.open("C:\\afro\\index\\lexiko")
    
    # gia kathe arxeio metetrepse to xml se euretirio
    l = []
    for f in filelist:
        #print "Processing: " + f
        print ".",
        xti = parser.xmlToIndex(f, afrodir)
        
        # i xti.getLemmas mas epistrefei ta limmata. Ora na ta valoume sto euretirio
        normalIndex [ xti.file_id ] =  xti.getLemmas()

        #for i in normalIndex.keys():
        #    print "Len for " + i + ", " + str( len(normalIndex[i]) ) + " -- ",

        # gia to reversed theloume gia kathe limma na prosthesoume kati sto reversed
        for lemma,count in normalIndex[xti.file_id].items():
            if lemma not in reversedIndex:
                reversedIndex [ lemma ] = { xti.file_id:count}
            else:
                reversedIndex [ lemma ][xti.file_id] = count
        idLexiko["id"] = xti.file_id
        idLexiko["path"] = f
        del xti
    
    update_weights(normalIndex, reversedIndex)
    handlers.normalIndexToXml(normalIndex, afrodir + "\\index\\index.xml" )
    handlers.invertedIndexToXml(reversedIndex, afrodir + "\\index\\inverted_index.xml" )
    
    idLexiko.close()
    
