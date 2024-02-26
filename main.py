class App:
    def getConstraints(self):
        self.constraints = []
        self.constraintsInfo = []
        for i in range(self.constNumber):
            self.constraints.append([])
            self.constraintsInfo.append({})
            for j in range(self.varNumber):
                self.constraints[i].append(
                    float(input("Enter X{} for constraint {}:".format(j + 1, i + 1)))
                )
            self.constraintsInfo[i]["inequality"] = int(
                input("Is it lte or gte? Type 0 for lte and type 1 for gte:")
            )

            self.constraintsInfo[i]["rhs"] = float(
                input(
                    "Plese enter the right hand side of the inequality for constraint {}:".format(
                        i + 1
                    )
                )
            )

    def getObjective(self):
        max = input("Is objective max or min:")
        if max == "max":
            self.max = 1
        elif max == "min":
            self.max = 0
        self.objective = []
        for i in range(self.varNumber):
            self.objective.append(
                float(input("Enter X{} for objective function:".format(i + 1)))
            )
        self.objective.append(
            float(input("Please enter the constant of the objective function:"))
        )

    def readFromText(self, text):
        f = open(text)
        nums = f.readline().strip().split()
        self.constNumber = int(nums[0])
        self.varNumber = int(nums[1])
        self.max = 1
        objective = f.readline().strip().split()
        self.objective = []
        self.objective2 = []
        for num in objective:
            self.objective.append(float(num))
            self.objective2.append(float(num))
        self.objective.append(0.0)
        self.constraints = []
        self.constraintsInfo = []
        lineCounter = 0
        for line in f:
            self.constraints.append([])
            self.constraintsInfo.append({})
            row = line.strip().split()
            for i in range(self.varNumber):
                self.constraints[lineCounter].append(float(row[i]))
            self.constraintsInfo[lineCounter]["inequality"] = 0
            self.constraintsInfo[lineCounter]["rhs"] = float(row[-1])
            lineCounter += 1
        f.close()

    def simplexReady(self):
        # check for negative rhs and change them
        for i in range(self.constNumber):
            if self.constraintsInfo[i]["rhs"] < 0:
                self.constraintsInfo[i]["rhs"] *= -1
                self.constraintsInfo[i]["inequality"] = (
                    1 if self.constraintsInfo[i]["inequality"] == 0 else 0
                )
                for j in range(self.varNumber):
                    self.constraints[i][j] *= -1.0

        # add slack variables
        self.slacks = []
        for i in range(self.constNumber):
            self.slacks.append([])
            self.objective.insert(len(self.objective) - 1, 0.0)
            for j in range(self.constNumber):
                self.slacks[i].append(0.0)
        for i in range(self.constNumber):
            if self.constraintsInfo[i]["inequality"] == 0:
                self.slacks[i][i] = 1.0
            elif self.constraintsInfo[i]["inequality"] == 1:
                self.slacks[i][i] = -1.0

        # create modified constraints with equalities
        for i in range(self.constNumber):
            self.constraints[i].extend(self.slacks[i])

        # choose pivots (at first they are slack variables)
        self.pivots = []
        for i in range(len(self.slacks)):
            self.pivots.append(i + self.varNumber)
        # if it is maximization turn it into minimization
        if self.max:
            for i in range(len(self.objective)):
                self.objective[i] *= -1

    def simplex(self):
        isAllPositive = False
        unbounded = False
        while(not isAllPositive):
            for i in range(len(self.objective) - 1):
                isAllPositive = True
                for j in range(len(self.objective) - 1):
                    if self.objective[j] < 0:
                        isAllPositive = False
                if isAllPositive:
                    break
                if i not in self.pivots and self.objective[i] < 0:
                    minimumRatio = 238472634
                    newPivot = None
                    oldPivot = None
                    for j in range(len(self.pivots)):
                        if self.constraints[j][i] != 0:
                            ratio = self.constraintsInfo[j]["rhs"] / self.constraints[j][i]
                            if ratio > 0 and minimumRatio > min(minimumRatio, ratio):
                                minimumRatio = min(minimumRatio, ratio)
                                newPivot = i
                                oldPivot = j
                    if newPivot == None:
                        unbounded = True
                        break
                    if newPivot != None:
                        pivotRatio = self.constraints[oldPivot][newPivot]
                        for j in range(len(self.constraints[oldPivot])):
                            self.constraints[oldPivot][j] /= pivotRatio
                        self.constraintsInfo[oldPivot]["rhs"] /= pivotRatio
                        objectiveRatio = self.objective[newPivot]
                        self.objective[-1] -= (
                            self.constraintsInfo[oldPivot]["rhs"] * objectiveRatio
                        )
                        for j in range(len(self.objective) - 1):
                            self.objective[j] = (
                                self.objective[j]
                                - objectiveRatio * self.constraints[oldPivot][j]
                            )
                        for j in range(len(self.constraints)):
                            if j == oldPivot:
                                continue
                            if self.constraints[j][newPivot] == 0:
                                continue
                            ratio = self.constraints[j][newPivot]
                            self.constraintsInfo[j]["rhs"] -= (
                                ratio * self.constraintsInfo[oldPivot]["rhs"]
                            )
                            for k in range(len(self.constraints[0])):
                                self.constraints[j][k] = (
                                    self.constraints[j][k]
                                    - ratio * self.constraints[oldPivot][k]
                                )
                        self.pivots[oldPivot] = newPivot
            if unbounded:
                break
            if isAllPositive:
                break
        if unbounded:
            print("Unbounded")
            return
        constraintCounter = 0
        printMatrix = []
        for i in range(len(self.objective) -1):
            if i in self.pivots:
                printMatrix.append(self.constraintsInfo[self.pivots.index(i)]["rhs"])
                constraintCounter += 1
            else:
                printMatrix.append(0.0)
        space= 17 + len(self.objective2)*3 + (len(self.objective2) - 1) *2
        for i in self.objective2:
            if i<0:
                space += 1
        
        for i in range(len(self.objective2)):
            if i == 0:
                print("z = ",end="")
                print("{:.3f}".format(self.objective[-1]), end=" = ")
                print(self.objective2, end=" * ")
                print("{:.6f}".format(printMatrix[i]))
            else:
                print(" " * space + "{:.6f}".format(printMatrix[i]))


app = App()
print("Solution for data1")
app.readFromText("Assignment3_Data1.txt")
app.simplexReady()
app.simplex()
print("Solution for data2")
app.readFromText("Assignment3_Data2.txt")
app.simplexReady()
app.simplex()
print("Solution for data3")
app.readFromText("Assignment3_Data3.txt")
app.simplexReady()
app.simplex()
