import Library
from AST import CalEvent

def main():
    program = input("Hello! This is an example program for testing the backend of ClippyCal. Please enter a sample program: ")
    eval(program)

if __name__ == '__main__':
    main()