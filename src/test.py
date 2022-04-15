import json
import piexif
import piexif.helper
import house
import pickle
a = house.House()

metaData= {}
for variable in dir(a):
    if callable(getattr(a, variable)) and variable.startswith("__"):
        continue
    metaData[str(variable)] = getattr(a, variable)

metaData = {"test": "test", "amin": "amin"}

exif_dict = {"0th": {}, "Exif": {}, "1st": {},
            "thumbnail": None, "GPS": {}}

filename = "./img.jpg"


exif_dict = piexif.load(filename)
# insert custom data in usercomment field
exif_dict["Exif"][piexif.ExifIFD.UserComment] = piexif.helper.UserComment.dump(
    pickle.dumps(metaData),
    encoding="unicode"
)
# insert mutated data (serialised into JSON) into image
piexif.insert(
    piexif.dump(exif_dict),
    filename
)

exif_dict = piexif.load(filename)
# Extract the serialized data
user_comment = piexif.helper.UserComment.load(exif_dict["Exif"][piexif.ExifIFD.UserComment])
# Deserialize
d = pickle.loads(user_comment)
print("Read in exif data: %s" % d)