
import csv
from copy import deepcopy
import copy
import os
import Tkinter as tk
import tkFileDialog
from Tkinter import *
import tkMessageBox

class Naive_Bayes_Classifier:
    def __init__(self):
        self.title = "Naive Bayes Classifier"
        self.root = tk.Tk()
        self.root.title(self.title)
        w = 280  # width for the Tk root
        h = 200  # height for the Tk root

        # get screen width and height
        ws = self.root.winfo_screenwidth()  # width of the screen
        hs = self.root.winfo_screenheight()  # height of the screen

        # calculate x and y coordinates for the Tk root window
        x = (ws / 2) - (w / 2)
        y = (hs / 2) - (h / 2)

        # set the dimensions of the screen
        # and where it is placed
        self.root.geometry('%dx%d+%d+%d' % (w, h, x, y))
        self.frame = Frame(self.root)
        self.frame.grid()
        self.path = None
        self.flag = True
        self.numOfBins = None
        self.e1 = Entry(self.root)
        self.build = {}
        self.testList = []
        self.data_train = None
        self.data_test = None
        self.classes_list = None
        self.repeat_dict = None
        self.structure_dict = None
        self.min_max_range_dict = None

    def start(self):
        text = tk.Label(self.root, text="Click 'Browse' and choose Directory Path")
        text.grid(row=0, column=1)
        browseButton = Button(command=self.Path, text="Browse", fg="black")
        browseButton.grid(row = 1, column=1)
        text2 = tk.Label(self.root, text="Discretization Bins:")
        text2.grid(row=2, column=1)
        self.e1.grid(row=3, column=1)
        buildButton = Button(command=self.Build, text="Build", fg="black")
        buildButton.grid(row=4, column=1)
        classifyButton = Button(command=self.Classify, text="Classify", fg="black")
        classifyButton.grid(row=5, column=1)
        self.root.mainloop()

    def Classify(self):
        if self.flag:
            tkMessageBox.showinfo("Error", "build before classify!")
            return

        filename = str(self.path) + "/test.csv"
        # filename = "test.csv"

        try:
            self.data_test = loadCsv(filename)
        except Exception as e:
            tkMessageBox.showerror("Error", e)

            return


        success = naive_baYes(self.data_train,self.data_test,self.classes_list,self.repeat_dict,self.numOfBins,self.structure_dict,self.min_max_range_dict)
        tkMessageBox.showinfo(self.title, "classify is finished!" + "\n" + "Naive Base success rate: " + " %.2f " % success + "%")
        #print("Naive Base success rate: " + " %.2f " % success + "%")
        self.root.destroy()

        pass

    def Build(self):
        filename = str(self.path) + "/Structure.txt"
        try:
            structure_dict2 = (structure_dict(filename))
        except Exception as e:
            tkMessageBox.showerror("Error", e)
            return
        self.structure_dict = structure_dict2.d
        filename = str(self.path) + "/train.csv"
        # filename = "train.csv"
        try:
            data_train = data_dict(filename)
        except Exception as e:
            tkMessageBox.showerror("Error",e)
            return
        self.data_train = data_train.data
        self.numOfBins = self.e1.get()
        try:
            self.numOfBins = int(self.numOfBins)
            if self.numOfBins <= 0:
                raise Exception()
        except:
            tkMessageBox.showerror("Error", "Illegal number of bins")
            return

        self.min_max_range_dict = {}

        self.repeat_dict = create_empty_repeat_dict(self.structure_dict)
        create_repeat_dict(self.repeat_dict, self.data_train, self.structure_dict)  # repeat dict

        normalize_data(self.repeat_dict, self.data_train, self.structure_dict)
        self.repeat_dict = create_empty_repeat_dict(self.structure_dict)
        create_repeat_dict(self.repeat_dict, self.data_train, self.structure_dict)  # repeat dict after normalize

        bin_dict = sep_bins(self.structure_dict, self.repeat_dict, self.data_train, self.numOfBins, self.min_max_range_dict)
        self.classes_list = classification_list_init(bin_dict, self.data_train, self.structure_dict)

        self.flag = False
        tkMessageBox.showinfo(self.title, "Building classifier using train-set is done!")
        pass

    def Path(self):
        file_path = tkFileDialog.askdirectory()
        self.path = file_path
        pass



def loadCsv(filename):
    if(os.stat(filename).st_size == 0):
        raise Exception("Error , file name: " + filename + " is empty.")
    try:
        lines = csv.reader(open(filename, "r"))
        data = list(list(lines))
        for i in range(len(data)):
            data[i] = [(x) for x in data[i]]
    except Exception as e:
        raise Exception("Error file name: " + filename +" does not exist.")

    return data


