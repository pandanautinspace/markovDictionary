import json

irrel_words = [
    "esp.",
    "n.",
    "adj.",
    "adv.",
    "etc.",
    "pl.",
    "colloq.",
]

irrel_chars = [
    '—',
    '—',
    '-'
]


def toJSON(filePath):
    data = {}
    dic = open(filePath, "r", encoding="UTF8")
    for line in dic:
        line_stripped = line.strip()
        if len(line_stripped) <= 1 or "prefix." in line_stripped \
                or "suffix." in line_stripped or "Usage" in line_stripped \
                or "abbr." in line_stripped or "symb." in line_stripped \
                or "Propr." in line_stripped or "Esp." in line_stripped \
                or "Of *" in line_stripped:
            continue

        word_part = [word.lower() for word in line_stripped.split(".")[0].split(" ")[:-1] if word != '']
        if len(word_part) != 1:
            continue
        word = word_part[0]
        if "-" in word or "'" in word:
            continue

        word = "".join([letter for letter in word if letter.isalpha()]).lower()

        defs_part = ".".join(line_stripped.split(".")[1:])
        # print(word)
        defs_part = remove_brackets(defs_part, "(", ")")
        # print(word)
        defs_part = remove_brackets(defs_part, "[", "]")
        defs_part = remove_irrel(defs_part)
        defs = defs_part.split(".")
        defs_new = []
        for definition in defs:
            words = definition.split(" ")
            words = [word.strip().strip(",./;'[]\\-=<>?:\"{}|") for word in words]
            words = [word.lower() for word in words if word.isalpha()]
            if len(words) > 0:
                defs_new.append(" ".join(words))
        data[word] = defs_new
    write_dic = open("dic.json", "w")
    json.dump(data, write_dic)


def remove_brackets(process_string: str, open_char: chr, close_char: chr) -> str:
    open_indices = []
    while open_char in process_string:
        open_indices.append(process_string.index(open_char))
        while len(open_indices) != 0:
            curr_open = open_indices[-1]
            try:
                next_close = process_string.index(close_char, curr_open)
            except ValueError:
                process_string = process_string[:curr_open]
                break
            next_open = process_string.find(open_char, curr_open + 1, next_close)
            if next_open != -1:
                open_indices.append(next_open)
            else:
                open_indices.pop()
                if curr_open == 0:
                    process_string = process_string[next_close + 1:]
                else:
                    # print(f'removing from {curr_open} to {next_close}, {process_string[curr_open:next_close - 1]}')
                    part1 = process_string[:curr_open]
                    part2 = process_string[next_close + 1:]
                    process_string = part1 + part2
    return process_string


def remove_irrel(process_string):
    words = process_string.split(" ")
    return " ".join(word for word in words if len(word) > 0 and word.lower() not in irrel_words and word[0] not in irrel_chars)


if __name__ == '__main__':
    toJSON("Oxford English Dictionary.txt")
