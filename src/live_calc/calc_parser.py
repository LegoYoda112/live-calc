import time
import re
from math import sqrt, sin, cos
import math
import numpy as np
from pint import UnitRegistry, Quantity, PintError

# Set up units
ureg = UnitRegistry()

# preferred units
preferred_units = [
    ureg.m,
    ureg.kg,
    ureg.s,
    ureg.C,
    ureg.N,
    ureg.W,
    ureg.m * ureg.N
]
ureg.default_preferred_units = preferred_units
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

    line_dependencies = {'assign': None, 'use': []}
    
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

                # Update dependencies
                line_dependencies['use'].append(element)

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
            variable_name = line_split[0]

            # If the value is a list, convert to a np array
            if type(eval_value) == list:
                context[variable_name] = np.array(eval_value)
            else:
                context[variable_name] = eval_value

            line_dependencies['assign'] = variable_name

            # If it's a number, round for output
            # Note this doesn't round the value stored in context
            if(is_number(eval_value)):
                eval_value = round(eval_value, 4)

            if(isinstance(eval_value, Quantity)):
                eval_value = simplify_units(eval_value)
            
            # Convert to a string
            eval_value = str(eval_value)

            # Add to the output line
            if(not (line_split[1] == "=" and len(line_split) == 3)):
                output_line += ' '.join(("=", eval_value))
        else:
            
            # If it's a number, round it
            if(is_number(eval_value)):
                eval_value = round(eval_value, 4)

            # If it's a number with units, round it as well and reduce units
            if(isinstance(eval_value, Quantity)):
                eval_value = simplify_units(eval_value)
            
            # Convert to string
            eval_value = str(eval_value)
            
            # Add to output
            output_line += "= " + eval_value

    return output_line, line_dependencies

def simplify_units(value):

    # Attempt to force conversions
    # TODO: This is bad
    try:
        value = value.to(ureg.N * ureg.m)
    except PintError:
        pass

    
    value = value.to_reduced_units().to_compact()

    return round(value, 4)

# Generates dependencies given the list of line dependencies
# Essentially just fills in line numbers
def generate_line_dependencies(dependency_list):
    number_of_lines = len(dependency_list)

    incoming_line_dependencies = [None] * number_of_lines
    outgoing_line_dependencies = [[]] * number_of_lines

    # I really don't like doing this, there must be a better way
    for i in range(number_of_lines):
        incoming_line_dependencies[i] = []

    # Generate outgoing dependencies
    for line_num in range(number_of_lines):
        outgoing_line_dependency = []

        assign_variable = dependency_list[line_num]["assign"]
        
        # If current line uses a value, assign outgoing dependencies
        if(dependency_list[line_num]["use"] != None):
            
            # Move forward through list to find if variable is used again
            for forward_num in range(number_of_lines - line_num - 1):
                forward_line_num = line_num + forward_num + 1

                # If the variable is found in the lines "use" list, add it to the outgoing dependencies
                if(assign_variable in dependency_list[forward_line_num]["use"]):
                    outgoing_line_dependency.append(forward_line_num)

                # If variable gets set again, break
                if(dependency_list[forward_line_num]["assign"] == assign_variable):
                    break
                        
            # put current line's dependency into main list
            outgoing_line_dependencies[line_num] = outgoing_line_dependency

            # update incoming dependencies 
            # this is somewhat redundant information, but helpful
            for outgoing_dependency_line_number in outgoing_line_dependencies[line_num]:

                incoming_line_dependencies[outgoing_dependency_line_number].append(line_num)

    return incoming_line_dependencies, outgoing_line_dependencies



def parse(input_text, output_only = False):
    # TODO: Make this a class?

    # Holds current values of all variables
    context = {}

    # Holds which variables each line relies on
    dependency_list = []

    # Holds output text
    output_text = ""

    error = None

    # Iterate over each input line going from top to bottom
    for (line_number, line) in enumerate(input_text.splitlines()):
        try:
            output_line, line_dependencies = parse_line(line, context)
            output_text += output_line + "\n"

            dependency_list.append(line_dependencies)
        except Exception as e:
            error = (line_number, str(e))
            break
        
    # Return output text, variable context and error
    return output_text, context, dependency_list, error

# Check if a variable is an integer or float
# TODO: Make this work better with units
def is_number(x):
    return type(x) == int or type(x) == float