def loadStructure(filename):
    d={}
    try:
        with open(filename) as f:
            for line in f:
                line = line.strip()
                lines = line.split(" ")
                attr = lines[2].split(",")
                for i in range(len(attr)):
                    attr[i] = str(attr[i].replace('{', '').replace('}', ''))
                d[lines[1]] = attr

    except Exception as e:
        raise Exception("Error file name: " + filename + " does not exist.")
    f.close()
    return d


class structure_dict(object):
    d = {}


    def __init__(self,fileName):
        self.d = loadStructure(fileName)
    def __str__(self):
        return ("{0}".format(self.d))


class data_dict(object):
    data=[[]]
    def __init__(self,fileName):
        #print("------data start-----")
        self.data=loadCsv(fileName)


        #print ("------data end------")
    def __str__(self):
        return ("{0}".format("No accsess"))

def create_empty_repeat_dict(dict):
    utilityDict = {}
    for keyword in dict:
        utilityDict[keyword] = []
        for i in range(len(dict[keyword])):
            if (dict[keyword][0] == "NUMERIC"):
                utilityDict[keyword].append(0)
            utilityDict[keyword].append(0)
    return utilityDict


def create_repeat_dict(utilityDict,data,attr_dict):
    lines_number = len(data)
    col_number = len(data[0])
    for i in range(col_number):
        flag = 0
        for j in range(lines_number):
            if data[j][i].isdigit():  # if numeric
                if (float(data[j][i]) >= 0):
                    flag += 1
                    utilityDict[data[0][i]][0] = utilityDict[data[0][i]][0] + 1  # enter counter
                    utilityDict[data[0][i]][1] = utilityDict[data[0][i]][1] + float(data[j][i])  # enter sum
            else:
                attribute_name = data[0][i]
                if data[j][i] in attr_dict[attribute_name]:
                    index = attr_dict[attribute_name].index(data[j][i])
                    utilityDict[attribute_name][index] = utilityDict[attribute_name][index] + 1


def normalize_data(repeat_dict,data,attr_dict):
    lines_number = len(data)
    col_number = len(data[0])
    flag=0
    for i in range(col_number):
        keyword = data[0][i]
        counter=0
        for j in range(lines_number):
            if (j==0):
                j=1
            if(attr_dict[keyword].count("NUMERIC") == 1):
                if data[j][i].isdigit():  # if numeric
                    if (float(data[j][i]) < 0):
                        counter+=1

                        data[j][i] = (str)(int(repeat_dict[keyword][1] / repeat_dict[keyword][0]))


                else:
                    data[j][i] = (str)(int(repeat_dict[keyword][1] / repeat_dict[keyword][0]))
                    counter += 1



            else: ## attr_dict[keyword]!= "NUMERIC"
                if data[j][i] == '':
                    data[j][i] = "null"
                flag=0
                for word in attr_dict[keyword]:
                    if(data[j][i] == word):
                        flag=flag+1
                if(flag == 0):
                    maxlist = max(repeat_dict[keyword])
                    index = repeat_dict[keyword].index(maxlist)
                    data[j][i] = attr_dict[keyword][index]


def sep_bins(attr_dict,repeat_dict,data,numOfBins,minMaxRangeDict):
    maximum=0
    minimum=100000000
    d = repeat_dict
    lines_number = len(data)
    col_number = len(data[0])

    for i in range(col_number):
        keyword = data[0][i]
        if (attr_dict[keyword].count("NUMERIC") == 1):
            keyword2 = data[0][i]
            maximum=0
            minimum=100000
            if (attr_dict[keyword2].count("NUMERIC") == 1):
                for t in range(lines_number):

                    if (t != 0):
                        if (float(data[t][i]) > maximum):


                            maximum = float(data[t][i])
                        if (float(data[t][i]) < minimum):
                            minimum = float(data[t][i])


                temp_range = (maximum - minimum) / numOfBins
                minMaxRangeDict[keyword]=[maximum,minimum,temp_range]
                for j in range(lines_number):
                    if (j != 0):
                        if(float(data[j][i])==maximum):
                            data[j][i] = str(numOfBins)
                        else:
                            data[j][i]=str(int((float(data[j][i])-minimum)/temp_range)+1)


    for i in range(col_number):
        keyword = data[0][i]
        if (attr_dict[keyword].count("NUMERIC") == 1):
            l = []
            for x in range(numOfBins + 1):
                l.append(0)
            l[0] = (repeat_dict[keyword][0])
            d[keyword] = l
            for j in range(lines_number):
                if(j != 0):
                    index = int(float(data[j][i]))
                    #print ("index: ",index)
                    d[keyword][index]=d[keyword][index] + 1


    #print("---------Z-------")
    #print(d)
    #print("----------Z------")
    return d

