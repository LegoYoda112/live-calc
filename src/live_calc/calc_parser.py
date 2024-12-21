import time
import re
from math import sqrt, sin, cos
import math
import numpy as np
from pint import UnitRegistry

# Set up units
ureg = UnitRegistry()
# Units to parse
unit_list = ["m", "cm", "mm", "km", "s"]

def parse_line(line, context, output_only = True):
    output_line = ""

    # If output_only, replace input characters with spaces
    if(output_only):
        output_line = ' '*(len(line) + 1)
    else:
        output_line = line + ' '

    # Print line for debug purposes
    # print(">", line)

    # Insert spaces between ( _ )
    line = re.sub("(\()(?=[0-9a-zA-Z])", "( ", line)
    line = re.sub("(\))(?!=[0-9a-zA-Z])", " )", line)

    # Pad control characters
    chars_to_pad = ('\=', '\+', '\*', '\[', '\]', '\,', '\/')
    for char in chars_to_pad:
        line = re.sub(char, " " + char[-1] + " ", line)

    # Pad units
    # for unit in unit_list:
    #     line = re.sub(unit, " " + unit + " ", line)

    # Does something to arrays, figure out what?
    line = re.sub('[ ]+', " ", line)

    # Split line by spaces
    line_split = line.split()
    
    # EMPTY LINE
    if(len(line_split) == 0):
        # Pass
        pass

    # COMMENT
    elif(line_split[0] == "#"):
        # Pass
        pass
    
    # ASSIGNMENT AND EVALUATION
    else:
        new_line_split = []
        assign = None
        
        # If we're assigning:
        # > variable = expression
        # set assign to true and remove the variable name and the "=" from the eval line
        if line_split[1] == "=":
            assign = True
            eval_line_split = line_split[2:]
        else:
            assign = False
            eval_line_split = line_split
        
        # For each element in the split check if it's a variable in our context
        # if so, replace it with context['variable_name'] so it's evaluated correctly

        # if it's a unit, add "* ureg.unit" TODO: make this work on both sides
        # e.g. 10 m / s
        for element in eval_line_split:
            if element in unit_list:
                new_element = "ureg." + element

                new_line_split.append(new_element)
            elif element in context.keys():
                # print(element)
                new_element = "context['" + element + "']"

                new_line_split.append(new_element)
            else:
                new_line_split.append(element)

        # Join line to feed to eval
        new_line = ' '.join(new_line_split)

        # print(new_line)
        
        # Evaluate line value
        # TODO: without some filtering, this is bad!
        eval_value = eval(new_line)
        
        # If we're assigning, assign to a new variable in the context
        if assign:

            # If the value is a list, convert to a np array
            if type(eval_value) == list:
                context[line_split[0]] = np.array(eval_value)
            else:
                context[line_split[0]] = eval_value

            # If it's a number, round for output
            # Note this doesn't round the value stored in context
            if(is_number(eval_value)):
                eval_value = round(eval_value, 3)
            
            # Convert to a string
            eval_value = str(eval_value)

            # Add to the output line
            if(not (line_split[1] == "=" and len(line_split) == 3)):
                output_line += ' '.join(("=", eval_value))
        else:
            
            # If it's a number, round it
            if(is_number(eval_value)):
                eval_value = round(eval_value, 3)
            
            # Convert to string
            eval_value = str(eval_value)
            
            # Add to output
            output_line += "= " + eval_value

    return output_line

def parse(input_text, output_only = False):
    # TODO: Make this a class?

    # Holds current values of all variables
    context = {}

    # Holds output text
    output_text = ""

    error = None
    line_number = 0

    # Iterate over each input line going from top to bottom
    for line in input_text.splitlines():
        try:
            output_text += parse_line(line, context) + "\n"
        except Exception as e:
            error = (line_number, str(e))
            break
        
        line_number += 1
    
    # Return output text, variable context and error
    return output_text, context, error

# Check if a variable is an integer or float
# TODO: Make this work better with units
def is_number(x):
    return type(x) == int or type(x) == float