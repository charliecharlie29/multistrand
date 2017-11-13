# Frits Dannenberg, May 17th, 2017.
# This is used for the slowdown study 
# and the comparison between first step and trajectory mode

""" 
# Run this using arguments 
# plots 160
# or
# slowDownStudy 82000
"""

from multistrand.objects import Strand
from multistrand.experiment import standardOptions, hybridization
from multistrand.utils import concentration_string, standardFileName
from multistrand.concurrent import  FirstStepRate, FirstPassageRate, Bootstrap, myMultistrand
from multistrand.options import Options



from constantsgao import goa2006_P0, goa2006_P3, goa2006_P4, setSaltGao2006, colors

import nupack

import matplotlib.pylab as plt
import numpy as np
import time, sys

SCRIPT_DIR = "Hybridization_F1"
TEMPERATURE = 20.0
ATIME_OUT = 100.0
 
markers = ["8", ">", "D", "s", "*", "<", "^"] 
 
myMultistrand.setNumOfThreads(8) 




def first_step_simulation(strand_seq, trials, T=20.0, leak=False):

    print ("Running first step mode simulations for %s (with Boltzmann sampling)..." % (strand_seq))
       
    def getOptions(trials):
       
       
        o = standardOptions(Options.firstStep, TEMPERATURE, trials, ATIME_OUT) 
        hybridization(o, strand_seq, trials)
        setSaltGao2006(o)
        
        o.JSMetropolis25()
               
        
        return o
    
    myMultistrand.setOptionsFactory1(getOptions, trials)
    myMultistrand.setFirstStepMode() # ensure the right results object is set.
    if leak:
        myMultistrand.setLeakMode()
    myMultistrand.run()
    return myMultistrand.results



def first_passage_association(strand_seq, trials, concentration, T=20.0):

    print "Running first passage time simulations for association of %s at %s..." % (strand_seq, concentration_string(concentration))
    
    def getOptions(trials):

           
        o = standardOptions(Options.firstPassageTime, TEMPERATURE, trials, ATIME_OUT) 
        
        hybridization(o, strand_seq, trials, True)
        setSaltGao2006(o)
        o.join_concentration = concentration

        return o
    
    myMultistrand.setOptionsFactory1(getOptions, trials)
    myMultistrand.setPassageMode()
    myMultistrand.run()
    
    return myMultistrand.results



#


def doFirstStepMode(seq, concentrations, T=20.0, numOfRuns=500, leak=False):
    
    # track time for each kind of simulation, using time.time(), which has units of second
    # do one "first step mode" run, get k1, k2, etc, from which z_crit and k_eff(z) can be computed

    myRates = first_step_simulation(seq, numOfRuns, T=T, leak=leak) 
    time2 = time.time()
    print str(myRates)
    
    
    FSResult = list()
    
    for z in concentrations:
        
        if leak:
            kEff = myRates.k1()
        else:
            kEff = myRates.kEff(z)
            
        myBootstrap = Bootstrap(myRates, N=1000, concentration=z, computek1=leak)
        
        low, high = myBootstrap.ninetyFivePercentiles()
        logStd = myBootstrap.logStd()
        
        print "keff = %g /M/s at %s" % (kEff, concentration_string(z))
        
        myResult = (np.log10(kEff), np.log10(low), np.log10(high), logStd)
        FSResult.append(myResult)
        
    print
    
    # call NUPACK for pfunc dG of the reaction, calculate krev based on keff
    print "Calculating dissociate rate constant based on NUPACK partition function energies and first step mode k_eff..."

    dG_top = nupack.pfunc([seq], T=T)
    dG_bot = nupack.pfunc([ Strand(sequence=seq).C.sequence ], T=T)
    dG_duplex = nupack.pfunc([ seq, Strand(sequence=seq).C.sequence ], T=T)
    RT = 1.987e-3 * (273.15 + T)
    time3 = time.time()
    time_nupack = time3 - time2
    krev_nupack = kEff * np.exp((dG_duplex - dG_top - dG_bot) / RT)
    print "krev = %g /s (%g seconds)" % (krev_nupack, time_nupack)
    
    
    times = list()
    for i in concentrations:
        myTime = (np.log10(myMultistrand.runTime), 0.0, 0.0)
        times.append(myTime)
    
    return FSResult, times
   

   
def doFirstPassageTimeAssocation(seq, concentrations, T=20, numOfRuns=500):  

    # for each concentration z, do one "first passage time" run for association, and get k_eff(z)
    Result = []
    times = list()
    
    
    for concentration in concentrations:
        
        myRates = first_passage_association(seq, numOfRuns, concentration=concentration, T=T)
        keff = myRates.log10KEff(concentration)
        
        myBootstrap = Bootstrap(myRates, concentration=concentration)
        low, high = myBootstrap.ninetyFivePercentiles()
        logStd = myBootstrap.logStd()
        

        Result.append((keff, np.log10(low), np.log10(high), logStd))
        times.append((np.log10(myMultistrand.runTime), 0.0, 0.0))
        
        
        print "keff = %g /M/s at %s" % (keff, concentration_string(concentration))
    
    
    print 
    
    return Result, times


def fluffyPlot(ax, seqs, concentrations):
    
    
    myXTicks = list()
    for conc in concentrations:
        myXTicks.append(concentration_string(conc))
    
    
    plt.xticks(rotation=-40) 
    plt.xticks(np.log10(concentrations), myXTicks)
    
    plt.gca().invert_xaxis()
    ax.set_xlabel('Concentration')
    
    # Shrink current axis by 20%
    box = ax.get_position()
    ax.set_position([box.x0, box.y0 + box.height * 0.2, box.width * 0.8, 0.8 * box.height])
    

    ax.legend(seqs, loc='center left', bbox_to_anchor=(1, 0.5))
    
    