def clean_dict(dict):
    d={}
    for keyword in dict:
        d[keyword] = []
        for i in range(len(dict[keyword])):
            d[keyword].append(0)
    return d




def enter_class_repeats_to_dict(class_dict, data, attr_dict,class_type):
    d=class_dict
    lines_number = len(data)
    col_number = len(data[0])
    count = 0
    for i in range(col_number):
        flag = 0
        attribute_name = data[0][i]
        for j in range(lines_number):
            if (data[j][15] == class_type):
                if data[j][i].isdigit():  # if numeric

                    bin_index = int(float(data[j][i]))
                    d[data[0][i]][bin_index] = d[data[0][i]][bin_index] + 1  # enter to bins
                    d[data[0][i]][0] = d[data[0][i]][0] + 1  # counter


                else:
                    attribute_name = data[0][i]
                    if data[j][i] in attr_dict[attribute_name]:
                        index = attr_dict[attribute_name].index(data[j][i])
                        d[attribute_name][index] = d[attribute_name][index] + 1
        laplaceCorrection(attribute_name, d)
    return d


def laplaceCorrection(attribute_name, d):
    for k in range(len(d[attribute_name])):  # laplaceCorrection
        if d[attribute_name][k] == 0:
            for p in range(len(d[attribute_name])):
                d[attribute_name][p] = d[attribute_name][p] + 1




def naive_baYes(data_train,data_test,classes_list,repeat_dict,numOfBins,structure_dict,minMaxRangeDict):
    fh = open("output.txt","w")

    lines_number = len(data_test)
    col_number = len(data_test[0])

    count_yes = 0

    probability_by_class_list = []

    for x in range(len(structure_dict["class"])):
        probability_by_class_list.append([1,structure_dict["class"][x]])

    for i in range(lines_number):
        for j in range(col_number):
            attribute_name = data_test[0][j]
            if(i!=0 and j!=15 ):
                if data_test[i][j].isdigit():  # if numeric
                        maximum=minMaxRangeDict[attribute_name][0]
                        minimum=minMaxRangeDict[attribute_name][1]
                        temp_range=minMaxRangeDict[attribute_name][2]

                        index_bin = float(float(float(data_test[i][j]) - minimum) / temp_range)+1

                        if(index_bin>numOfBins):
                            index_bin=numOfBins
                        elif index_bin < 1:
                            index_bin =1

                        if(index_bin>numOfBins or index_bin<1):
                            print("bin out of range")
                        else:
                            list_index = 0
                            index_bin = int(index_bin)
                            for x in classes_list:
                                probability_by_class_list[list_index][0] *= float(
                                    float(x[attribute_name][index_bin]) / float(repeat_dict["class"][list_index])) #first calc if numeric
                                list_index += 1
                else:
                    list_index = 0
                    index=0
                    for x in classes_list:
                        if data_test[i][j] in structure_dict[attribute_name]:
                            index = structure_dict[attribute_name].index(data_test[i][j])
                            probability_by_class_list[list_index][0] *= float((float(x[attribute_name][index]) / float(repeat_dict["class"][list_index])))   #first calc (not numeric)
                            list_index += 1

            maximum = 0
            maximum_index = 0

            if (data_test[0][j]=="class" and i!=0):
                for index in range(len(probability_by_class_list)):

                    base=float(repeat_dict[attribute_name][index]) / len(data_train)
                    if(probability_by_class_list[index][0] >= 1):
                        probability_by_class_list[index][0]=0
                    probability_by_class_list[index][0]=float(probability_by_class_list[index][0])*base   # second calc
                    if (probability_by_class_list[index][0] > maximum):
                        maximum = float(probability_by_class_list[index][0])
                        maximum_index = index
                print>> fh, i , probability_by_class_list[maximum_index][1]

                if (i != 0):

                    if (probability_by_class_list[maximum_index][1] == data_test[i][15]):
                        count_yes += 1
                for index in range(len(probability_by_class_list)):
                    probability_by_class_list[index][0] = 1

    success = float(count_yes)/lines_number * 100
    #print("Naive Base success rate: "+" %.2f " %success +"%")

    fh.close()
    return success


def main():
    program = Naive_Bayes_Classifier()
    program.start()




def classification_list_init(bin_dict, data, structure_dict2):
    classes_list = []
    for i in range(len(structure_dict2["class"])):
        classes_list.append(clean_dict(bin_dict))
        classes_list[i] = enter_class_repeats_to_dict(classes_list[i], data, structure_dict2,
                                                      structure_dict2["class"][i])
    return classes_list


main()
