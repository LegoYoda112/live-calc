from live_calc import calc_parser


dependency_list = [
    {'assign': 'x', 'use': []},
    {'assign': '', 'use': []},
    {'assign': 'y', 'use': ['x']},
    {'assign': 'x', 'use': ['x', 'y']},
    {'assign': 'x', 'use': ['y']}
]

incoming_line_dependencies, outgoing_line_dependencies = calc_parser.generate_line_dependencies(dependency_list)

print(incoming_line_dependencies)
print(outgoing_line_dependencies)