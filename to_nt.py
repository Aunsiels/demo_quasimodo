from urllib.parse import quote


to_write = []

prefix_subject = "<http://quasimodo.r2.enst.fr/explorer?subject="
prefix_predicate = "<http://quasimodo.r2.enst.fr/explorer?predicate="
prefix_object = "<http://quasimodo.r2.enst.fr/explorer?object="
suffix = ">"


with open("quasimodo_spo.tsv") as f:
    for line in f:
        line = line.strip().split("\t")
        if (len(line) < 3 or not line[0].strip() or not line[1].strip()
                or not line[2].strip()):
            continue
        temp = [
            prefix_subject + quote(line[0], safe="") + suffix,
            prefix_predicate + quote(line[1], safe="") + suffix,
            prefix_object + quote(line[2], safe="") + suffix]
        to_write.append(" ".join(temp))

with open("quasimodo.nt", "w") as f:
    f.write(" .\n".join(to_write))
    f.write(" .\n")

