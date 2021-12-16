class Matrix(object):
    def __init__(self, rows, cols):
        self.rows = int(rows)
        self.cols = int(cols)
        self.values = []

    #waarden van user input ophalen en invullen in self.values list
    def askValues(self):
        for r in range(self.rows):
            rowValues = []
            for c in range(self.cols):
                val = input("Enter value " + str(r+1) +":"+ str(c+1)+ ": ")
                rowValues.append(val)
            self.values.append(rowValues)

    #functie nodig om matrixC te kunnen gebruiken
    def setZero(self):
        for r in range(self.rows):
            rowValues = []
            for c in range(self.cols):
                val = 0
                rowValues.append(val)
            self.values.append(rowValues)

    #printfunctie
    def debugValues(self):
        for r in range(self.rows):
            print()
            for c in range(self.cols):
                print('|'+str(self.values[r][c])+"|" , end='')
        print()

    @staticmethod
    def multiply(matrixA, matrixB):
        print("Multiplying...")

        matrixC = Matrix(matrixA.rows, matrixB.cols)
        matrixC.setZero()

        for rA in range(matrixA.rows):
            for cB in range(matrixB.cols):
                for rB in range(matrixB.rows):
                    matrixC.values[rA][cB] += int(matrixA.values[rA][rB]) * int(matrixB.values[rB][cB])
        return matrixC


class UserInput:
    rowsA = input("Enter amount of rows of first matrix:")
    colsA = input("Enter amount of columns of first matrix:")

    rowsB = input("Enter amount of rows of second matrix:")
    colsB = input("Enter amount of columns of second matrix:")
    if(colsA == rowsB):
        matrixA = Matrix(rowsA, colsA)
        matrixA.askValues()
        matrixA.debugValues()
        matrixB = Matrix(rowsB, colsB)
        matrixB.askValues()
        matrixB.debugValues()

        matrixC = Matrix.multiply(matrixA, matrixB)
        matrixC.debugValues()
    else:
        print("RowsA must be equals to ColsB")




