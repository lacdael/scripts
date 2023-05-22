#!/usr/bin/env python3
import sys;
import os;
import PyPDF2;
import tempfile;
import random
import string

letters = string.ascii_lowercase

def _getRandS():
    return ''.join(random.choice(letters) for i in range(12))

def _writeFile( out , path ):
    with open(path,"wb") as f:
        out.write(f);

def work( aFile ):
    pageCount = 0;
    h = 0;
    w = 0;
    #get doc info
    inFile = PyPDF2.PdfReader(open(aFile,"rb"));
    pageCount = len(inFile.pages);
    h = inFile.pages[0].mediabox.height;
    w = inFile.pages[0].mediabox.width;
    # print("len:",len(inFile.pages)," h:",h," w:",w );
    # make working dir
    aDir = tempfile.gettempdir()+"/"+_getRandS();
    os.mkdir(aDir);
    def _aBlankPage(n):
        path = aDir+"/"+str(n)+".pdf";
        outFile = PyPDF2.PdfWriter();
        outFile.add_blank_page(width=w,height=h);
        _writeFile(outFile,path);
    def _aPage( n , pageData):
        path = aDir+"/"+str(n)+".pdf";
        outFile = PyPDF2.PdfWriter();
        outFile.add_page( pageData );
        _writeFile(outFile,path);
    # Add start flyleaf
    ptr = 0;
    _aBlankPage(ptr);
    ptr += 1;
    _aBlankPage(ptr);
    ptr += 1;
    # pad with blanks to make page count a factor of 4
    if (pageCount+3) % 4 == 0:
        _aBlankPage(ptr);
        ptr += 1;
        _aBlankPage(ptr);
        ptr += 1;
    elif (pageCount+2) % 4 == 0:
        _aBlankPage(ptr);
        ptr += 1;
        _aBlankPage(ptr);
        ptr += 1;
    # add pages from in file
    for i in range(0,pageCount):
        _aPage( ptr , inFile.pages[i] );
        ptr += 1;
    # Add end flyleaf
    _aBlankPage(ptr);
    ptr += 1;
    _aBlankPage(ptr);
    ptr += 1;
    if (pageCount+3) % 4 == 0:
        _aBlankPage(ptr);
        ptr += 1;
    elif (pageCount+1) % 4 == 0:
        _aBlankPage(ptr);
        ptr += 1;
    # Get the section count
    newPageCount = ptr;
    pagesPerSection = newPageCount;
    opt = [];
    while pagesPerSection > 0:
        if (newPageCount%pagesPerSection) == 0 and pagesPerSection%4 == 0:
            opt.append(pagesPerSection)
        pagesPerSection -= 1;
    # present the options
    for i in range(0,len(opt)):
        print("\t[{}] section count:{} with {} pages".format(i+1,newPageCount/opt[i],opt[i]))
    v = 0;
    pagesPerSection = 0;
    try:
        v = int(input("please select an option: ")) -1;
        print("selected: section count:{} with {} pages".format(newPageCount/opt[v],opt[v]))
        pagesPerSection = opt[v];
    except:
        print("invalid input exiting");
        sys.exit(1);
    # get new page order
    start = 0;
    end = pagesPerSection;
    shuffled = [];
    pages = [ i for i in range(0,newPageCount) ];
    while start < newPageCount:
        mid = (end - start ) /2
        i = 0;
        while i < mid:
            #3,2,4,1 page order
            shuffled.append( pages[ end - i - 1 - 1] )
            shuffled.append( pages[ start + i + 1 ] )
            shuffled.append( pages[ end - i - 1] )
            shuffled.append( pages[ start + i ] )
            i += 2;
        start = end
        end += pagesPerSection;
    print( shuffled )
    # merge pages and for i in range(0,len(pages),4): rotate pages[ i + 1 ] and pages[ i + 2 ]
    _state = 0;
    outFile = PyPDF2.PdfWriter();
    for n in range(0,newPageCount):
        path = aDir+"/"+str(shuffled[n])+".pdf";


        if os.path.isfile( path ):
            reader = None;
            page = None;
            reader = PyPDF2.PdfReader(open(path,"rb"))
            page = reader.pages[0]
            if _state == 0 or _state == 1:
                page.rotate(180);
            outFile.add_page(page)
        else:
            print("Error, not a path: ",path)
        _state +=1;
        if _state > 3:
            _state = 0;
    # write new document to file
    pdfOut = open( os.path.splitext(os.path.basename(aFile))[0]+"-printspread.pdf",'wb');
    outFile.write(pdfOut);

def help( name ):
    print("pad and reorder a pdf file for a print spread\n\n{} <path to pdf file>".format(name));

if __name__ == '__main__':
    if len(sys.argv) != 2:
        help( sys.argv[0] );
    elif not os.path.isfile(sys.argv[1]):
        help( sys.argv[0] );
    else:
        work( sys.argv[1]);