def addPoints(results, i, alp, seqs, concentrations, lineStyle, extraOptions=None):
    
#     print results
    xVal = np.log10(concentrations)
    yVal = [r[0] for r in results[i]]
    
    
    plt.scatter(x=xVal, y=yVal, color=colors[i], marker=markers[i], alpha=alp, s=50.0, label=str(seqs[i]))
    plt.plot(xVal, yVal, marker=markers[i], linestyle=lineStyle, color=colors[i], alpha=alp , label=str(seqs[i]))
    
    if not extraOptions == "noErrorBars" :

        yLow = np.array([ (r[1])  for r in results[i]])
        yHigh = np.array([ (r[2]) for r in results[i]])
                
        plt.errorbar(xVal, yVal, yerr=[yLow - yVal, yLow - yVal], linestyle="None", color=colors[i], alpha=alp , label=str(seqs[i]))
#     

def doPlots(seqs, concentrations, results1, results2, trials):
       
    ax = plt.subplot(111)       

    length = len(seqs)
    
    for i in range(length):
        
        addPoints(results2, i, 0.85, seqs, concentrations, '-')

    fluffyPlot(ax, seqs, concentrations)
    
    for i in range(length):
     

        addPoints(results1, i, 0.45, ["", "", "", "", "", "", "", ""], concentrations, '--')
    
    ax.set_title("Estimated hybridization rate (" + str(trials) + " trajectories)")
    ax.set_ylabel("k-effective (per second, log 10)")    
    
    plt.gca().invert_xaxis()
    
    plt.savefig(standardFileName(SCRIPT_DIR) + 'scatter1.pdf')
    plt.close()
    
    
def doTimePlots(seqs, concentrations, results1, results2, trials):
                   
    ax = plt.subplot(111)
                       
    ax.set_title("Computation time for " + str(trials) + " trajectories")
    ax.set_ylabel("Time (seconds, log 10)")    
        
    length = len(seqs)
    
    for i in range(length):
        addPoints(results2, i, 0.85, seqs, concentrations, '-', extraOptions="noErrorBars")


    fluffyPlot(ax, seqs, concentrations)
    
    
    for i in range(length):
        addPoints(results1, i, 0.45, seqs, concentrations, '--', extraOptions="noErrorBars")
    
    
    plt.gca().invert_xaxis()
    
    plt.savefig(standardFileName(SCRIPT_DIR) + 'runTime1.pdf')



def basicResults(results1, results2, runTime1, runTime2, seq, concentrations, trials):
              
    FSResult, times = doFirstStepMode(seq, concentrations, numOfRuns=trials)
    results1.append(FSResult)
    runTime1.append(times)


    FPResult, times = doFirstPassageTimeAssocation(seq, concentrations, numOfRuns=trials)
    results2.append(FPResult)
    runTime2.append(times)    
    
    


def doInference(concentrations, trials):

    
    results1 = list()
    results2 = list()
    
    runTime1 = list()
    runTime2 = list()
       
    
    seqs = list()
    seqs.append('TCGATG')
    seqs.append('TCGATGC')
    seqs.append('AGTCCTTTTTGG')
    

    for seq in seqs:
        basicResults(results1, results2, runTime1, runTime2, seq, concentrations, trials)
         
    # results1, resutls2 are identical but first passage time and first step    

    doPlots(seqs, concentrations, results1, results2, trials)   
    doTimePlots(seqs, concentrations, runTime1, runTime2, trials)
   

def doSlowdownStudy(trials):
            
    
    def computeMeanStd(seq):
    
        
        result, times = doFirstStepMode(seq, [1.0e-6], T=20, numOfRuns=trials, leak=True) 
        
        return result[0]
    
    
    result0 = computeMeanStd(goa2006_P0)
    result3 = computeMeanStd(goa2006_P3)
    result4 = computeMeanStd(goa2006_P4)
    
    print result0
    print result3
    print result4
   
    output = ""
   
    for result in [result0, result3, result4]:
   
        output += "mean,  is " + str(result[0]) + "  " + str(result[1]) + "  " + str(result[2]) + "  " + str(result[3]) + "\n"

    factor3 = np.power(10, result0[0] - result3[0])
    factor4 = np.power(10, result0[0] - result4[0])
    
    
    dev3 = result0[3] + result3[3]
    dev4 = result0[3] + result4[3]
    
        
    dev3 = np.power(10, result0[0] - result3[0] + dev3) - factor3
    dev4 = np.power(10, result0[0] - result4[0] + dev4) - factor4                           
    
    output += "factor3" + " " + str(factor3) + "  " + str(dev3) + " \n"
    output += "factor4" + " " + str(factor4) + "  " + str(dev4) + " \n"

    
    f = open(standardFileName(SCRIPT_DIR) + "relRates.txt", 'w')
    f.write(output)
    f.close()    



# # The actual main method

if __name__ == '__main__':

    print sys.argv

    if len(sys.argv) > 1:

        toggle = str(sys.argv[1])
        trials = int(sys.argv[2])


        if toggle == "plots":     
            doInference([1e0, 1e-1, 1e-2, 1e-3, 1e-4, 1e-5], trials)                     
        
        if toggle == "slowDownStudy":
            doSlowdownStudy(trials)
        
        
        
        

















