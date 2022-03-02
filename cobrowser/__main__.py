from cobrowser import browse

x = {}
x["key1"] = "val1"
x["key2"] = [{"some": "thing"}]
x["key3"] = [x["key2"]]
x["cycle"] = [("point back to x:", x)]

browse(x)
