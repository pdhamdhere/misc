import argparse
import sys

def pSet(s):
    powerSet = []
    length = len(s)
    numSets = 1 << length

    for i in range(numSets):
        subSet = []
        for j in range(length):
            if i & (1 << j):
                subSet.append(s[j])
        print(i , subSet)
        powerSet.append(subSet)
    return powerSet

def main():
    sets = pSet(sys.argv[1])
    print("PowerSets for", sys.argv[1], ": ", sets)

if __name__ == "__main__":
    main()