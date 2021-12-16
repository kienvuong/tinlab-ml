import muser as ms
import shutil
from util.utils import Utils
import sys
import os.path
from os import path
import pickle
from shutil import copyfile
import configparser
import random
from itertools import islice

muser = ms.Muser()
#CONSTANTS
MAX_QUARTERS = 32
MAX_PREV_QUARTER = 3
TOP_QUARTERS = 5
QUARTERS_PER_SONG = 8
MAX_SONGS_PER_GEN = 10
CURRENT_GENERATION = 0

#CHANCES percentages
MUTATION_CHANCE = 5
PREV_GEN_CHANCE = 15
POPULAR_POS_CHANCE = 80

#check whether gen 0 is existing
def init():
    config = configparser.ConfigParser()
    config.read('config.ini')
    gen = config['DEFAULT'].getint('generation')
    if (gen == None):
        config['DEFAULT'] = {'generation': 0}
        with open('config.ini', 'w') as configfile:
            config.write(configfile)
        os.mkdir('generation_0')
        generateGeneration(0)
        sys.exit()
    return gen

#generate generation 0 with random tones
def generateGeneration(generation=CURRENT_GENERATION):
    weightsConfig = configparser.ConfigParser()
    weights = {}
    if (not (path.exists('generation_' + str(generation)))):
        os.mkdir('generation_' + str(generation))
    for quarterCount in range(0, MAX_QUARTERS):
        quarter = Utils.generateQuarter(1)
        fileName = 'generation_' + str(generation) + '/quarter_' + str(quarterCount)
        muser.generate(quarter, fileName)
        with open(fileName + '.pkl', 'wb') as f:
            pickle.dump(quarter, f)
    for songCount in range(0, 10):
        generateRandomSong(songCount)
        weights['song_' + str(songCount)] = 0
    weightsConfig['WEIGHTS'] = weights
    with open('generation_' + str(generation) + '/config.ini', 'w') as configfile:
        weightsConfig.write(configfile)

#get all quarters from a generation
def getQuarters(generation=CURRENT_GENERATION):
    quarters = []
    for quarterCount in range(0, MAX_QUARTERS):
        fileName = 'generation_' + str(generation) + '/quarter_' + str(quarterCount)
        with open(fileName + '.pkl', 'rb') as f:
            loadedQuarter = pickle.load(f)
            quarters.append({str(quarterCount): loadedQuarter})
            quarterCount += 1
    return quarters


def take(n, iterable):
    "Return first n items of the iterable as a list"
    return list(islice(iterable, n))

#get randomly 1 of the top 5 quarters in a previous generation
def getRandomPopularQuarter(generation):
    with open('generation_' + str(generation) + '/quarter_weights.pkl', 'rb') as f:
        loadedQuarter = pickle.load(f)

    popularQuarters = take(TOP_QUARTERS, loadedQuarter.items())
    random.shuffle(popularQuarters)

    return popularQuarters[0]

#get all rated quarters
def getPopularQuarters():
    # config = configparser.ConfigParser()
    # config.read('generation_' + str(CURRENT_GENERATION) + '/config.ini')
    # quarterWeights = config['QUARTER_WEIGHTS']
    with open('generation_' + str(CURRENT_GENERATION) + '/quarter_weights.pkl', 'rb') as f:
        loadedQuarter = pickle.load(f)

    return loadedQuarter

#get a quarter
def loadQuarter(quarterKey):
    with open('generation_' + str(CURRENT_GENERATION) + '/quarter_'+str(quarterKey) + '.pkl', 'rb') as f:
        loadedQuarter = pickle.load(f)
    return loadedQuarter

#wel of niet gebruiken van de positie
def usePopularPos(weight):
    rand = random.randint(0, 10) / 10
    chance = random.randint(0, 100)
    chance = chance < POPULAR_POS_CHANCE
    if  rand >= weight and chance:
        return False
    return True

#quarter van vorige generatie pakken of niet
def usePrevGenQuarter():
    rand = random.randint(0, 100)
    if rand >= PREV_GEN_CHANCE:
        return False
    return True

