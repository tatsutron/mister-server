import json, os, subprocess
from bottle import put, request, route, run
from xml.etree.ElementTree import Element, ElementTree, SubElement


@route("/scan/<extensions>/<path:path>")
def scan(extensions, path):
    entries = []
    with os.scandir(path) as it:
        for entry in it:
            if entry.is_dir():
                entries.append(os.path.join(entry.path, ""))
            else:
                name, extension = os.path.splitext(entry.path)
                if extension[1:] in extensions.split("|"):
                    entries.append(entry.path)
    return json.dumps(entries)


@route("/hash/<header_size>/<path:path>")
def hash(header_size, path):
    return subprocess.run(
        ["/media/fat/tatsutron/hash", path, "{}".format(header_size)],
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
    ).stdout


# TODO Remove afte MGL migration
@route("/load/<command>/<path:path>")
def load(command, path):
    return subprocess.run(
        ["/media/fat/tatsutron/mbc", "load_rom", command, path],
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
    ).stdout


@put("/play")
def play():
    root = Element("mistergamedescription")
    rbf = SubElement(root, "rbf")
    rbf.text = request.json["rbf"]
    file = SubElement(root, "file")
    file.set("delay", request.json["delay"])
    file.set("index", request.json["index"])
    file.set("path", request.json["path"])
    file.set("type", request.json["type"])
    with open("temp.mgl", "w") as file:
        ElementTree(root).write(file, encoding='unicode')
    with open("/dev/MiSTer_cmd", "w") as file:
        file.write("load_core /media/fat/tatsutron/temp.mgl")
    os.remove("temp.mgl")


run(host='0.0.0.0', port=8080, debug=True)
