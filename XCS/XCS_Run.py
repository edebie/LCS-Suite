# Import Required Modules------------------------------------
import datetime
import os
import random
import time

from XCS.XCS_Algorithm import XCS
from XCS.XCS_ConfigParser import ConfigParser
from XCS.XCS_Constants import cons
from XCS.XCS_Offline_Environment import Offline_Environment
from XCS.XCS_Timer import Timer
from XCS.XCS_OutputFileManager import OutputFileManager


def mainRun():
    helpstr = """Failed attempt to run e-LCS.  Please ensure that a configuration file giving all run parameters has been specified."""
    # Specify the name and file path for the configuration file.
    config_file = "XCS_Configuration_File.txt"
    # Obtain all run parameters from the configuration file and store them in the 'Constants' module.
    ConfigParser(config_file)
    # Initialize the 'Timer' module which tracks the run time of algorithm and it's different components.
    timer = Timer()
    cons.referenceTimer(timer)
    # Set random seed if specified.-----------------------------------------------
    if cons.useSeed:
        random.seed(cons.randomSeed)
    else:
        random.seed(datetime.datetime.now().microsecond)
    # Initialize the 'Environment' module which manages the data presented to the algorithm.  While e-LCS learns iteratively (one inistance at a time
    env = Offline_Environment()
    cons.referenceEnv(
        env)  # Passes the environment to 'Constants' (cons) so that it can be easily accessed from anywhere within the code.
    # Clear Local_Output Folder before Run
    folder = 'Local_Output'
    for file in os.listdir(folder):
        file_path = os.path.join(folder, file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(e)
    # Run the e-LCS algorithm.
    kfold_accuracy = 0
    t0 = time.clock()
    if cons.kfold > 0:
        total_instances = env.format_data.numTrainphenotypes
        env.format_data.splitDataIntoKSets()
        accurate_numbs = [0.0] * cons.kfold
        for i in range(cons.kfold):
            print("")
            print("Starting next XCS learning iteration...")
            print("K-FOLD: " + str(i))
            env.format_data.selectTrainTestSets(i)
            cons.parseIterations()  # Identify the maximum number of learning iterations as well as evaluation checkpoints.
            XCS().run_XCS()
            accuracy = XCS.standard_accuracy
            accurate_numbs[i] = accuracy * env.format_data.numTestphenotypes
            kfold_accuracy = sum(accurate_numbs) / total_instances
        print("AVERAGE ACCURACY AFTER " + str(cons.kfold) + "-FOLD CROSS VALIDATION is " + str(kfold_accuracy))
    else:
        cons.parseIterations()  # Identify the maximum number of learning iterations as well as evaluation checkpoints.
        XCS().run_XCS()
    t1 = time.clock()
    total = t1 - t0
    total = round(total, 2)
    print("Total run time in seconds: %.2f" % total)
    f = open("RESULTS_FILE.txt", 'a')
    f.write(" Accuracy: " + str(kfold_accuracy) + " Total time: " + str(total) + " Rules: " + str(OutputFileManager.totalPopulationSize) + "\n")

# -----------------------------------------------------------
# Function to parse arguments--------------------------------
if __name__ == '__main__':

    for i in range(1):
        mainRun()