#mutate of niet
def willMutate(weight):
    rand = random.randint(0, 100) / 10
    chance = random.randint(0, 100)
    # print("Rand: " + str(rand) + " | Weight: " + str(weight) + " | Chance: " + str(chance))
    chance = chance < MUTATION_CHANCE
    if rand >= weight and chance:
        return True
    return False

#generate a random song for generation 0
def generateRandomSong(songCount):
    genQuarters = getQuarters(0)
    random.shuffle(genQuarters)
    quarters = []
    song = []
    for quarter in genQuarters[:QUARTERS_PER_SONG]:
        quarterKey = list(quarter.keys())[0]
        quarters.append(quarter[quarterKey])
        for note in quarter[quarterKey]:
            song.append(note)
    fileName = 'generation_' + str(CURRENT_GENERATION) + '/song_'+str(songCount)
    print(song)
    muser.generate(song, fileName)
    with open(fileName + '.pkl', 'wb') as f:
        pickle.dump(genQuarters[:QUARTERS_PER_SONG], f)

#check wheter a quarter is mutated or not
def isMutated(quarterKey):
    config = configparser.ConfigParser()
    config.read('generation_'+str(CURRENT_GENERATION+1)+'/config.ini')
    mutations = config['MUTATIONS']
    for mutation in  mutations:
        if quarterKey == mutations[mutation]:
            return True
    return False

#generate song based on chances
def generateSong(songCount):
    print("Generating song ("+str(songCount)+") for generation "+str(CURRENT_GENERATION+1)+"...")

    popularQuarters = getPopularQuarters()
    genQuarters = getQuarters(CURRENT_GENERATION+1)
    random.shuffle(genQuarters)
    song = []
    posWritten = []
    debugQuartersWritten = []

    #override with popular quarters from previous gen
    for popularQuarter in popularQuarters:
        for popularPos in popularQuarters[popularQuarter]['pos']:
            popularPosWeight = popularQuarters[popularQuarter]['pos'][popularPos]
            if not isMutated(popularQuarter) and not popularPos in posWritten and usePopularPos(popularPosWeight):
                print("POS "+str(popularPos)+": Using popular quarter ("+str(popularQuarter)+") and its top position ("+str(popularPos)+") from previous gen ("+str(CURRENT_GENERATION)+")")
                genQuarters[popularPos] = {str(popularQuarter): loadQuarter(popularQuarter)}
                posWritten.append(popularPos)
                debugQuartersWritten.append({str(popularQuarter): loadQuarter(popularQuarter)})
                break

    #Loop through each quarter in song and maybe change the quarter with a top quarter from a random previous generation
    #Also print if its using a mutated quarter
    for pos in range(0, QUARTERS_PER_SONG):
        if not CURRENT_GENERATION <= 0:
            prevGen = -1
            while prevGen < 0:
                prevGen = random.randint(CURRENT_GENERATION-MAX_PREV_QUARTER, CURRENT_GENERATION)
            topQuarter = getRandomPopularQuarter(prevGen)
            # if not isMutated(topQuarter[0]) and not pos in posWritten and usePrevGenQuarter():
            if not isMutated(topQuarter[0]) and usePrevGenQuarter():
                print("POS "+ str(pos) + ": Using random top quarter ("+str(topQuarter[0])+") from random previous generation ("+str(prevGen)+")")
                genQuarters[pos] = {str(topQuarter[0]): loadQuarter (topQuarter[0])}
                posWritten.append(pos)
        posQuarter = list(genQuarters[pos].keys())[0]
        if isMutated(posQuarter):
            print("POS "+ str(pos) + ": Using a new mutated quarter ("+str(posQuarter)+")")

    #Generate song and quartert list for pkl
    for quarter in genQuarters[:QUARTERS_PER_SONG]:
        quarterKey = list(quarter.keys())[0]

        for note in quarter[quarterKey]:
            song.append(note)

    fileName = 'generation_' + str(CURRENT_GENERATION+1) + '/song_'+str(songCount)
    muser.generate(song, fileName)
    with open(fileName + '.pkl', 'wb') as f:
        pickle.dump(genQuarters[:QUARTERS_PER_SONG], f)

