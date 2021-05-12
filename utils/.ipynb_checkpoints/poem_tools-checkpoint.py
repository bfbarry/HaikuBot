#from https://datascience.stackexchange.com/questions/23376/how-to-get-the-number-of-syllables-in-a-word

from nltk.corpus import cmudict
d = cmudict.dict()

def syllables(word):
    #referred from stackoverflow.com/questions/14541303/count-the-number-of-syllables-in-a-word
    count = 0
    vowels = 'aeiouy'
    word = word.lower()
    if word[0] in vowels:
        count +=1
    for index in range(1,len(word)):
        if word[index] in vowels and word[index-1] not in vowels:
            count +=1
        elif word[index] in 'iy' and word[index-1] in vowels and word[index+1] in vowels:
            count +=1 # added this to fix 'Brian' or 'Broyo'
    if word.endswith('e'):
        count -= 1
    if word.endswith('le'):
        count += 1
    if count == 0:
        count += 1
    return count

def nsyl(word):
    try:
        return [len(list(y for y in x if y[-1].isdigit())) for x in d[word.lower()]][0]
    except KeyError:
        print('not in dict')
        #if word not found in cmudict
        return syllables(word)