import requests
from google import search
from mutagen.id3 import ID3NoHeaderError
from bs4 import BeautifulSoup
import os
from mutagen.id3 import ID3, TIT2, TALB, TPE1, TPE2, COMM, USLT, TCOM, TCON, TDRC


def google_search(title, artist):
    search_string = "azlyrics " + title + " " + artist
    result = search(search_string)
    url = ''
    for url in result:
        # count += 1
        if "http://www.azlyrics.com" not in url:
            # if count==2:
            #     break
            break
        break
    return url


def parse(url, headers):
    source_code = requests.get(url, headers=headers, verify=True)
    plain_text = source_code.text
    # print(plain_text)
    soup = BeautifulSoup(plain_text, "lxml")
    for script in soup(["script", "style"]):
        script.extract()
    text = soup.get_text()
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = '\n'.join(chunk for chunk in chunks if chunk)

    text = text[text.find('Print'):]
    text = text[:text.find('Visit www.azlyrics.com for these lyrics')]
    lyrics = text
    run_once = 1
    return lyrics, run_once


def Embed(fpath, fn, failed, embedded, lyrics, tags):
    fname = os.path.join(fpath, fn)
    fail = 0
    embed = 0
    # print(fname)
    if fname.lower().endswith('.mp3'):
        #     tags=ID3(fname)
        #     if len(tags.getall('USLT::\'en\'')) != 0:
        #         tags.delall('USLT::\'en\'')
        #         print("removing lyrics")
        #         tags.save(fname)
        #         tags.save()
        tags["USLT"] = USLT(encoding=0, lang="eng", text=lyrics)
        tags.save(fname)
        tags.save()
        # print(tags['USLT'])
        lol = str(tags['USLT'])
        print(lol[50:150])

        if len(lol) < 50:

            print('----------------------------- FAILED=' + str(failed) + '----------------------')
            fail = 1
        else:
            print('------------------------ Lyrics Embedded=' + str(embedded) + '-----------------')
            embed = 1
        return fail, embed


def main():
    fpath = (os.path.abspath(''))
    embedded = 0
    failed = 0
    count = 0
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.0; WOW64; rv:24.0) Gecko/20100101 Firefox/24.0'}
    list_dir = os.listdir(fpath)
    for fn in list_dir:
        fname = os.path.join(fpath, fn)

        if fname.lower().endswith('.mp3'):
            count += 1
            try:
                print(fname)
                tags = ID3(fname)
                cool = tags.getall('USLT')
                cool = len(str(cool))
                if cool > 50:
                    failed += 1
                    print('--------------------- Lyrics PRESENT failed =' + str(failed) + ' --------------------')
                    continue

                title = str(tags['TIT2'])
                artist = str(tags['TPE1'])
                print(title, artist)
                # print(artist)
                url = google_search(title, artist)
                # print(url)
                if "http://www.azlyrics.com" not in url:
                    print('----------------------------- Lyrics NOT FOUND failed =' + str(
                        failed) + ' ----------------------')
                    failed += 1
                    continue
                lyrics, run_once = parse(url, headers)

                if run_once == 1:
                    fail, embed = Embed( fpath, fn, failed, embedded, lyrics, tags)

                    failed += fail
                    embedded += embed

            except (KeyError, UnicodeEncodeError, ConnectionError, ID3NoHeaderError, UnicodeEncodeError, IndexError,
                    TimeoutError, requests.exceptions.ConnectionError,
                    requests.packages.urllib3.exceptions.MaxRetryError) as e:
                failed += 1
                print(str(e))
                print('----------------------------- Error occured FAILED=' + str(failed) + ' ----------------------')

    print('failed objects: '+str(failed))
    #print(failed)
    print('Successful: '+str(embedded))
    #print(embedded)
    print('total number of files: '+str(count))


if __name__ == "__main__":
    main()