def rateQuarters():
    config = configparser.ConfigParser()
    config.read('generation_'+str(CURRENT_GENERATION)+'/config.ini')
    # if 'quarter_weights.pkl' does not exist:
    if not(path.exists('generation_' + str(CURRENT_GENERATION) + '/quarter_weights.pkl')):
        print("Rating quarters in generation " + str(CURRENT_GENERATION)  + "...")
        weights = config['WEIGHTS']
        popularQuarters = {}
        for songCount in range(0, MAX_SONGS_PER_GEN):
            fileName = 'generation_' + str(CURRENT_GENERATION) + '/song_' + str(songCount)
            with open(fileName + '.pkl', 'rb') as f:
                loadedSong = pickle.load(f)
                # print('Weight: ' + weights['song_'+str(songCount)])
                # print(loadedSong)
                quarterPos = 0
                for quarter in loadedSong:
                    quarterKey = list(quarter.keys())[0]
                    # print(str(quarterKey) + " | " + str(quarterPos))
                    quarterWeight = (int(weights['song_'+str(songCount)]) / 10)
                    if str(quarterKey) in popularQuarters:
                        popularQuarters[str(quarterKey)]['weight'] += quarterWeight
                        if str(quarterPos) in popularQuarters[str(quarterKey)]['pos']:
                            popularQuarters[str(quarterKey)]['pos'][quarterPos] += quarterWeight
                        else:
                            popularQuarters[str(quarterKey)]['pos'][quarterPos] = quarterWeight
                    else:
                        popularQuarters[str(quarterKey)] = {"weight": quarterWeight, "pos": {quarterPos: quarterWeight}}
                    sortedPos = dict(sorted(popularQuarters[str(quarterKey)]['pos'].items(), key=lambda item: item[1], reverse=True))
                    popularQuarters[str(quarterKey)]['pos'] = sortedPos
                    quarterPos += 1
        for quarterKey in range(0, MAX_QUARTERS):
            if not (str(quarterKey) in popularQuarters):
                popularQuarters[str(quarterKey)] = {'weight': 0, 'pos': {}}
        sortedpopularQuarters = dict(sorted(popularQuarters.items(), key=lambda item: item[1]['weight'], reverse=True))
        config['QUARTER_WEIGHTS'] = sortedpopularQuarters
        with open('generation_' + str(CURRENT_GENERATION) + '/config.ini', 'w') as configfile:
            config.write(configfile)
        with open('generation_' + str(CURRENT_GENERATION) + '/quarter_weights.pkl', 'wb') as f:
            pickle.dump(sortedpopularQuarters, f)

def updateGeneration():
    config = configparser.ConfigParser()
    config.read('config.ini')
    config['DEFAULT'] = {'generation': (CURRENT_GENERATION)}
    with open('config.ini', 'w') as configfile:
        config.write(configfile)

def mutateQuarter(quarterKey, generation):
    print("Mutating quarter ("+str(quarterKey)+") for generation " + str(generation))
    quarter = Utils.generateQuarter(1)
    fileName = 'generation_' + str(generation) + '/quarter_' + str(quarterKey)
    muser.generate(quarter, fileName)
    with open(fileName + '.pkl', 'wb') as f:
        pickle.dump(quarter, f)

def mutateGen():
    config = configparser.ConfigParser()
    config.read('generation_'+str(CURRENT_GENERATION+1)+'/config.ini')
    quarterWeights = getPopularQuarters()
    mc = 0
    mutatedQuarters = {}
    for quarterKey in range(0, MAX_QUARTERS):
        if willMutate(quarterWeights[str(quarterKey)]['weight']):
            mutateQuarter(quarterKey, CURRENT_GENERATION+1)
            mutatedQuarters[mc] = quarterKey
            mc += 1
    config['MUTATIONS'] = mutatedQuarters
    with open('generation_' + str(CURRENT_GENERATION+1) + '/config.ini', 'w') as configfile:
        config.write(configfile)
    print("Total mutations: " + str(mc) + "/" + str(MAX_QUARTERS) + " for generation " + str(CURRENT_GENERATION+1))

