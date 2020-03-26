import codetable
import time
from PIL import Image, ImageDraw 

CODE_TABLE = {
    "A": codetable.CODE_A_LIST,
    "B": codetable.CODE_B_LIST,
    "C": codetable.CODE_C_LIST
}

def find_code_tables(t):
    result = []
    if t in CODE_TABLE["A"]:
        result.append({
            "index": CODE_TABLE["A"].index(t),
            "table": "A"
        })
    if t in CODE_TABLE["B"]:
        result.append({
            "index": CODE_TABLE["B"].index(t),
            "table": "B"
        })
    if t in CODE_TABLE["C"]:
        result.append({
            "index": CODE_TABLE["C"].index(t),
            "table": "C"
        })
    return result
        

def multiply_node(node):
    sequence = node["sequence"]
    remaining = node["remaining"]

    result = []

    for l in range(min(3, len(remaining))):
        rl = l + 1
        t = ''.join(remaining[:rl])

        for code_table in find_code_tables(t):
            result.append({
                "sequence": sequence + [ code_table ],
                "remaining": remaining[rl:]
            })

    return result

def get_sequence_length(sequence):
    if len(sequence) == 0:
        return []

    changes = 0
    code_table = sequence[0]["table"]
    for item in sequence:
        if item["table"] != code_table:
            code_table = item["table"]
            changes = changes + 1
    return changes + len(sequence)

def find_shortest_sequence(sequences):
    if len(sequences) == 0:
        return []

    shortest_sequence = sequences[0]
    shortest_sequence_length = get_sequence_length(sequences[0])
    for sequence in sequences[1:]:
        sequence_length = get_sequence_length(sequence)
        if sequence_length < shortest_sequence_length:
            shortest_sequence = sequence
            shortest_sequence_length = sequence_length
    return shortest_sequence

def get_table_switch_code(current_table, next_table):
    next_code_text = "Code " + next_table
    table_codes = CODE_TABLE[current_table]
    return {
        "table": current_table,
        "index": table_codes.index(next_code_text)
    }

def get_table_stop_code(current_table):
    return {
        "table": current_table,
        "index": CODE_TABLE[current_table].index("STOP")
    }
def get_checksum_code(value):
    return {
        "table": "A",
        "index": value
    }

def calculate_checksum(sequence):
    c_sum = sequence[0]["index"]
    for i, item in enumerate(sequence[1:]):
        c_sum = c_sum + item["index"] * (i + 1)
    return c_sum % 103

def convert_full_barcode(sequence):
    if len(sequence) == 0:
        return []

    n_sequence = []
    start_code_text = "START " + sequence[0]["table"]
    n_sequence.append({
        "table": sequence[0]["table"],
        "index": codetable.CODE_A_LIST.index(start_code_text)
    })

    for item in sequence:
        last_new_table = n_sequence[-1]["table"]
        if last_new_table != item["table"]:
            n_sequence.append(get_table_switch_code(last_new_table, item["table"]))
        n_sequence.append(item)
    
    checksum = calculate_checksum(n_sequence)
    n_sequence.append(get_checksum_code(checksum))
    n_sequence.append(get_table_stop_code(n_sequence[-1]["table"]))
    return n_sequence

def create_tree(text):
    t_pending = []
    t_submitted = [{
        "sequence": [],
        "remaining": list(text)
    }]
    t_finished = []

    while len(t_submitted) > 0:
        for n in t_submitted:
            t_pending = t_pending + multiply_node(n)

        t_submitted = t_pending
        t_pending = []
        t_finished = t_finished + [ n for n in t_submitted if len(n["remaining"]) == 0 ]
        t_submitted = [ n for n in t_submitted if len(n["remaining"]) > 0 ]
    return t_finished

def create_barcode_image(binary, ratio, padding):
    inner_size = 24
    img = Image.new("RGB", (padding * 2 + len(binary) * ratio, padding * 2 + ratio * inner_size), color=0xffffff)

    imgd = ImageDraw.Draw(img)  

    for i, c in enumerate(list(binary)):
        if c == "1":
            left = padding + i * ratio
            top = padding
            bottom = padding + inner_size * ratio
            imgd.line([ (left, top), (left, bottom) ], fill = "black", width = ratio)

    img.show() 


def encode_text(text):
    shortest_sequence = find_shortest_sequence([ n["sequence"] for n in create_tree(text) ])
    barcode_sequence = convert_full_barcode(shortest_sequence)

    binary_code = ""
    for item in barcode_sequence:
        binary_code = binary_code + codetable.BINARY_LIST[item["index"]]
    binary_code = binary_code + "11"
    return binary_code


binary = encode_text("9zr4983zr38h8")
create_barcode_image(binary, 5, 30)