#Check for generation and set generation zero when non-existent
CURRENT_GENERATION = init()
print("Current generation: " + str(CURRENT_GENERATION))
#Rate previous quarters based on song ratings
rateQuarters()
print("Preparing generation " + str(CURRENT_GENERATION + 1) + "...")
#Copy previous generation
if not(path.exists("generation_"+str(CURRENT_GENERATION+1))):
    shutil.copytree("generation_"+str(CURRENT_GENERATION), "generation_"+str(CURRENT_GENERATION+1))
    os.remove('generation_'+str(CURRENT_GENERATION+1)+'/config.ini')
    os.remove('generation_'+str(CURRENT_GENERATION+1)+'/quarter_weights.pkl')
    config = configparser.ConfigParser()
    config.read('generation_'+str(CURRENT_GENERATION+1)+'/config.ini')
    weights = {}
    for songcount in range(0, 10):
        weights['song_' + str(songcount)] = 0
    config['WEIGHTS'] = weights
    with open('generation_' + str(CURRENT_GENERATION+1) + '/config.ini', 'w') as configfile:
        config.write(configfile)

mutateGen()

for songCount in range(0, MAX_SONGS_PER_GEN):
    generateSong(songCount)
#Update generation
CURRENT_GENERATION += 1
updateGeneration()


#
# if not(CURRENT_GENERATION == None):
#     #Copy generation
#     if not(path.exists("generation_"+str(CURRENT_GENERATION+1))):
#         shutil.copytree("generation_"+str(CURRENT_GENERATION), "generation_"+str(CURRENT_GENERATION+1))
#     CURRENT_GENERATION += 1
#     #-----------------------------------------------------
#     # songNr = 0
#     for songNr in range(0, 15):
#         combinedQuarters = []
#         songPath = "generation_"+str(CURRENT_GENERATION)+"/song_"+str(songNr)
#         weights = configparser.ConfigParser()
#         weights.read(songPath + "/weights.ini")
#         weights = weights['WEIGHTS']
#         for quarter in range(0, 16):
#             with open('generation_'+str(CURRENT_GENERATION)+'/song_' + str(songNr) + '/quarter_' + str(quarter) + '.pkl', 'rb') as f:
#                 loadedQuarter = pickle.load(f)
#                 print(loadedQuarter)
#             if(mutate(int(weights['quarter_'+str(quarter)]))):
#                 print("Mutating quarter: " + str(quarter))
#                 newQuarter = Utils.generateQuarter(1)
#                 loadedQuarter = newQuarter
#                 fileName = 'generation_' + str(CURRENT_GENERATION) + '/song_' + str(songNr) + '/quarter_' + str(quarter)
#                 with open(fileName+'.pkl', 'wb') as f:
#                     pickle.dump(newQuarter, f)
#                 muser.generate(newQuarter, fileName)
#                 print(newQuarter)
#             for note in loadedQuarter:
#                 combinedQuarters.append(note)
#         # Combine quarters in new song
#         print(combinedQuarters)
#         muser.generate(combinedQuarters, 'generation_' + str(CURRENT_GENERATION) + '/song_' + str(songNr) + '/song')
#     #------------------------
#     #Update generation
#     config = configparser.ConfigParser()
#     config.read('config.ini')
#     config['DEFAULT'] = {'generation': CURRENT_GENERATION}
#     with open('config.ini', 'w') as configfile:
#         config.write(configfile)


# --------------------------------------------------------
# with open('generation_1/song_0/quarter_0.pkl', 'rb') as f:
#     x = pickle.load(f)
# print(x)
# i = 0
# while i < 20:
#
#     i += 1
